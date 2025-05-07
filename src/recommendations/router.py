from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from src.app.dependencies import SessionDep, LLMDep, VectorStoreDep
from src.recommendations.service import RecommendationService, ProductRecommendation, UserQuery
from src.products.service import ProductService
from src.shops.service import ShopService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def recommendation_service(session: SessionDep, llm: LLMDep, vector_store: VectorStoreDep):
    shop_service = ShopService(session)
    product_service = ProductService(session, shop_service)
    return RecommendationService(product_service, llm, vector_store)


ServiceDep = Annotated[RecommendationService, Depends(recommendation_service)]


@router.post("/", response_model=list[ProductRecommendation])
def get_recommendations(query: UserQuery, service: ServiceDep):
    recommendations = service.get_recommendations(query)
    if not recommendations:
        raise HTTPException(status_code=400)

    return recommendations
