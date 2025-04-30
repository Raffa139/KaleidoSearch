import asyncio
from typing import Annotated
from uvicorn import Config, Server
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session, create_engine, select

from src.products.models import Product, ProductOut, ProductIn
from src.shops.models import Shop, ShopOut, ShopIn

sqlite_file = "database.db"
sqlite_url = f"sqlite:///{sqlite_file}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def initialize_db():
    SQLModel.metadata.create_all(engine)


def db_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(db_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    initialize_db()


@app.get("/")
def root():
    return {"Status": "KaleidoSearch is up and running"}


@app.get("/products", response_model=list[ProductOut])
def get_products(session: SessionDep):
    return session.exec(select(Product)).all()


@app.get("/products/{id}", response_model=ProductOut)
def get_product_by_id(id: int, session: SessionDep):
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product


@app.post("/products", response_model=ProductOut, status_code=201)
def create_product(product_in: ProductIn, session: SessionDep):
    product = Product.model_validate(product_in)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.get("/shops", response_model=list[ShopOut])
def get_shops(session: SessionDep):
    return session.exec(select(Shop)).all()


@app.get("/shops/{id}", response_model=ShopOut)
def get_shop_by_id(id: int, session: SessionDep):
    shop = session.get(Shop, id)
    if not shop:
        raise HTTPException(status_code=404, detail="Not found")
    return shop


@app.post("/shops", response_model=ShopOut, status_code=201)
def create_shop(shop_in: ShopIn, session: SessionDep):
    shop = Shop.model_validate(shop_in)
    session.add(shop)
    session.commit()
    session.refresh(shop)
    return shop


async def main():
    config = Config(app, host="0.0.0.0", port=8000, reload=True)
    server = Server(config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
