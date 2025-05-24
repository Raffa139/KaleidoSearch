from abc import ABC
from typing import List
from pydantic import BaseModel, Field
from backend.src.search.graphs.search_graph_state import QueryEvaluation
from backend.src.products.models import ProductBase


class UserAnswer(BaseModel):
    id: int = Field(
        description="Unique integer identifier, starting from 0 and incrementing sequentially"
    )
    answer: str = Field(
        description="Answer from the user"
    )

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(id)


class BaseUserSearch(ABC, BaseModel):
    query: str

    def get_answers(self) -> List[UserAnswer] | None:
        return None

    def has_content(self) -> bool:
        return bool(self.query)

    def format_answers(self) -> str | None:
        return None


class UserSearch(BaseUserSearch):
    query: str | None = None
    answers: List[UserAnswer] | None = None

    def get_answers(self) -> List[UserAnswer] | None:
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
    ai_title: str
    description: str


class ThreadOut(BaseModel):
    thread_id: int
