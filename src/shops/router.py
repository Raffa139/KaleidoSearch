from fastapi import APIRouter, HTTPException
from sqlmodel import select
from src.shops.models import Shop, ShopOut, ShopIn
from src.app.session import SessionDep

router = APIRouter(prefix="/shops", tags=["shops"])


@router.get("/", response_model=list[ShopOut])
def get_shops(session: SessionDep):
    return session.exec(select(Shop)).all()


@router.post("/", response_model=ShopOut, status_code=201)
def create_shop(shop_in: ShopIn, session: SessionDep):
    shop = Shop.model_validate(shop_in)
    session.add(shop)
    session.commit()
    session.refresh(shop)
    return shop


@router.get("/{id}", response_model=ShopOut)
def get_shop_by_id(id: int, session: SessionDep):
    shop = session.get(Shop, id)
    if not shop:
        raise HTTPException(status_code=404, detail="Not found")
    return shop
