import os
import sys
import logging
from backend.src.definitions import DATA_DIR
from backend.src.environment import product_catalogues
from backend.src.data_import.extract import extract_amazon_data
from backend.src.data_import.service import ImportService
from backend.src.data_import.stopwatch import Stopwatch
from backend.src.products.service import ProductService
from backend.src.shops.service import ShopService
from backend.src.app.dependencies import create_db_session, chroma, create_summarize_graph

logging.basicConfig(format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


def get_data_files() -> list[str]:
    return [os.path.join(DATA_DIR, catalog) for catalog in product_catalogues()]


def always_accept() -> bool:
    return len(sys.argv) == 2 and sys.argv[1] == "--y"


def main():
    watch = Stopwatch(units="s")

    with next(create_db_session()) as session:
        shop_service = ShopService(session)
        product_service = ProductService(session, shop_service, create_summarize_graph())
        import_service = ImportService(product_service, shop_service, chroma)

        data_files = get_data_files()

        log.info("Starting import of %s data file(s)...", len(data_files))

        for data_file in data_files:
            source = os.path.basename(data_file)
            log.info("Importing %s", source)

            documents = chroma.get(where={"source": source}, include=["metadatas"])
            if len(documents["ids"]) > 0:
                log.info("Skipping already imported %s", source)
                continue

            try:
                extracted_products = extract_amazon_data(data_file)
                log.info(
                    "Extracted %s from %s, took %s",
                    len(extracted_products),
                    source,
                    str(watch)
                )

                if not always_accept():
                    answer = watch.isolate(
                        input,
                        f"Continue importing {len(extracted_products)} products? (Y/N): "
                    )
                    if not answer.lower() == "y":
                        continue

                result = import_service.import_products(extracted_products, source=source)
                for failed_batch, exception in result.failed_batches:
                    log.warning(
                        "Failed to import batch (len: %s). Details %s",
                        len(failed_batch),
                        str(exception)
                    )
                watch.lap()
            except Exception as e:
                log.error("Import of %s failed after %s, details: %s", source, str(watch), str(e))

    log.info("Import took %ss", watch.stop())


if __name__ == '__main__':
    main()
