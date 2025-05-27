import chromadb
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine
from psycopg_pool import ConnectionPool
from langchain.chat_models import init_chat_model
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langgraph.checkpoint.postgres import PostgresSaver
from backend.src.search.graphs.search_graph import SearchGraph, build as build_search_graph
from backend.src.search.graphs.retrieve_graph import RetrieveGraph, build as build_retrieve_graph
from backend.src.products.graphs.summarize_graph import SummarizeGraph, \
    build as build_summarize_graph
from backend.src.environment import datasource_url, chroma_host, chroma_port, chroma_collection, \
    llm_model, llm_provider

# TODO: Maybe create all dependencies here and none inside routers?

db_engine = create_engine(datasource_url())

llm = init_chat_model(llm_model(), model_provider=llm_provider(), temperature=0)

bi_encoder = OpenAIEmbeddings(model="text-embedding-3-small")
cross_encoder = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L6-v2")
reranker = CrossEncoderReranker(model=cross_encoder, top_n=4)

chroma = Chroma(
    client=chromadb.HttpClient(host=chroma_host(), port=chroma_port()),
    collection_name=chroma_collection(),
    embedding_function=bi_encoder
)

chroma_retriever = chroma.as_retriever(search_kwargs={"k": 4})
rerank_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=chroma.as_retriever(search_kwargs={"k": 20})
)


def search_graph():
    with ConnectionPool(
            datasource_url(),
            max_size=20,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0
            }
    ) as pool:
        memory = PostgresSaver(pool)
        memory.setup()
        yield build_search_graph(llm, memory)


def retrieve_graph():
    return build_retrieve_graph(llm, chroma_retriever, rerank_retriever)


def summarize_graph():
    return build_summarize_graph(llm, chroma)


def db_session():
    with Session(db_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(db_session)]

SearchGraphDep = Annotated[SearchGraph, Depends(search_graph)]

RetrieveGraphDep = Annotated[RetrieveGraph, Depends(retrieve_graph)]

SummarizeGraphDep = Annotated[SummarizeGraph, Depends(summarize_graph)]
