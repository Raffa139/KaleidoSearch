from sqlmodel import Field, Relationship
from backend.src.products.models import Product, ProductOut, ShopBase


class ShopIn(ShopBase):
    pass


class ShopOut(ShopBase):
    id: int
    products: list[ProductOut]


class Shop(ShopBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    products: list[Product] = Relationship(back_populates="shop")
