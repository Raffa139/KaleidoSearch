import time
import logging
import tiktoken
from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from backend.src.environment import max_tokens_minute
from backend.src.products.models import ProductBase, ProductIn
from backend.src.products.service import ProductService
from backend.src.shops.models import ShopIn
from backend.src.shops.service import ShopService
from backend.src.data_import.stopwatch import Stopwatch

log = logging.getLogger(__name__)

SECONDS_IN_MINUTE = 60


class ProductImport(ProductBase):
    description: str
    shop: str


class BatchedProduct(BaseModel):
    product: ProductImport
    document: Document


class ImportResult(BaseModel):
    failed_batches: list[tuple[list[BatchedProduct], Exception]] = []

    def add_failed(self, batched_products: list[BatchedProduct], exception: Exception):
        self.failed_batches.append((batched_products, exception))

    class Config:
        arbitrary_types_allowed = True


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

    def import_products(self, products: list[ProductImport], *, source: str) -> ImportResult:
        watch = Stopwatch(units="s")
        result = ImportResult()
        batches = self._create_batches(products, source=source)
        total_tokens = self._count_total_tokens(
            [bp.document.page_content for batch in batches for bp in batch]
        )

        log.info(
            "Total tokens: %s, Total batches: %s, Estimated time %ss",
            total_tokens,
            len(batches),
            len(batches) * SECONDS_IN_MINUTE
        )

        for i, batch in enumerate(batches):
            try:
                log.info("Processing %s. batch (len: %s)", i + 1, len(batch))
                self._import_product_batch(batch)
            except Exception as e:
                log.error("Exception caught: %s", str(e))
                result.add_failed(batch, e)

            duration = watch.lap()
            timeout = max(0, SECONDS_IN_MINUTE - duration)
            unprocessed_batches = len(batches) - (i + 1)
            remaining = unprocessed_batches * SECONDS_IN_MINUTE + timeout
            log.info("Batch processed, took %ss", duration)

            if unprocessed_batches:
                log.info("Next batch in %ss, estimated %ss remaining", timeout, remaining)
                watch.isolate(time.sleep, timeout)

        log.info("All batches processed, took %ss", watch.stop())
        return result

    def _import_product_batch(self, batch: list[BatchedProduct]):
        create_shops_batch = self._shop_service.create_batch()
        create_products_batch = self._product_service.create_batch()

        for batched_product in batch:
            product = batched_product.product
            shop = self._shop_service.find_by_name(product.shop)

            if not shop and product.shop not in create_shops_batch:
                create_shops_batch.add(ShopIn(
                    name=product.shop,
                    url="https://example.com"
                ))

        shops = create_shops_batch.commit()

        for batched_product in batch:
            product = batched_product.product
            shop = self._shop_service.find_by_name(product.shop)

            if not shop:
                log.warning("Shop '%s' not found, skipping", product.shop)
                continue

            create_products_batch.add(ProductIn(
                **product.model_dump(),
                shop_id=shop.id
            ))

        products = create_products_batch.commit()

        for product in products:
            batched_product = next((bp for bp in batch if bp.product.title == product.title), None)

            if not batched_product:
                log.warning("Product '%s' not found, skipping", product.title)
                continue

            batched_product.document.metadata["ref_id"] = product.id

        try:
            documents = [bp.document for bp in batch]
            self._vector_store.add_documents(documents)
        except Exception as e:
            log.error("Failed to store embeddings. Performing rollback... Details: %s", str(e))
            self._product_service.delete(products)
            self._shop_service.delete(shops)
            raise

    def _create_batches(
            self,
            products: list[ProductImport],
            *,
            source: str,
            batch_token_limit: int = max_tokens_minute()
    ) -> list[list[BatchedProduct]]:
        batches: list[list[BatchedProduct]] = []

        current_batch: list[BatchedProduct] = []
        tokens_in_batch = 0
        i = 0

        while i < len(products):
            product = products[i]
            content = f"{product.title} - {product.price}$ - {product.description}"
            tokens = self._count_tokens(content)

            if tokens > batch_token_limit:
                raise Exception("Document contains more tokens than allowed in batch")

            if tokens_in_batch + tokens > batch_token_limit:
                batches.append(current_batch)
                tokens_in_batch = 0
                current_batch = []
            else:
                document = Document(page_content=content, metadata={"source": source})
                current_batch.append(BatchedProduct(product=product, document=document))
                tokens_in_batch += tokens
                i += 1

        if current_batch:
            batches.append(current_batch)

        return batches

    def _count_total_tokens(self, texts: list[str]) -> int:
        return sum([self._count_tokens(text) for text in texts])

    def _count_tokens(self, text: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
