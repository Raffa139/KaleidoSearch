from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from backend.src.app.dependencies import SessionDep, SummarizeGraphDep
from backend.src.authentication.router import CurrentUserDep
from backend.src.products.service import ProductService
from backend.src.shops.service import ShopService
from backend.src.users.service import UserService
from backend.src.users.models import UserOut, UserIn
from backend.src.users.threads_router import router as threads_router
from backend.src.users.bookmarks_router import router as bookmarks_router

router = APIRouter(prefix="/users", tags=["users"])


def create_product_service(session: SessionDep, summarize_graph: SummarizeGraphDep):
    shop_service = ShopService(session)
    return ProductService(session, shop_service, summarize_graph)


ProductServiceDep = Annotated[ProductService, Depends(create_product_service)]


def create_user_service(session: SessionDep, product_service: ProductServiceDep):
    return UserService(session, product_service)


UserServiceDep = Annotated[UserService, Depends(create_user_service)]


@router.get("/", response_model=list[UserOut])
def get_users(user_service: UserServiceDep):
    return user_service.find_all_users()


@router.post("/", response_model=UserOut, status_code=201)
def create_user(user_in: UserIn, user_service: UserServiceDep):
    return user_service.create_user(user_in)


@router.get("/me", response_model=UserOut)
def get_user(user: CurrentUserDep, user_service: UserServiceDep):
    if user := user_service.find_user_by_id(user.id):
        return user

    raise HTTPException(status_code=404)


router.include_router(threads_router)
router.include_router(bookmarks_router)
