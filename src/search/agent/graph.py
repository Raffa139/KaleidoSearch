from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver
from src.search.agent.state import SearchAgentState, QueryEvaluation


def chat_model(llm: BaseChatModel, state: SearchAgentState):
    def invoke(s: SearchAgentState):
        return {
            "messages": [llm.invoke(s["messages"])]
        }

    return invoke(state)


def structured_response(llm: BaseChatModel, state: SearchAgentState):
    # TODO: Maybe can be called as tool to remove extra llm call
    #       Custom tool condition that wires to END after tool called
    #       Custom tool node that saves evaluation in state

    def invoke(s: SearchAgentState):
        last_message = s["messages"][-1].content
        response = llm.with_structured_output(QueryEvaluation).invoke(
            [HumanMessage(content=last_message)]
        )
        return {"query_evaluation": response}

    return invoke(state)


def build_agent(llm: BaseChatModel, memory: BaseCheckpointSaver) -> CompiledStateGraph:
    graph_builder = StateGraph(SearchAgentState)

    graph_builder.add_node("llm", lambda state: chat_model(llm, state))
    graph_builder.add_node("respond", lambda state: structured_response(llm, state))
    graph_builder.add_edge(START, "llm")
    graph_builder.add_edge("llm", "respond")
    graph_builder.add_edge("respond", END)

    return graph_builder.compile(checkpointer=memory)
