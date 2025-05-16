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
    DEFAULT_CONFIG = {"configurable": {"thread_id": "default"}}

    def __init__(self, grap: CompiledStateGraph, state_schema: type[T], prompt: str = None):
        self._graph = grap
        self._prompt = prompt
        self._state_schema = state_schema

    def invoke(self, input: T | str, config: RunnableConfig = DEFAULT_CONFIG, **kwargs) -> T:
        past_messages = self.get_dict_state(config).get("messages")
        system_message = [SystemMessage(self._prompt)] if not past_messages and self._prompt else []

        if isinstance(input, str):
            graph_input = {"messages": [*system_message, HumanMessage(input)]}
        else:
            graph_input = {**input.model_dump(), "messages": [*system_message, *input.messages]}

        result = self._graph.invoke(graph_input, config, **kwargs)
        return self._state_schema(**result)

    def get_state(self, config: RunnableConfig = DEFAULT_CONFIG) -> T | None:
        try:
            state_values = self.get_dict_state(config)
            return self._state_schema(**state_values)
        except ValidationError:
            return None

    def get_dict_state(self, config: RunnableConfig = DEFAULT_CONFIG):
        return self._graph.get_state(config).values

    @classmethod
    def from_builder(
            cls,
            state_schema: type[T],
            builder: Callable[..., CompiledStateGraph],
            prompt: str = None,
            *builder_args,
            **builder_kwargs
    ) -> "GraphWrapper":
        return GraphWrapper[T](
            builder(*builder_args, **builder_kwargs),
            state_schema,
            prompt
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
        build_test_agent,
        "Be kind.",
        InMemorySaver()
    )

    print(test_graph.get_state({"configurable": {"thread_id": "1"}}))

    test_graph.invoke(
        CustomAgentState(messages=[HumanMessage("Test")], my_str="String", my_int=1),
        config={"configurable": {"thread_id": "1"}}
    )
    print(test_graph.get_state({"configurable": {"thread_id": "1"}}))

    test_graph.invoke("Test 2", config={"configurable": {"thread_id": "1"}})
    print(test_graph.get_state({"configurable": {"thread_id": "1"}}))
