from typing import TypedDict, Annotated, List
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from src.environment import gemini_api_key

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


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=gemini_api_key()
)


def gemini(state: State):
    return {
        "messages": [llm.invoke(state["messages"])]
    }


def structured_response(state: State):
    last_message = state["messages"][-1].content
    res = llm.with_structured_output(QueryEvaluation).invoke([HumanMessage(content=last_message)])
    return {"query_evaluation": res}


graph_builder = StateGraph(State)

graph_builder.add_node("llm", gemini)
graph_builder.add_node("respond", structured_response)
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", "respond")
graph_builder.add_edge("respond", END)

graph = graph_builder.compile(checkpointer=InMemorySaver())
config = RunnableConfig(configurable={"thread_id": "1"})

sys_message = SystemMessage(EVAL_QUERY_PROMPT)

if __name__ == '__main__':
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["q"]:
            break

        if user_input == "1":
            config = RunnableConfig(configurable={"thread_id": "1"})
            continue
        elif user_input == "2":
            config = RunnableConfig(configurable={"thread_id": "2"})
            continue

        for event in graph.stream(State(messages=[sys_message, HumanMessage(user_input)]), config):
            for node, update in event.items():
                print("Update from node", node)
                print(update)
                print("\n")
