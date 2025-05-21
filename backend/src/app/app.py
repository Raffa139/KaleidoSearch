from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from backend.src.app.dependencies import db_engine
from backend.src.products.router import router as products_router
from backend.src.shops.router import router as shops_router
from backend.src.users.router import router as users_router


def initialize_db():
    SQLModel.metadata.create_all(db_engine)


def handle_value_error(_, error: Exception):
    return JSONResponse(status_code=400, content={"detail": f"Bad request: {error}"})


def create_app():
    app = FastAPI()

    app.include_router(products_router)
    app.include_router(shops_router)
    app.include_router(users_router)

    app.add_exception_handler(ValueError, handle_value_error)

    app.add_event_handler("startup", initialize_db)

    return app
