from sqlmodel import select
from sqlmodel.sql.expression import Select, SelectOfScalar
from src.app.session import SessionDep
from src.shops.models import Shop, ShopIn


class ShopService:
    def __init__(self, session: SessionDep):
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


def shop_service(session: SessionDep):
    return ShopService(session)
