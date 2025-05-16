from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import InMemorySaver
from src.search.agents.graph_wrapper import GraphWrapper
from src.search.agents.retrieve_agent_state import RetrieveAgentState, RelevanceScoreList, \
    SummarizedContentList

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

SUMMARIZE_PROMPT = (
    """
You are an AI E-commerce expert who writes compelling product descriptions.
I am going to provide a list of e-commerce product descriptions in the form of documents. Each 
document has a unique ID and I want you to rewrite and enhance all descriptions. The new 
descriptions should be referenced to their original document using its ID.

Each document/product is presented in the following format:

Document ID: [document_id]
Description: [product_description]

The main point of these commands is for you to develop new informative, and captivating 
product summaries/descriptions which are less than {n_words} words long. The purpose of product 
descriptions is marketing the products to users looking to buy.

Do not use any kind of text formatting besides line breaks. Do not echo my prompt. Do not remind 
me what I asked you for. Do not apologize. Do not self-reference.

Here are the documents/products:

{documents}
    """
)


def retrieve(vector_store: VectorStoreRetriever, s: RetrieveAgentState):
    def invoke(state: RetrieveAgentState):
        documents = vector_store.invoke(state.query)
        return {"retrieved_documents": documents}

    return invoke(s)


def rerank(state: RetrieveAgentState):
    pass


def filter_relevant(llm: BaseChatModel, s: RetrieveAgentState):
    def invoke(state: RetrieveAgentState):
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


def summarize(llm: BaseChatModel, s: RetrieveAgentState):
    def invoke(state: RetrieveAgentState):
        prompt = SUMMARIZE_PROMPT.format(
            n_words=state.summary_length,
            documents="\n\n".join(map(
                lambda d: f"Document ID: {d.metadata.get('ref_id')}\nDescription: {d.page_content}",
                state.relevant_documents
            ))
        )

        # TODO: Increase temperatur for this
        summaries = llm.with_structured_output(SummarizedContentList).invoke(prompt)

        return {"summarized_documents": [
            Document(d.description, metadata={"ref_id": d.id}) for d in summaries.list
        ]}

    return invoke(s)


def build_graph(llm: BaseChatModel, vector_store: VectorStoreRetriever) -> CompiledStateGraph:
    graph_builder = StateGraph(RetrieveAgentState)

    graph_builder.add_node("retrieve", lambda state: retrieve(vector_store, state))
    graph_builder.add_node("filter", lambda state: filter_relevant(llm, state))
    graph_builder.add_node("summarize", lambda state: summarize(llm, state))
    graph_builder.add_edge(START, "retrieve")
    graph_builder.add_edge("retrieve", "filter")
    graph_builder.add_edge("filter", "summarize")
    graph_builder.add_edge("summarize", END)

    return graph_builder.compile(checkpointer=InMemorySaver())


RetrieveAgentGraph = GraphWrapper[RetrieveAgentState]


def build_agent(llm: BaseChatModel, vector_store: VectorStoreRetriever) -> RetrieveAgentGraph:
    return GraphWrapper.from_builder(
        RetrieveAgentState,
        build_graph,
        None,
        llm,
        vector_store
    )
