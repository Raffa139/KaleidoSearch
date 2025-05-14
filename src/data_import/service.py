from langchain_core.language_models import BaseChatModel
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from src.products.models import ProductBase, ProductIn
from src.products.service import ProductService
from src.shops.models import ShopIn
from src.shops.service import ShopService
from src.data_import.stopwatch import global_stopwatch as watch

SUMMARIZE_PROMPT = (
    """
Condense the following product description to a maximum of 512 words. The goal is to create a 
representation that can be effectively used in a vector store to retrieve semantically similar 
products. Therefore, the summary must preserve the original meaning and key attributes of the 
product.

Here is the original description:

{description}
    """
)


# TODO: Test summary prompt further
# TODO: Put price into summary


class ProductImport(ProductBase):
    description: str
    shop: str


class ImportService:
    MAX_DESCRIPTION_LENGTH = 512

    def __init__(
            self,
            product_service: ProductService,
            shop_service: ShopService,
            llm: BaseChatModel,
            vector_store: VectorStore
    ):
        self._product_service = product_service
        self._shop_service = shop_service
        self._llm = llm
        self._vector_store = vector_store

    def add_products(
            self,
            products: list[ProductImport],
            *,
            source: str,
            summarize=False
    ) -> list[ProductImport]:
        documents = []
        too_big_products = []

        print("Write products to DB")

        for product in products:
            description = f"{product.title} - {product.price}$ - {product.description}"
            words_in_description = len(description.split())

            if words_in_description > ImportService.MAX_DESCRIPTION_LENGTH and not summarize:
                too_big_products.append(product)
                continue

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

            content = self._summarize_description(description) \
                if words_in_description > ImportService.MAX_DESCRIPTION_LENGTH else description

            documents.append(Document(page_content=content, metadata=metadata))

        print(f"Products successfully written to DB, took {watch}")

        print("Write products to Vector Store")
        self._vector_store.add_documents(documents)
        print(f"Products successfully written to Vector Store, took {watch}")

        return too_big_products

    def _summarize_description(self, description: str) -> str:
        prompt = SUMMARIZE_PROMPT.format(description=description)
        return self._llm.invoke(prompt).content.lower()
