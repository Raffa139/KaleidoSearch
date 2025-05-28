from pydantic import HttpUrl
from sqlmodel import SQLModel, Field, Relationship
from backend.src.common.http_url_type import HttpUrlType


class ShopBase(SQLModel):
    name: str
    url: HttpUrl = Field(sa_type=HttpUrlType)


class ProductBase(SQLModel):
    price: float
    title: str
    url: HttpUrl = Field(sa_type=HttpUrlType)
    thumbnail_url: HttpUrl | None = Field(default=None, sa_type=HttpUrlType)


class ProductIn(ProductBase):
    shop_id: int


class ProductOut(ProductBase):
    id: int
    shop: ShopBase


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    shop_id: int = Field(foreign_key="shop.id")
    shop: "Shop" = Relationship(back_populates="products")
