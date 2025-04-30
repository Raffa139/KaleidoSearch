from sqlmodel import SQLModel, Field, Relationship


class ProductBase(SQLModel):
    price: float
    title: str
    url: str
    thumbnail_url: str | None = None
    shop_id: int


class ProductIn(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    chroma_doc_id: str | None = Field(default=None, unique=True)
    shop_id: int = Field(foreign_key="shop.id")
    shop: "Shop" = Relationship(back_populates="products")
