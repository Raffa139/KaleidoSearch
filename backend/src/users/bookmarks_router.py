from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from backend.src.app.dependencies import SessionDep, SummarizeGraphDep
from backend.src.authentication.router import CurrentUserDep
from backend.src.users.models import BookmarkOut, BookmarkIn
from backend.src.products.service import ProductService
from backend.src.shops.service import ShopService
from backend.src.users.service import UserService

router = APIRouter(
    prefix="/me/bookmarks",
    tags=["users"],
    responses={
        498: {"description": "Token expired"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    }
)


def create_product_service(session: SessionDep, summarize_graph: SummarizeGraphDep):
    shop_service = ShopService(session)
    return ProductService(session, shop_service, summarize_graph)


ProductServiceDep = Annotated[ProductService, Depends(create_product_service)]


def create_user_service(session: SessionDep, product_service: ProductServiceDep):
    return UserService(session, product_service)


UserServiceDep = Annotated[UserService, Depends(create_user_service)]


@router.get("/", response_model=list[BookmarkOut])
def get_user_bookmarks(user: CurrentUserDep, user_service: UserServiceDep):
    return user_service.find_user_bookmarks(user.id)


@router.post("/", response_model=BookmarkOut)
def create_bookmark(user: CurrentUserDep, bookmark: BookmarkIn, user_service: UserServiceDep):
    return user_service.create_bookmark(user.id, bookmark.product_id)


@router.get("/{product_id}", response_model=BookmarkOut)
def get_user_bookmark_by_product_id(
        product_id: int,
        user: CurrentUserDep,
        user_service: UserServiceDep
):
    if bookmark := user_service.find_bookmark_by_user_product_id(user.id, product_id):
        return bookmark

    raise HTTPException(status_code=404)


@router.delete("/{bookmark_id}")
def delete_bookmark(bookmark_id: int, user: CurrentUserDep, user_service: UserServiceDep):
    if not user_service.has_user_access_to_bookmark(user.id, bookmark_id):
        raise HTTPException(status_code=403)

    user_service.delete_bookmark(bookmark_id)
