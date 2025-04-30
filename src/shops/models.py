from pydantic import HttpUrl
from sqlmodel import SQLModel, Field, Relationship
from src.products.models import Product, ProductOut
from src.common.http_url_type import HttpUrlType


class ShopBase(SQLModel):
    name: str
    url: HttpUrl = Field(sa_type=HttpUrlType)


class ShopIn(ShopBase):
    pass


class ShopOut(ShopBase):
    id: int
    products: list[ProductOut]


class Shop(ShopBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    products: list[Product] = Relationship(back_populates="shop")
