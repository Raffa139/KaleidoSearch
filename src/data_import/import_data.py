import os
import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.definitions import DATA_DIR
from src.environment import product_catalogues
from src.data_import.extract import extract_amazon_data
from src.data_import.service import ImportService
from src.products.service import ProductService
from src.shops.service import ShopService
from src.app.session import db_session


def get_data_files() -> list[str]:
    return [os.path.join(DATA_DIR, catalog) for catalog in product_catalogues()]


def main():
    # TODO: Use chroma from global dependencies?
    # TODO: Use batch processing to import large amounts more efficiently
    # TODO: Stop and log import time deltas

    with next(db_session()) as session:
        shop_service = ShopService(session)
        product_service = ProductService(session, shop_service)

        chroma = Chroma(
            client=chromadb.HttpClient(host="localhost", port=5000),
            collection_name="kaleido_search_products",
            embedding_function=HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2")
            # By default, input text longer than 384 word pieces is truncated.
        )

        import_service = ImportService(product_service, shop_service, chroma)

        data_files = get_data_files()

        print(f"Starting import of {len(data_files)} data file(s)...")

        for data_file in data_files:
            source = os.path.basename(data_file)

            print()
            print(f"Importing {source}")

            documents = chroma.get(where={"source": source}, include=["metadatas"])
            if len(documents["ids"]) > 0:
                print(f"Skipping already imported {source}")
                continue

            try:
                extracted_products = extract_amazon_data(data_file)
                print(f"Extracted {len(extracted_products)} from {source}")
                import_service.add_products(extracted_products, source=source)
                print(f"Imported {source} successfully")
            except Exception as e:
                print(f"Import of {source} failed, details: {e}")


if __name__ == '__main__':
    main()
