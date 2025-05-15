from sqlmodel import Session, select, delete
from sqlmodel.sql.expression import Select, SelectOfScalar
from src.shops.models import Shop, ShopIn


class ShopService:
    def __init__(self, session: Session):
        self._session = session

    def find_all(self) -> list[Shop]:
        return self._query(select(Shop)).all()

    def find_by_id(self, id: int) -> Shop | None:
        return self._session.get(Shop, id)

    def find_by_name(self, name: str) -> Shop | None:
        return self._query(select(Shop).where(Shop.name == name)).first()

    def create(self, shop_in: ShopIn) -> Shop:
        shop = Shop.model_validate(shop_in)
        self._session.add(shop)
        self._session.commit()
        self._session.refresh(shop)
        return shop

    def create_batch(self, shops_in: list[ShopIn] = ()) -> "ShopService.BatchedCreate":
        return ShopService.BatchedCreate(self, shops_in)

    def delete(self, shops: list[Shop]):
        ids = [shop.id for shop in shops]
        self._query(delete(Shop).where(Shop.id.in_(ids)))
        self._session.commit()

    def _query(self, query: Select | SelectOfScalar):
        return self._session.exec(query)

    class BatchedCreate:
        def __init__(self, shop_service: "ShopService", shops_in: list[ShopIn] = ()):
            self._shop_service = shop_service
            self._shops_in = list(shops_in)

        def add(self, shop_in: ShopIn) -> "ShopService.BatchedCreate":
            self._shops_in.append(shop_in)
            return self

        def commit(self) -> list[Shop]:
            shops = [Shop.model_validate(shop_in) for shop_in in self._shops_in]
            self._shop_service._session.bulk_save_objects(shops)
            self._shop_service._session.commit()
            self._shops_in = []

            return self._shop_service._query(
                select(Shop).order_by(Shop.id.desc()).limit(len(shops))).all()

        def __contains__(self, item):
            if isinstance(item, ShopIn):
                return item.name in [shop_in.name for shop_in in self._shops_in]
            elif isinstance(item, str):
                return item in [shop_in.name for shop_in in self._shops_in]
            else:
                raise ValueError(f"Type {type(item)} not supported")
