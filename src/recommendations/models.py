from typing import List
from pydantic import BaseModel, Field
from src.products.models import ProductBase


class BinaryScore(BaseModel):
    id: int | None = Field(
        default=None,
        description="Optional identifier for the related document"
    )
    score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


class BinaryScoreList(BaseModel):
    list: List[BinaryScore] = Field(description="Relevance scores of documents")


class ProductRecommendation(ProductBase):
    description: str
