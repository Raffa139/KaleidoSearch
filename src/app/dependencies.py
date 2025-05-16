import chromadb
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine
from psycopg_pool import ConnectionPool
from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langgraph.checkpoint.postgres import PostgresSaver
from src.search.agents.search_agent import SearchAgentGraph, build_agent
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

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
chroma = Chroma(
    client=chromadb.HttpClient(host="localhost", port=5000),
    collection_name="kaleido_search_products",
    embedding_function=embeddings
)


def search_agent():
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
        yield build_agent(llm, memory)


def db_session():
    with Session(db_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(db_session)]

LLMDep = Annotated[BaseChatModel, Depends(lambda: llm)]

SearchAgentDep = Annotated[SearchAgentGraph, Depends(search_agent)]

VectorStoreRetrieverDep = Annotated[
    VectorStoreRetriever, Depends(lambda: chroma.as_retriever(search_kwargs={"k": 4}))
]
