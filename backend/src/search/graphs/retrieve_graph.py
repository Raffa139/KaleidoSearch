from langchain_core.language_models import BaseChatModel
from langchain_core.retrievers import BaseRetriever
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import InMemorySaver
from backend.src.search.graphs.graph_wrapper import GraphWrapper
from backend.src.search.graphs.retrieve_graph_state import RetrieveGraphState, RelevanceScoreList

FILTER_DOCS_PROMPT = (
    """
You are an expert grader tasked with evaluating the relevance of retrieved documents to a given 
user query. Your goal is to determine, for each document individually, whether it shares 
significant semantic meaning or keywords with the query.

Each document is presented in the following format:

Document ID: [document_id]
Content: [document_content]

Here are the retrieved documents:

{documents}

Here is the user query:

{query}

For each document listed above, carefully analyze its content and compare it to the user query. 
Consider both the presence of specific keywords and the overall semantic similarity.

Provide your evaluation for each document, where 'True' indicates that the document is highly 
relevant to the user query (sharing significant semantic meaning or keywords), and 'False' 
indicates that the document is not relevant. Ensure you provide a True/False evaluation for every 
document presented.
    """
)


def retrieve(retriever: BaseRetriever, s: RetrieveGraphState):
    def invoke(state: RetrieveGraphState):
        documents = retriever.invoke(state.query)
        return {"retrieved_documents": documents}

    return invoke(s)


def filter_relevant(llm: BaseChatModel, s: RetrieveGraphState):
    def invoke(state: RetrieveGraphState):
        prompt = FILTER_DOCS_PROMPT.format(
            query=state.query,
            documents="\n\n".join(map(
                lambda d: f"Document ID: {d.metadata.get('ref_id')}\nContent: {d.page_content}",
                state.retrieved_documents
            ))
        )

        rankings = llm.with_structured_output(RelevanceScoreList).invoke(prompt)
        relevant_ids = [ranking.id for ranking in rankings.list if ranking.relevant]

        return {"relevant_documents": [
            d for d in state.retrieved_documents if d.metadata.get("ref_id") in relevant_ids
        ]}

    return invoke(s)


def rerank_or_retrieve(state: RetrieveGraphState):
    return "rerank" if state.rerank_documents else "retrieve"


def summarize_or_end(state: RetrieveGraphState):
    return "summarize" if state.relevant_documents else END


def build_graph(
        llm: BaseChatModel,
        retriever: BaseRetriever,
        reranker: BaseRetriever
) -> CompiledStateGraph:
    graph_builder = StateGraph(RetrieveGraphState)

    graph_builder.add_node("retrieve", lambda state: retrieve(retriever, state))
    graph_builder.add_node("rerank", lambda state: retrieve(reranker, state))
    graph_builder.add_node("filter", lambda state: filter_relevant(llm, state))
    graph_builder.add_conditional_edges(START, rerank_or_retrieve)
    graph_builder.add_edge("rerank", "filter")
    graph_builder.add_edge("retrieve", "filter")
    graph_builder.add_edge("filter", END)

    return graph_builder.compile(checkpointer=InMemorySaver())


RetrieveGraph = GraphWrapper[RetrieveGraphState]


def build(
        llm: BaseChatModel,
        retriever: BaseRetriever,
        reranker: BaseRetriever
) -> RetrieveGraph:
    return GraphWrapper.from_builder(
        RetrieveGraphState,
        build_graph,
        None,
        llm,
        retriever,
        reranker
    )
