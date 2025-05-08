from typing import TypedDict, Annotated, List
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class QueryQuestion(BaseModel):
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
    questions: List[QueryQuestion] = Field(
        description="Questions to guide the user, improve the query, and add information to it"
    )
    cleaned_query: str | None = Field(
        default=None,
        description=(
            "Cleaned-up version of the query combined with all answered questions, "
            "retaining semantic meaning, used for distance-based similarity search"
        )
    )


class QueryAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    query_evaluation: QueryEvaluation
