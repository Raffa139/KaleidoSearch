from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_chroma.vectorstores import Chroma
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import InMemorySaver
from backend.src.search.graphs.graph_wrapper import GraphWrapper
from backend.src.products.graphs.summarize_graph_state import SummarizeGraphState, \
    SummarizedContentList, ProductSummary

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
for. Do not apologize. Do not self-reference. Do not include Document IDs in your output. Only 
write one description and title per document, even if only one document is provided.

Here are the documents/products:

{documents}
    """
)


def summarize(llm: BaseChatModel, chroma: Chroma, s: SummarizeGraphState):
    def invoke(state: SummarizeGraphState):
        product_documents: list[Document] = []

        for product_id in state.product_ids:
            chroma_result = chroma.get(where={"ref_id": product_id})
            [page_content] = chroma_result.get("documents")
            [metadata] = chroma_result.get("metadatas")
            product_documents.append(Document(page_content, metadata=metadata))

        prompt = SUMMARIZE_PROMPT.format(
            n_words_titles=state.title_length,
            n_words_descriptions=state.summary_length,
            documents="\n\n".join(map(
                lambda d: f"Document ID: {d.metadata.get('ref_id')}\nDescription: {d.page_content}",
                product_documents
            ))
        )

        # TODO: Increase temperatur for this -> https://python.langchain.com/docs/how_to/configure/
        summaries = llm.with_structured_output(SummarizedContentList).invoke(prompt)

        return {"summarized_products": [
            ProductSummary(
                id=summary.id,
                ai_title=summary.title,
                ai_description=summary.description
            ) for summary in summaries.list
        ]}

    return invoke(s)


def build_graph(llm: BaseChatModel, chroma: Chroma) -> CompiledStateGraph:
    graph_builder = StateGraph(SummarizeGraphState)

    graph_builder.add_node("summarize", lambda state: summarize(llm, chroma, state))
    graph_builder.add_edge(START, "summarize")
    graph_builder.add_edge("summarize", END)

    return graph_builder.compile(checkpointer=InMemorySaver())


SummarizeGraph = GraphWrapper[SummarizeGraphState]


def build(llm: BaseChatModel, chroma: Chroma) -> SummarizeGraph:
    return GraphWrapper.from_builder(
        SummarizeGraphState,
        build_graph,
        None,
        llm,
        chroma
    )
