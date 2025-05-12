import os
import concurrent.futures
import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.definitions import DATA_DIR
from src.environment import product_catalogues
from src.data_import.extract import extract_amazon_data
from src.data_import.service import ImportService
from src.data_import.stopwatch import Stopwatch, global_stopwatch_config, global_stopwatch as watch
from src.products.service import ProductService
from src.shops.service import ShopService
from src.app.session import db_session

global_stopwatch_config(units="s")

# chroma_client = chromadb.HttpClient(host="localhost", port=5000)
mpnet_base_v2_embeddings = watch.isolate(HuggingFaceEmbeddings,
                                         model_name="sentence-transformers/all-mpnet-base-v2")
miniLM_L6_v2_embeddings = watch.isolate(HuggingFaceEmbeddings,
                                        model_name="sentence-transformers/all-MiniLM-L6-v2")


# chroma = Chroma(
#    client=chroma_client,
#    collection_name="kaleido_search_products",
#    embedding_function=mpnet_base_v2_embeddings
#    # By default, input text longer than 384 word pieces is truncated.
# )


def get_data_files() -> list[str]:
    return [os.path.join(DATA_DIR, catalog) for catalog in product_catalogues()]


def work(args: tuple[list[str], str]):
    process_watch = Stopwatch(units="s")
    batch, embedding_model = args

    print(f"Starting work with {embedding_model}, batch len: {len(batch)}")
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    documents = embeddings.embed_documents(batch)
    print(f"Work done, took {process_watch}")

    return documents


def with_threads(texts: list[str], embedding_model: str, batch_size: int):
    batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]

    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as pool:
        results = []
        for result in pool.map(work, [(batch, embedding_model) for batch in batches]):
            results.extend(result)

    return results


def main():
    # TODO: Use chroma from global dependencies?
    # TODO: Embedding function is the bottle neck - take ~98% of time
    #       Measure time for different models
    # TODO: Use batch processing to import large amounts more efficiently

    with next(db_session()) as session:
        shop_service = ShopService(session)
        product_service = ProductService(session, shop_service)

        # import_service = ImportService(product_service, shop_service, chroma)

        data_files = get_data_files()

        print(f"Starting import of {len(data_files)} data file(s)...")

        for data_file in data_files:
            source = os.path.basename(data_file)

            print()
            print(f"Importing {source}")

            # documents = chroma.get(where={"source": source}, include=["metadatas"])
            # if len(documents["ids"]) > 0:
            #    print(f"Skipping already imported {source}")
            #    continue

            try:
                extracted_products = extract_amazon_data(data_file)[:1000]
                print(f"Extracted {len(extracted_products)} from {source}, took {watch}")

                # import_service.add_products(extracted_products[:100], source=source)

                texts = [f"{p.title} - {p.description}" for p in extracted_products]
                # [print(p.description) for p in extracted_products]

                embedded_texts = mpnet_base_v2_embeddings.embed_documents(texts)
                print(f"all-mpnet-base-v2 (no threads) took: {watch}")

                embedded_texts = with_threads(
                    texts,
                    "sentence-transformers/all-mpnet-base-v2",
                    batch_size=250
                )
                print(f"all-mpnet-base-v2 (threaded) took: {watch}")

                # miniLM_L6_v2_embeddings.embed_documents(texts)
                # print(f"all-MiniLM-L6-v2 took: {watch}")

                print(f"Imported {source} successfully")
            except Exception as e:
                print(f"Import of {source} failed after {watch}, details: {e}")

    print(f"Import took {watch.stop()}s\n\n")
    watch.print_segments()


if __name__ == '__main__':
    main()
