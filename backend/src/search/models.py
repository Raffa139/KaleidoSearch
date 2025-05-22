from abc import ABC
from typing import List
from pydantic import BaseModel
from backend.src.search.graphs.search_graph_state import QueryEvaluation, AnsweredQuestion
from backend.src.products.models import ProductBase


class BaseUserSearch(ABC, BaseModel):
    query: str

    def get_answers(self) -> List[AnsweredQuestion] | None:
        return None

    def has_content(self) -> bool:
        return bool(self.query)

    def format_answers(self) -> str | None:
        return None


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


class CreateThreadOut(BaseModel):
    thread_id: int
