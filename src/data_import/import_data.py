import os
from src.definitions import DATA_DIR
from src.environment import product_catalogues
from src.data_import.extract import extract_amazon_data
from src.data_import.service import ImportService
from src.data_import.stopwatch import global_stopwatch_config, global_stopwatch as watch
from src.products.service import ProductService
from src.shops.service import ShopService
from src.app.dependencies import db_session, chroma

global_stopwatch_config(units="s")


def get_data_files() -> list[str]:
    return [os.path.join(DATA_DIR, catalog) for catalog in product_catalogues()]


def main():
    with next(db_session()) as session:
        shop_service = ShopService(session)
        product_service = ProductService(session, shop_service)
        import_service = ImportService(product_service, shop_service, chroma)

        data_files = get_data_files()

        print(f"Starting import of {len(data_files)} data file(s)...")

        for data_file in data_files:
            source = os.path.basename(data_file)
            print(f"\nImporting {source}")

            documents = chroma.get(where={"source": source}, include=["metadatas"])
            if len(documents["ids"]) > 0:
                print(f"Skipping already imported {source}")
                continue

            try:
                extracted_products = extract_amazon_data(data_file)
                print(f"Extracted {len(extracted_products)} from {source}, took {watch}")
                import_service.add_products(extracted_products, source=source)
                print(f"Imported {source} successfully")
            except Exception as e:
                print(f"Import of {source} failed after {watch}, details: {e}")

    print(f"Import took {watch.stop()}s\n\n")
    watch.print_segments()


if __name__ == '__main__':
    main()
