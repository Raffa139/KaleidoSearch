from typing import TypedDict, Annotated, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

EVAL_QUERY_PROMPT = (
    "You are a evaluator assessing relevance of a user query.\n"
    "Evaluate if the users query contains valid products, categories, or specific user needs "
    "related to e-commerce products.\n"
    "Guide the user with questions to improve the query and to add information to it.\n"
    "Once you gathered enough information consider the query to be valid and score it with True, "
    "score False otherwise.\n"
    "Also provide a cleaned-up version of the users query with the same semantic meaning and "
    "incorporating all answered questions, used for distance-based similarity search.\n"
    "There is always room for improvement, provide further guidance with questions, even if the "
    "query scored a True."
)


class QueryQuestion(BaseModel):
    short: str = Field(
        description="Brief summary of a question, only 1-3 words long"
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


class State(TypedDict):
    messages: Annotated[list, add_messages]
    query_evaluation: QueryEvaluation


class ConversationService:
    def __init__(self, agent):
        self._agent = agent

    def invoke(self, user_query: str, thread_id: str) -> QueryEvaluation:
        config = RunnableConfig(configurable={"thread_id": thread_id})
        past_messages = self._agent.get_state(config).values.get("messages")
        initial_messages = [SystemMessage(EVAL_QUERY_PROMPT)] if not past_messages else []

        return self._agent.invoke(
            input=State(messages=[*initial_messages, HumanMessage(user_query)]),
            config=config
        ).get("query_evaluation")


if __name__ == '__main__':
    # service = ConversationService(llm)
    thread = "1"

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["q"]:
            break

        if user_input == "1":
            thread = "1"
            continue
        elif user_input == "2":
            thread = "2"
            continue

        # res = service.invoke(user_input, thread)
        # print("EVAL", res.get("query_evaluation"))
