from sqlmodel import Session, select, delete
from sqlmodel.sql.expression import Select, SelectOfScalar
from backend.src.products.models import Product, ProductIn
from backend.src.products.graphs.summarize_graph import SummarizeGraph
from backend.src.products.graphs.summarize_graph_state import ProductSummary
from backend.src.shops.service import ShopService


class ProductService:
    def __init__(
            self,
            session: Session,
            shop_service: ShopService,
            summarize_graph: SummarizeGraph
    ):
        self._session = session
        self._shop_service = shop_service
        self._summarize_graph = summarize_graph

    def find_all(self) -> list[Product]:
        return self._query(select(Product)).all()

    def find_by_id(self, id: int) -> Product | None:
        return self._session.get(Product, id)

    def find_by_ids(self, ids: list[int]) -> list[Product]:
        return self._query(select(Product).where(Product.id.in_(ids))).all()

    def create(self, product_in: ProductIn) -> Product:
        product = self._validate_new_product(product_in)
        self._session.add(product)
        self._session.commit()
        self._session.refresh(product)
        return product

    def create_batch(self, products_in: list[ProductIn] = ()) -> "ProductService.BatchedCreate":
        return ProductService.BatchedCreate(self, products_in)

    def delete(self, products: list[Product]):
        ids = [product.id for product in products]
        self._query(delete(Product).where(Product.id.in_(ids)))
        self._session.commit()

    def summarize(self, ids: list[int], summary_length: int = 100) -> list[ProductSummary]:
        return self._summarize_graph.invoke(
            product_ids=ids,
            summary_length=summary_length
        ).summarized_products

    def _validate_new_product(self, product_in: ProductIn) -> Product:
        shop = self._shop_service.find_by_id(product_in.shop_id)
        if not shop:
            raise ValueError(f"Invalid shop id {product_in.shop_id}")

        return Product.model_validate(product_in)

    def _query(self, query: Select | SelectOfScalar):
        return self._session.exec(query)

    class BatchedCreate:
        def __init__(self, product_service: "ProductService", products_in: list[ProductIn] = ()):
            self._product_service = product_service
            self._products_in = list(products_in)

        def add(self, product_in: ProductIn) -> "ProductService.BatchedCreate":
            self._products_in.append(product_in)
            return self

        def commit(self) -> list[Product]:
            products = [self._product_service._validate_new_product(product_in) for product_in in
                        self._products_in]
            self._product_service._session.bulk_save_objects(products)
            self._product_service._session.commit()
            self._products_in = []

            return self._product_service._query(
                select(Product).order_by(Product.id.desc()).limit(len(products))).all()

        def __contains__(self, item):
            if isinstance(item, ProductIn):
                return item.title in [product_in.title for product_in in self._products_in]
            elif isinstance(item, str):
                return item in [product_in.title for product_in in self._products_in]
            else:
                raise ValueError(f"Type {type(item)} not supported")
