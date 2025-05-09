from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Header
from src.app.dependencies import SessionDep, LLMDep, QueryAgentDep, VectorStoreDep
from src.recommendations.service import RecommendationService, ProductRecommendation
from src.recommendations.query_agent.state import QueryEvaluation
from src.products.service import ProductService
from src.shops.service import ShopService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def recommendation_service(
        session: SessionDep,
        llm: LLMDep,
        query_agent: QueryAgentDep,
        vector_store: VectorStoreDep
):
    shop_service = ShopService(session)
    product_service = ProductService(session, shop_service)
    return RecommendationService(product_service, llm, query_agent, vector_store)


ServiceDep = Annotated[RecommendationService, Depends(recommendation_service)]


@router.get("/", response_model=list[ProductRecommendation])
def get_recommendations(q: str, service: ServiceDep):
    # TODO: Remove q, provide thread_id, access thread state and use cleaned query if exists
    recommendations = service.get_recommendations(q)
    if not recommendations:
        raise HTTPException(status_code=400)

    return recommendations


@router.get("/query", response_model=QueryEvaluation)
def evaluate_user_query(q: str, thread_id: Annotated[str, Header()], service: ServiceDep):
    return service.evaluate_user_query(q, thread_id)
