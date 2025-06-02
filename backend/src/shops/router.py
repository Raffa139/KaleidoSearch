from fastapi import APIRouter, HTTPException
from backend.src.app.dependencies import ShopServiceDep
from backend.src.shops.models import ShopOut, ShopIn

router = APIRouter(prefix="/shops", tags=["shops"])


@router.get("/", response_model=list[ShopOut])
def get_shops(service: ShopServiceDep):
    return service.find_all()


@router.post("/", response_model=ShopOut, status_code=201)
def create_shop(shop_in: ShopIn, service: ShopServiceDep):
    return service.create(shop_in)


@router.get("/{id}", response_model=ShopOut)
def get_shop_by_id(id: int, service: ShopServiceDep):
    shop = service.find_by_id(id)
    if not shop:
        raise HTTPException(status_code=404)
    return shop
