from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from backend.src.app.dependencies import SessionDep, SearchGraphDep, RetrieveGraphDep
from backend.src.search.service import SearchService, ProductRecommendation
from backend.src.search.models import QueryEvaluationOut, UserSearch, BaseUserSearch, \
    ThreadOut
from backend.src.products.service import ProductService
from backend.src.shops.service import ShopService
from backend.src.users.service import UserService
from backend.src.users.models import UserOut, UserIn

router = APIRouter(prefix="/users", tags=["users"])


def create_user_service(session: SessionDep):
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(create_user_service)]


def create_search_service(
        session: SessionDep,
        search_graph: SearchGraphDep,
        retrieve_graph: RetrieveGraphDep,
        user_service: UserServiceDep
):
    shop_service = ShopService(session)
    product_service = ProductService(session, shop_service)
    return SearchService(product_service, user_service, search_graph, retrieve_graph)


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


@router.get("/{uid}/threads", response_model=list[ThreadOut])
def get_user_threads(uid: int, user_service: UserServiceDep):
    if not user_service.find_user_by_id(uid):
        raise HTTPException(status_code=401)

    threads = user_service.find_user_threads(uid)
    return map(lambda thread: ThreadOut(thread_id=thread.id), threads)


@router.post("/{uid}/threads", response_model=ThreadOut, status_code=201)
def create_thread(uid: int, user_service: UserServiceDep):
    if not user_service.find_user_by_id(uid):
        raise HTTPException(status_code=401)

    thread = user_service.create_thread(uid)
    return ThreadOut(thread_id=thread.id)


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
        user_service: UserServiceDep,
        rerank: bool = False
):
    if not user_service.find_user_by_id(uid):
        raise HTTPException(status_code=401)

    if not user_service.has_user_access_to_thread(uid, tid):
        raise HTTPException(status_code=403)

    return search_service.get_recommendations(tid, rerank=rerank)


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
