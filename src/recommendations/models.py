from typing import List
from pydantic import BaseModel, Field
from src.products.models import ProductBase


class RelevanceScore(BaseModel):
    id: int = Field(
        description="Identifier for the related document"
    )
    relevant: bool = Field(
        description="Relevance score: True if relevant, or False if not relevant"
    )


class RelevanceScoreList(BaseModel):
    list: List[RelevanceScore] = Field(description="Relevance scores of documents")


class ProductRecommendation(ProductBase):
    description: str
