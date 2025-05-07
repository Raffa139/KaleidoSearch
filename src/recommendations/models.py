from pydantic import BaseModel, Field
from src.products.models import ProductBase


class BinaryScore(BaseModel):
    score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


class Question(BaseModel):
    question: str
    answer: str


class UserQuery(BaseModel):
    query: str
    questions: list[Question] | None = None


class ProductRecommendation(ProductBase):
    description: str
