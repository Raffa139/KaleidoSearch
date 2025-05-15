import time
import tiktoken
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


class BatchedProduct:
    def __init__(self, product: ProductImport, document: Document):
        self.product = product
        self.document = document


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
        batched_products: list[BatchedProduct] = []

        print("Write products to DB")

        for product in products:
            content = f"{product.title} - {product.price}$ - {product.description}"
            batched_products.append(
                BatchedProduct(product, Document(page_content=content, metadata={"source": source})))

        print(f"Products successfully written to DB, took {watch}")

        batches = self._create_batches(batched_products)
        total_tokens = self._count_total_tokens([bp.document for bp in batched_products])

        print(f"Total tokens: {total_tokens}")
        print(f"Total batches: {len(batches)}")
        print(f"Write products to Vector Store, estimated time {len(batches) * 60}s")

        for i, batch in enumerate(batches):
            print(f"Starting {i + 1}. batch ({len(batch)}) ... ", end="")
            self._add_product_batch(batch)

            duration = watch.lap()
            timeout = max(0, 60 - duration)
            n_unprocessed_batches = len(batches) - (i + 1)
            remaining = n_unprocessed_batches * 60 + timeout
            print(
                f"Batch processed, took {duration}s, next batch in {timeout}s, estimated time "
                f"remaining {remaining}s")
            watch.isolate(time.sleep, timeout)

        print(f"Products successfully written to Vector Store, took {watch}")

    def _add_product_batch(self, batch: list[BatchedProduct]):
        shop_batch = self._shop_service.create_batch()
        product_batch = self._product_service.create_batch()

        for batched_product in batch:
            product = batched_product.product
            shop = self._shop_service.find_by_name(product.shop)

            if not shop and product.shop not in shop_batch:
                shop_batch.add(ShopIn(
                    name=product.shop,
                    url="https://example.com"
                ))

        shops = shop_batch.commit()

        for batched_product in batch:
            product = batched_product.product
            shop = self._shop_service.find_by_name(product.shop)

            if not shop:
                print("NO SHOP", product)

            product_batch.add(ProductIn(
                **product.model_dump(),
                shop_id=shop.id
            ))

        products = product_batch.commit()
        for product in products:
            batched_product = next((bp for bp in batch if bp.product.title == product.title), None)
            if not batched_product:
                print("NO PRODUCT", product)
            batched_product.document.metadata["ref_id"] = product.id

        documents = [bp.document for bp in batch]
        print([doc.metadata for doc in documents][:3])
        try:
            self._vector_store.add_documents(documents=documents)
        except Exception:
            self._product_service.delete(products)
            self._shop_service.delete(shops)

    def _create_batches(
            self,
            batched_products: list[BatchedProduct],
            *,
            batch_token_limit: int = 100000
    ) -> list[list[BatchedProduct]]:
        batches: list[list[BatchedProduct]] = []

        current_batch: list[BatchedProduct] = []
        tokens_in_batch = 0
        i = 0

        while i < len(batched_products):
            batched_product = batched_products[i]
            tokens = self._count_tokens_in_document(batched_product.document)

            if tokens > batch_token_limit:
                raise Exception("Document contains more tokens than allowed in batch")

            if tokens_in_batch + tokens > batch_token_limit:
                batches.append(current_batch)
                tokens_in_batch = 0
                current_batch = []
            else:
                current_batch.append(batched_product)
                tokens_in_batch += tokens
                i += 1

        if current_batch:
            batches.append(current_batch)

        return batches

    def _count_total_tokens(self, documents: list[Document]) -> int:
        return sum([self._count_tokens_in_document(document) for document in documents])

    def _count_tokens_in_document(self, document: Document) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(document.page_content))
