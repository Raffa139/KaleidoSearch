from fastapi import APIRouter, HTTPException, Depends
from backend.src.app.dependencies import UserServiceDep, SearchServiceDep
from backend.src.authentication.router import CurrentUserDep
from backend.src.search.service import ProductRecommendation
from backend.src.search.models import QueryEvaluationOut, UserSearch, BaseUserSearch, NewUserSearch
from backend.src.users.models import ThreadOut

router = APIRouter(
    prefix="/me/threads",
    tags=["users"],
    responses={
        498: {"description": "Token expired"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    }
)


def user_has_thread_access(tid: int, user: CurrentUserDep, user_service: UserServiceDep):
    if not user_service.has_user_access_to_thread(user.id, tid):
        raise HTTPException(status_code=403)


UserHasThreadAccess = Depends(user_has_thread_access)


@router.get("/", response_model=list[ThreadOut])
def get_user_threads(user: CurrentUserDep, user_service: UserServiceDep):
    threads = user_service.find_user_threads(user.id)
    return map(lambda thread: ThreadOut(**thread.model_dump(), thread_id=thread.id), threads)


@router.post("/", response_model=QueryEvaluationOut)
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

    return handle_thread_posts(user.id, None, user_search, search_service)


@router.get("/{tid}", dependencies=[UserHasThreadAccess], response_model=QueryEvaluationOut)
def get_user_thread(tid: int, search_service: SearchServiceDep):
    return search_service.get_query_evaluation(tid)


@router.post("/{tid}", dependencies=[UserHasThreadAccess], response_model=QueryEvaluationOut)
def post_to_thread(
        tid: int,
        user: CurrentUserDep,
        user_search: UserSearch,
        search_service: SearchServiceDep
):
    return handle_thread_posts(user.id, tid, user_search, search_service)


@router.delete("/{tid}", dependencies=[UserHasThreadAccess])
def delete_thread(tid: int, user_service: UserServiceDep):
    user_service.delete_thread(tid)


@router.get(
    "/{tid}/recommendations",
    dependencies=[UserHasThreadAccess],
    response_model=list[ProductRecommendation]
)
def get_recommendations_from_thread(
        tid: int,
        search_service: SearchServiceDep,
        rerank: bool = False
):
    return search_service.get_recommendations(tid, rerank=rerank)


def handle_thread_posts(
        uid: int,
        tid: int | None,
        user_search: BaseUserSearch,
        search_service: SearchServiceDep
) -> QueryEvaluationOut:
    return search_service.evaluate_user_query(user_search, uid, tid)
