from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from backend.src.app.dependencies import ProductServiceDep
from backend.src.products.models import ProductOut, ProductIn
from backend.src.products.graphs.summarize_graph_state import ProductSummary

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductOut])
def get_products(
        service: ProductServiceDep,
        ids: Annotated[str | None, Query(pattern="[\d]+,?")] = None
):
    if ids:
        product_ids = [int(id) for id in ids.split(",") if id]
        products = service.find_by_ids(product_ids)
        return sorted(products, key=lambda p: product_ids.index(p.id))

    return service.find_all()


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(product_in: ProductIn, service: ProductServiceDep):
    return service.create(product_in)


@router.post("/summarize", response_model=list[ProductSummary])
def summarize_products(ids: list[int], service: ProductServiceDep, length: int = 100):
    if len(ids) == 0:
        raise HTTPException(status_code=400)

    if len(ids) == len(service.find_by_ids(ids)):
        return service.summarize(ids, length)

    raise HTTPException(status_code=404)


@router.get("/{id}", response_model=ProductOut)
def get_product_by_id(id: int, service: ProductServiceDep):
    product = service.find_by_id(id)
    if not product:
        raise HTTPException(status_code=404)
    return product
