import json
import chromadb
from sqlmodel import SQLModel
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from src.products.models import ProductIn
from src.products.service import ProductService
from src.shops.models import ShopIn
from src.shops.service import ShopService
from src.app.session import db_session, engine

def flatten_dict(dictionary: dict) -> dict:
    result = {}

    for key, value in dictionary.items():
        if isinstance(value, dict):
            flattened = flatten_dict(value)
            result = {**result, **flattened}
        elif isinstance(value, list):
            joined = ", ".join(value)
            result[key] = joined
        else:
            result[key] = value

    return result


def load_amazon_data(data_file: str, product_service: ProductService, shop_service: ShopService, chroma: Chroma) -> list[Document]:
    with open(data_file, encoding="utf-8") as file:
        products = [json.loads(line.strip()) for line in file]

    docs = []
    for product in products[:100]:
        category, title, avg_rating, n_ratings, features, description, price, images, videos, store, categories, details, parent_asin, bought_together = product.values()

        required = [title, parent_asin, price, description + features]
        if not all(required):
            continue

        main_images = [image for image in images if image.get("variant") == "MAIN"]
        thumbnail = main_images[0].get('large') if main_images else None

        shop = shop_service.find_by_name(store)
        if not shop:
            shop = shop_service.create(ShopIn(name=store, url="https://example.com"))

        saved_product = product_service.create(ProductIn(
            title=title,
            price=price,
            url=f"https://www.amazon.com/dp/{parent_asin}",
            thumbnail_url=thumbnail,
            shop_id=shop.id
        ))

        metadata = {
            "ref_id": saved_product.id,
            "source": data_file
        }

        description = f" - {''.join(description)}" if description else ""
        features = f" - {''.join(features)}" if features else ""
        content = title + description + features
        docs.append(Document(page_content=content, metadata=metadata))

    chroma.add_documents(docs)

    return docs


def main():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with next(db_session()) as session:
        shop_service = ShopService(session)
        product_service = ProductService(session, shop_service)

        chroma_client = chromadb.HttpClient(host="localhost", port=5000)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

        print(chroma_client.heartbeat())

        chroma = Chroma(
            client=chroma_client,
            collection_name="kaleido_search_products",
            embedding_function=embeddings
        )

        shop_service.create(ShopIn(name="Test Shop", url="https://example.com"))

        data_file = "meta_Health_and_Personal_Care.jsonl"
        docs = load_amazon_data(data_file, product_service, shop_service, chroma)
        chroma_docs = chroma.get(where={"source": data_file}, include=["metadatas"])

        print("DOCS")
        print(len(docs))
        for doc in docs[:3]:
           print(doc.metadata)

        print()
        print("CHROMA DOCS")
        for metadata in chroma_docs["metadatas"][:3]:
            print(metadata)

        results = chroma.as_retriever().invoke("white socks short")
        print()
        print("RESULTS")
        for doc in results[:3]:
            print(doc)


if __name__ == '__main__':
    main()
