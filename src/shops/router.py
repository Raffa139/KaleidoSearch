from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from src.app.dependencies import SessionDep
from src.shops.models import ShopOut, ShopIn
from src.shops.service import ShopService

router = APIRouter(prefix="/shops", tags=["shops"])


def shop_service(session: SessionDep):
    return ShopService(session)


ServiceDep = Annotated[ShopService, Depends(shop_service)]


@router.get("/", response_model=list[ShopOut])
def get_shops(service: ServiceDep):
    return service.find_all()


@router.post("/", response_model=ShopOut, status_code=201)
def create_shop(shop_in: ShopIn, service: ServiceDep):
    return service.create(shop_in)


@router.get("/{id}", response_model=ShopOut)
def get_shop_by_id(id: int, service: ServiceDep):
    shop = service.find_by_id(id)
    if not shop:
        raise HTTPException(status_code=404)
    return shop
