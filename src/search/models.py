from abc import ABC
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


class BaseUserSearch(ABC, BaseModel):
    query: str

    def get_answers(self) -> List[AnsweredQuestion] | None:
        return None

    def has_content(self) -> bool:
        return bool(self.query)

    def format_answers(self) -> str | None:
        return None


class NewUserSearch(BaseUserSearch):
    pass


class UserSearch(BaseUserSearch):
    query: str | None = None
    answers: List[AnsweredQuestion] | None = None

    def get_answers(self) -> List[AnsweredQuestion] | None:
        return self.answers

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
