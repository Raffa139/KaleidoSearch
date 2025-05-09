from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Header
from src.app.dependencies import SessionDep, LLMDep, SearchAgentDep, VectorStoreDep
from src.search.service import SearchService, ProductRecommendation
from src.search.models import QueryEvaluationOut
from src.products.service import ProductService
from src.shops.service import ShopService
from src.users.service import UserService

router = APIRouter(prefix="/search", tags=["searching"])


def user_service_dep(session: SessionDep):
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(user_service_dep)]


def search_service(
        session: SessionDep,
        llm: LLMDep,
        search_agent: SearchAgentDep,
        vector_store: VectorStoreDep,
        user_service: UserServiceDep
):
    shop_service = ShopService(session)
    product_service = ProductService(session, shop_service)
    return SearchService(product_service, user_service, llm, search_agent, vector_store)


ServiceDep = Annotated[SearchService, Depends(search_service)]


@router.get("/", response_model=QueryEvaluationOut)
def evaluate_user_query(
        q: str,
        service: ServiceDep,
        user_service: UserServiceDep,
        user_id: Annotated[int, Header()],
        thread_id: Annotated[int, Header()] = None
):
    if not user_service.find_user_by_id(user_id):
        raise HTTPException(status_code=401)

    if thread_id and not user_service.has_user_access_to_thread(user_id, thread_id):
        raise HTTPException(status_code=403)

    return service.evaluate_user_query(q, user_id, thread_id)


@router.get("/recommendations", response_model=list[ProductRecommendation])
def get_recommendations(
        user_id: Annotated[int, Header()],
        thread_id: Annotated[int, Header()],
        service: ServiceDep,
        user_service: UserServiceDep
):
    if not user_service.find_user_by_id(user_id):
        raise HTTPException(status_code=401)

    if not user_service.has_user_access_to_thread(user_id, thread_id):
        raise HTTPException(status_code=403)

    recommendations = service.get_recommendations(thread_id)
    if recommendations is None:
        raise HTTPException(status_code=400, detail="User query needs refinement")

    return recommendations
