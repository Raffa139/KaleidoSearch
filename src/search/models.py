from typing import List
from pydantic import BaseModel, Field
from src.search.agent.state import QueryEvaluation, AnsweredQuestion
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


class UserSearch(BaseModel):
    query: str | None = None
    answers: List[AnsweredQuestion] | None = None

    def has_content(self) -> bool:
        return bool(self.query) or bool(self.answers)

    def format_answers(self) -> str | None:
        if not self.answers:
            return None

        formatted_answers = [
            f"{a.id}: {a.answer.strip().replace(';', ',')}" for a in set(self.answers)
        ]
        return "; ".join(formatted_answers)


class QueryEvaluationOut(QueryEvaluation):
    thread_id: int


class ProductRecommendation(ProductBase):
    description: str
