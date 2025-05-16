from typing import Annotated, List
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AnsweredQuestion(BaseModel):
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


class FollowUpQuestion(BaseModel):
    id: int = Field(
        description="Unique integer identifier, starting from 0 and incrementing sequentially"
    )
    short: str = Field(
        description="Brief summary of a question, only 1-3 words long, capitalized and without '?'"
    )
    long: str = Field(
        description="Short and concise one sentence description of a question"
    )


class QueryEvaluation(BaseModel):
    valid: bool = Field(
        description="Query score: True if valid, or False if not valid"
    )
    answered_questions: List[AnsweredQuestion] = Field(
        description="Questions that have already been answered by the user"
    )
    follow_up_questions: List[FollowUpQuestion] = Field(
        description=(
            "Follow Up Questions to guide the user, improve the query, and add information to it"
        )
    )
    cleaned_query: str | None = Field(
        default=None,
        description=(
            "Cleaned-up version of the query combined with all answered questions, "
            "retaining semantic meaning, used for distance-based similarity search"
        )
    )


class MessageState(BaseModel):
    messages: Annotated[List[AnyMessage], add_messages] = []


class SearchAgentState(MessageState):
    query_evaluation: QueryEvaluation | None = None
