from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from backend.src.app.dependencies import SessionDep, SummarizeGraphDep
from backend.src.products.models import ProductOut, ProductIn
from backend.src.products.service import ProductService
from backend.src.products.graphs.summarize_graph_state import ProductSummary
from backend.src.shops.service import ShopService

router = APIRouter(prefix="/products", tags=["products"])


def product_service(session: SessionDep, summarize_graph: SummarizeGraphDep):
    shop_service = ShopService(session)
    return ProductService(session, shop_service, summarize_graph)


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


@router.get("/{id}/summary", response_model=list[ProductSummary])
def summarize_product(id: int, service: ServiceDep, summary_length: int = 100):
    if service.find_by_id(id):
        return service.summarize([id], summary_length)

    raise HTTPException(status_code=404)
