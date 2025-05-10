from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from src.products.models import ProductBase, ProductIn
from src.products.service import ProductService
from src.shops.models import ShopIn
from src.shops.service import ShopService
from src.data_import.stopwatch import global_stopwatch as watch


class ProductImport(ProductBase):
    description: str
    shop: str


class ImportService:
    def __init__(
            self,
            product_service: ProductService,
            shop_service: ShopService,
            vector_store: VectorStore
    ):
        self._product_service = product_service
        self._shop_service = shop_service
        self._vector_store = vector_store

    def add_products(self, products: list[ProductImport], source: str):
        documents = []

        print("Write products to DB")

        for product in products:
            shop = self._shop_service.find_by_name(product.shop)

            if not shop:
                shop = self._shop_service.create(ShopIn(
                    name=product.shop,
                    url="https://example.com"
                ))

            saved_product = self._product_service.create(ProductIn(
                **product.model_dump(),
                shop_id=shop.id
            ))

            metadata = {
                "ref_id": saved_product.id,
                "source": source
            }

            content = f"{product.title} - {product.description}"
            documents.append(Document(page_content=content, metadata=metadata))

        print(f"Products successfully written to DB, took {watch}")

        print("Write products to Vector Store")
        documents = self._vector_store.add_documents(documents)
        print(f"Products successfully written to Vector Store, took {watch}")

        return documents
