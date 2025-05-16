from typing import Annotated, List, Generic, TypeVar, Callable
from pydantic import BaseModel, ValidationError
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver


class MessageState(BaseModel):
    messages: Annotated[List[AnyMessage], add_messages] = []


T = TypeVar("T", bound=MessageState)


class GraphWrapper(Generic[T]):
    def __init__(self, grap: CompiledStateGraph, prompt: str, state_schema: type[T]):
        self._graph = grap
        self._prompt = prompt
        self._state_schema = state_schema

    def invoke(self, input: T, config: RunnableConfig, **kwargs) -> T:
        past_messages = self.get_dict_state(config).get("messages")
        system_messages = [SystemMessage(self._prompt)] if not past_messages else []
        graph_input = {**input.model_dump(), "messages": [*system_messages, *input.messages]}
        result = self._graph.invoke(graph_input, config, **kwargs)
        return self._state_schema(**result)

    def get_state(self, config: RunnableConfig) -> T | None:
        try:
            state_values = self.get_dict_state(config)
            return self._state_schema(**state_values)
        except ValidationError:
            return None

    def get_dict_state(self, config: RunnableConfig):
        return self._graph.get_state(config).values

    @classmethod
    def from_builder(
            cls,
            state_schema: type[T],
            prompt: str,
            builder: Callable[..., CompiledStateGraph],
            *builder_args,
            **builder_kwargs
    ) -> "GraphWrapper":
        return GraphWrapper[T](
            builder(*builder_args, **builder_kwargs),
            prompt,
            state_schema
        )


class CustomAgentState(MessageState):
    my_str: str
    my_int: int


def build_test_agent(memory: BaseCheckpointSaver) -> CompiledStateGraph:
    graph_builder = StateGraph(CustomAgentState)

    def add_message(state: CustomAgentState):
        return {"messages": [AIMessage("Hello there!")]}

    graph_builder.add_node("llm", add_message)
    graph_builder.add_edge(START, "llm")
    graph_builder.add_edge("llm", END)

    return graph_builder.compile(checkpointer=memory)


if __name__ == '__main__':
    test_graph = GraphWrapper.from_builder(
        CustomAgentState,
        "Be kind.",
        build_test_agent,
        InMemorySaver()
    )

    print(test_graph.get_state({"configurable": {"thread_id": "1"}}))

    test_graph.invoke(
        CustomAgentState(my_str="String", my_int=1),
        config={"configurable": {"thread_id": "1"}}
    )
    print(test_graph.get_state({"configurable": {"thread_id": "1"}}))

    test_graph.invoke(
        CustomAgentState(messages=[HumanMessage("Test 2")], my_str="String 2", my_int=2),
        config={"configurable": {"thread_id": "1"}}
    )
    print(test_graph.get_state({"configurable": {"thread_id": "1"}}))
