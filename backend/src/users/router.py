from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from backend.src.app.dependencies import SessionDep, SearchGraphDep, RetrieveGraphDep, \
    SummarizeGraphDep
from backend.src.authentication.router import CurrentUserDep
from backend.src.search.service import SearchService, ProductRecommendation
from backend.src.search.models import QueryEvaluationOut, UserSearch, BaseUserSearch, NewUserSearch
from backend.src.products.service import ProductService
from backend.src.shops.service import ShopService
from backend.src.users.service import UserService
from backend.src.users.models import UserOut, UserIn, ThreadOut, BookmarkOut, BookmarkIn

# TODO: Split into separate router for threads & bookmarks

router = APIRouter(prefix="/users", tags=["users"])


def create_product_service(session: SessionDep, summarize_graph: SummarizeGraphDep):
    shop_service = ShopService(session)
    return ProductService(session, shop_service, summarize_graph)


ProductServiceDep = Annotated[ProductService, Depends(create_product_service)]


def create_user_service(session: SessionDep, product_service: ProductServiceDep):
    return UserService(session, product_service)


UserServiceDep = Annotated[UserService, Depends(create_user_service)]


def create_search_service(
        search_graph: SearchGraphDep,
        retrieve_graph: RetrieveGraphDep,
        product_service: ProductServiceDep,
        user_service: UserServiceDep
):
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


@router.get("/{uid}/bookmarks", response_model=list[BookmarkOut])
def get_user_bookmarks(uid: int, user_service: UserServiceDep):
    if not user_service.find_user_by_id(uid):
        raise HTTPException(status_code=401)

    return user_service.find_user_bookmarks(uid)


@router.post("/{uid}/bookmarks", response_model=BookmarkOut)
def create_bookmark(uid: int, bookmark: BookmarkIn, user_service: UserServiceDep):
    if not user_service.find_user_by_id(uid):
        raise HTTPException(status_code=401)

    return user_service.create_bookmark(uid, bookmark.product_id)


@router.get("/{uid}/bookmarks/{product_id}", response_model=BookmarkOut)
def get_user_bookmark_by_product_id(uid: int, product_id: int, user_service: UserServiceDep):
    if not user_service.find_user_by_id(uid):
        raise HTTPException(status_code=401)

    if bookmark := user_service.find_bookmark_by_user_product_id(uid, product_id):
        return bookmark

    raise HTTPException(status_code=404)


@router.delete("/{uid}/bookmarks/{bookmark_id}")
def delete_bookmark(uid: int, bookmark_id: int, user_service: UserServiceDep):
    if not user_service.find_user_by_id(uid):
        raise HTTPException(status_code=401)

    if not user_service.has_user_access_to_bookmark(uid, bookmark_id):
        raise HTTPException(status_code=403)

    user_service.delete_bookmark(bookmark_id)


@router.get("/me/threads", response_model=list[ThreadOut])
def get_user_threads(user: CurrentUserDep, user_service: UserServiceDep):
    threads = user_service.find_user_threads(user.id)
    return map(lambda thread: ThreadOut(**thread.model_dump(), thread_id=thread.id), threads)


@router.post("/me/threads", response_model=QueryEvaluationOut)
def create_thread(
        user: CurrentUserDep,
        search_service: SearchServiceDep,
        user_service: UserServiceDep,
        user_search: NewUserSearch | None = None
):
    if not user_search:
        thread = user_service.create_thread(user.id)

        return QueryEvaluationOut(
            thread_id=thread.id,
            valid=False,
            answered_questions=[],
            follow_up_questions=[]
        )

    return handle_thread_posts(user.id, None, user_search, search_service, user_service)


@router.get("/me/threads/{tid}", response_model=QueryEvaluationOut)
def get_user_thread(
        tid: int,
        user: CurrentUserDep,
        search_service: SearchServiceDep,
        user_service: UserServiceDep
):
    if tid and not user_service.has_user_access_to_thread(user.id, tid):
        raise HTTPException(status_code=403)

    return search_service.get_query_evaluation(tid)


@router.post("/me/threads/{tid}", response_model=QueryEvaluationOut)
def post_to_thread(
        tid: int,
        user: CurrentUserDep,
        user_search: UserSearch,
        search_service: SearchServiceDep,
        user_service: UserServiceDep
):
    return handle_thread_posts(user.id, tid, user_search, search_service, user_service)


@router.delete("/me/threads/{tid}")
def delete_thread(tid: int, user: CurrentUserDep, user_service: UserServiceDep):
    if tid and not user_service.has_user_access_to_thread(user.id, tid):
        raise HTTPException(status_code=403)

    user_service.delete_thread(tid)


@router.get("/me/threads/{tid}/recommendations", response_model=list[ProductRecommendation])
def get_recommendations_from_thread(
        tid: int,
        user: CurrentUserDep,
        search_service: SearchServiceDep,
        user_service: UserServiceDep,
        rerank: bool = False
):
    if not user_service.has_user_access_to_thread(user.id, tid):
        raise HTTPException(status_code=403)

    return search_service.get_recommendations(tid, rerank=rerank)


def handle_thread_posts(
        uid: int,
        tid: int | None,
        user_search: BaseUserSearch,
        search_service: SearchServiceDep,
        user_service: UserServiceDep
) -> QueryEvaluationOut:
    if tid and not user_service.has_user_access_to_thread(uid, tid):
        raise HTTPException(status_code=403)

    return search_service.evaluate_user_query(user_search, uid, tid)
