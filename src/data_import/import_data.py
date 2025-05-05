import chromadb
from sqlmodel import SQLModel
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.data_import.extract import extract_amazon_data
from src.data_import.service import ImportService
from src.products.service import ProductService
from src.shops.service import ShopService
from src.app.session import db_session, engine

DATA_FILE = "meta_Health_and_Personal_Care.jsonl"


def main():
    # TODO: Support multiple data files via .env
    # TODO: Check if docs with data file as source already existing (only import file if not)

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with next(db_session()) as session:
        shop_service = ShopService(session)
        product_service = ProductService(session, shop_service)

        chroma = Chroma(
            client=chromadb.HttpClient(host="localhost", port=5000),
            collection_name="kaleido_search_products",
            embedding_function=HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2")
        )

        import_service = ImportService(product_service, shop_service, chroma)

        extracted_products = extract_amazon_data(DATA_FILE)
        import_service.add_products(extracted_products[:100], DATA_FILE)

        results = chroma.as_retriever().invoke("birthday party favors kit")
        print()
        print("RESULTS")
        for doc in results:
            print(doc)


if __name__ == '__main__':
    main()
