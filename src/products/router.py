from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from src.app.dependencies import SessionDep
from src.products.models import ProductOut, ProductIn
from src.products.service import ProductService
from src.shops.service import ShopService

router = APIRouter(prefix="/products", tags=["products"])


def product_service(session: SessionDep):
    shop_service = ShopService(session)
    return ProductService(session, shop_service)


ServiceDep = Annotated[ProductService, Depends(product_service)]


@router.get("/", response_model=list[ProductOut])
def get_products(service: ServiceDep):
    return service.find_all()


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(product_in: ProductIn, service: ServiceDep):
    return service.create(product_in)


@router.get("/{id}", response_model=ProductOut)
def get_product_by_id(id: int, service: ServiceDep):
    product = service.find_by_id(id)
    if not product:
        raise HTTPException(status_code=404)
    return product
