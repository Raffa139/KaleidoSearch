from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.retrievers import BaseRetriever
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import InMemorySaver
from backend.src.search.graphs.graph_wrapper import GraphWrapper
from backend.src.search.graphs.retrieve_graph_state import RetrieveGraphState, RelevanceScoreList, \
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
You are an AI E-commerce expert who writes compelling product descriptions and titles.
I am going to provide a list of e-commerce product descriptions in the form of documents. Each 
document has a unique ID and I want you to rewrite and enhance all descriptions and generate a 
short and concise product title for each description. The new descriptions should be referenced 
to their original document using its ID.

Each document/product is presented in the following format:

Document ID: [document_id]
Description: [product_description]

The main point of these commands is for you to develop new informative, and captivating product 
summaries/descriptions which are about {n_words_descriptions} words long. And to develop precise 
product titles based on the enhanced description which are {n_words_titles} words long. The 
purpose of product descriptions and titles is marketing the products to users looking to buy.

Do not use any kind of text formatting. Do not echo my prompt. Do not remind me what I asked you 
for. Do not apologize. Do not self-reference. Do not include Document IDs in your output.

Here are the documents/products:

{documents}
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


def summarize(llm: BaseChatModel, s: RetrieveGraphState):
    def invoke(state: RetrieveGraphState):
        prompt = SUMMARIZE_PROMPT.format(
            n_words_titles=state.title_length,
            n_words_descriptions=state.summary_length,
            documents="\n\n".join(map(
                lambda d: f"Document ID: {d.metadata.get('ref_id')}\nDescription: {d.page_content}",
                state.relevant_documents
            ))
        )

        # TODO: Increase temperatur for this -> https://python.langchain.com/docs/how_to/configure/
        summaries = llm.with_structured_output(SummarizedContentList).invoke(prompt)

        return {"summarized_documents": [
            Document(
                content.description,
                metadata={"ref_id": content.id, "ai_title": content.title}
            ) for content in summaries.list
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
    graph_builder.add_node("summarize", lambda state: summarize(llm, state))
    graph_builder.add_conditional_edges(START, rerank_or_retrieve)
    graph_builder.add_edge("rerank", "filter")
    graph_builder.add_edge("retrieve", "filter")
    graph_builder.add_conditional_edges("filter", summarize_or_end)
    graph_builder.add_edge("summarize", END)

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
