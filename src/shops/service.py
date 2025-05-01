from sqlmodel import Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar
from src.shops.models import Shop, ShopIn


class ShopService:
    def __init__(self, session: Session):
        self._session = session

    def find_all(self) -> list[Shop]:
        return self._query(select(Shop)).all()

    def find_by_id(self, id: int) -> Shop | None:
        return self._session.get(Shop, id)

    def create(self, shop_in: ShopIn) -> Shop:
        shop = Shop.model_validate(shop_in)
        self._session.add(shop)
        self._session.commit()
        self._session.refresh(shop)
        return shop

    def _query(self, query: Select | SelectOfScalar):
        return self._session.exec(query)
