from fastapi import APIRouter, HTTPException
from sqlmodel import select
from src.products.models import Product, ProductOut, ProductIn
from src.app.session import SessionDep

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductOut])
def get_products(session: SessionDep):
    return session.exec(select(Product)).all()


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(product_in: ProductIn, session: SessionDep):
    product = Product.model_validate(product_in)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.get("/{id}", response_model=ProductOut)
def get_product_by_id(id: int, session: SessionDep):
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product
