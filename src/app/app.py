from fastapi import FastAPI
from sqlmodel import SQLModel

from .session import engine
from src.products.router import router as products_router
from src.shops.router import router as shops_router


def initialize_db():
    SQLModel.metadata.create_all(engine)


def create_app():
    app = FastAPI()

    app.include_router(products_router)
    app.include_router(shops_router)

    app.add_event_handler("startup", initialize_db)

    return app
