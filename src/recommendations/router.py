from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Header
from src.app.dependencies import SessionDep, LLMDep, QueryAgentDep, VectorStoreDep
from src.recommendations.service import RecommendationService, ProductRecommendation
from src.recommendations.query_agent.state import QueryEvaluation
from src.products.service import ProductService
from src.shops.service import ShopService
from src.users.service import UserService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def user_service_dep(session: SessionDep):
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(user_service_dep)]


def recommendation_service(
        session: SessionDep,
        llm: LLMDep,
        query_agent: QueryAgentDep,
        vector_store: VectorStoreDep,
        user_service: UserServiceDep
):
    shop_service = ShopService(session)
    product_service = ProductService(session, shop_service)
    return RecommendationService(product_service, user_service, llm, query_agent, vector_store)


ServiceDep = Annotated[RecommendationService, Depends(recommendation_service)]


@router.get("/", response_model=list[ProductRecommendation])
def get_recommendations(q: str, service: ServiceDep):
    # TODO: Remove q, provide thread_id, access thread state and use cleaned query if exists
    recommendations = service.get_recommendations(q)
    if not recommendations:
        raise HTTPException(status_code=400)

    return recommendations


@router.get("/query", response_model=QueryEvaluation)
def evaluate_user_query(
        q: str,
        service: ServiceDep,
        user_service: UserServiceDep,
        user_id: Annotated[int, Header()],
        thread_id: Annotated[int, Header()] = None
):
    if thread_id and not user_service.has_user_access_to_thread(user_id, thread_id):
        raise HTTPException(status_code=403)

    return service.evaluate_user_query(q, user_id, thread_id)
