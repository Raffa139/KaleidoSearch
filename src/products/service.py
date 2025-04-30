from sqlmodel import select
from sqlmodel.sql.expression import Select, SelectOfScalar
from src.app.session import SessionDep
from src.products.models import Product, ProductIn


class ProductService:
    def __init__(self, session: SessionDep):
        self._session = session

    def find_all(self) -> list[Product]:
        return self._query(select(Product)).all()

    def find_by_id(self, id: int) -> Product | None:
        return self._session.get(Product, id)

    def create(self, product_in: ProductIn) -> Product:
        product = Product.model_validate(product_in)
        self._session.add(product)
        self._session.commit()
        self._session.refresh(product)
        return product

    def _query(self, query: Select | SelectOfScalar):
        return self._session.exec(query)


def product_service(session: SessionDep):
    return ProductService(session)
