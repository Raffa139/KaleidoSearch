from sqlmodel import Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar
from src.products.models import Product, ProductIn
from src.shops.service import ShopService


class ProductService:
    def __init__(self, session: Session, shop_service: ShopService):
        self._session = session
        self._shop_service = shop_service

    def find_all(self) -> list[Product]:
        return self._query(select(Product)).all()

    def find_by_id(self, id: int) -> Product | None:
        return self._session.get(Product, id)

    def create(self, product_in: ProductIn) -> Product:
        shop = self._shop_service.find_by_id(product_in.shop_id)
        if not shop:
            raise ValueError(f"Invalid shop id {product_in.shop_id}")

        product = Product.model_validate(product_in)
        self._session.add(product)
        self._session.commit()
        self._session.refresh(product)
        return product

    def _query(self, query: Select | SelectOfScalar):
        return self._session.exec(query)
