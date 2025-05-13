from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from src.app.dependencies import SessionDep, LLMDep, SearchAgentDep, VectorStoreDep
from src.search.service import SearchService, ProductRecommendation
from src.search.models import QueryEvaluationOut, NewUserSearch, UserSearch, BaseUserSearch
from src.products.service import ProductService
from src.shops.service import ShopService
from src.users.service import UserService
from src.users.models import UserOut, UserIn

router = APIRouter(prefix="/users", tags=["users"])


def create_user_service(session: SessionDep):
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(create_user_service)]


def create_search_service(
        session: SessionDep,
        llm: LLMDep,
        search_agent: SearchAgentDep,
        vector_store: VectorStoreDep,
        user_service: UserServiceDep
):
    shop_service = ShopService(session)
    product_service = ProductService(session, shop_service)
    return SearchService(product_service, user_service, llm, search_agent, vector_store)


SearchServiceDep = Annotated[SearchService, Depends(create_search_service)]


@router.get("/", response_model=list[UserOut])
def get_users(user_service: UserServiceDep):
    return user_service.find_all_users()


@router.post("/", response_model=UserOut, status_code=201)
def create_user(user_in: UserIn, user_service: UserServiceDep):
    return user_service.create_user(user_in)


@router.get("/{uid}", response_model=UserOut)
def get_user_by_id(uid: int, user_service: UserServiceDep):
    user = user_service.find_user_by_id(uid)
    if not user:
        raise HTTPException(status_code=404)
    return user


@router.post("/{uid}/threads", response_model=QueryEvaluationOut)
def start_new_tread(
        uid: int,
        user_search: NewUserSearch,
        search_service: SearchServiceDep,
        user_service: UserServiceDep
):
    return handle_thread_posts(uid, None, user_search, search_service, user_service)


@router.post("/{uid}/threads/{tid}", response_model=QueryEvaluationOut)
def post_to_thread(
        uid: int,
        tid: int,
        user_search: UserSearch,
        search_service: SearchServiceDep,
        user_service: UserServiceDep
):
    return handle_thread_posts(uid, tid, user_search, search_service, user_service)


@router.get("/{uid}/threads/{tid}/recommendations", response_model=list[ProductRecommendation])
def get_recommendations_from_thread(
        uid: int,
        tid: int,
        search_service: SearchServiceDep,
        user_service: UserServiceDep
):
    if not user_service.find_user_by_id(uid):
        raise HTTPException(status_code=401)

    if not user_service.has_user_access_to_thread(uid, tid):
        raise HTTPException(status_code=403)

    return search_service.get_recommendations(tid)


def handle_thread_posts(
        uid: int,
        tid: int | None,
        user_search: BaseUserSearch,
        search_service: SearchServiceDep,
        user_service: UserServiceDep
) -> QueryEvaluationOut:
    if not user_service.find_user_by_id(uid):
        raise HTTPException(status_code=401)

    if tid and not user_service.has_user_access_to_thread(uid, tid):
        raise HTTPException(status_code=403)

    return search_service.evaluate_user_query(user_search, uid, tid)
