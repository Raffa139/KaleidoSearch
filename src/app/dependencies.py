import chromadb
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine
from psycopg_pool import ConnectionPool
from langchain.retrievers import ContextualCompressionRetriever, MultiQueryRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langgraph.checkpoint.postgres import PostgresSaver
from src.search.graphs.search_graph import SearchGraph, build as build_search_graph
from src.search.graphs.retrieve_graph import RetrieveGraph, build as build_retrieve_graph
from src.environment import datasource_url, gemini_api_key

# TODO: Maybe create all dependencies here and none inside routers?

db_engine = create_engine(datasource_url())

# TODO: Make LLM configurable

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=gemini_api_key()
)

# TODO: Make Chroma connection settings configurable

bi_encoder = OpenAIEmbeddings(model="text-embedding-3-small")
cross_encoder = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L6-v2")
reranker = CrossEncoderReranker(model=cross_encoder, top_n=4)

chroma = Chroma(
    client=chromadb.HttpClient(host="localhost", port=5000),
    collection_name="kaleido_search_products",
    embedding_function=bi_encoder
)

chroma_retriever = chroma.as_retriever(search_kwargs={"k": 4})
rerank_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=chroma.as_retriever(search_kwargs={"k": 20})
)
multi_query_retriever = MultiQueryRetriever.from_llm(retriever=chroma_retriever, llm=llm)
multi_query_reranker = MultiQueryRetriever.from_llm(retriever=rerank_retriever, llm=llm)


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
    return build_retrieve_graph(llm, multi_query_retriever, multi_query_reranker)


def db_session():
    with Session(db_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(db_session)]

SearchGraphDep = Annotated[SearchGraph, Depends(search_graph)]

RetrieveGraphDep = Annotated[RetrieveGraph, Depends(retrieve_graph)]
