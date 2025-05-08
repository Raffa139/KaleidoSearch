import chromadb
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine
from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from src.recommendations.query_agent.agent import build_agent
from src.environment import datasource_url, gemini_api_key

db_engine = create_engine(datasource_url())

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=gemini_api_key()
)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
chroma = Chroma(
    client=chromadb.HttpClient(host="localhost", port=5000),
    collection_name="kaleido_search_products",
    embedding_function=embeddings
).as_retriever(search_kwargs={"k": 2})

# TODO: Persist chats in DB
query_agent = build_agent(llm, InMemorySaver())


def db_session():
    with Session(db_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(db_session)]

LLMDep = Annotated[BaseChatModel, Depends(lambda: llm)]

QueryAgentDep = Annotated[CompiledStateGraph, Depends(lambda: query_agent)]

VectorStoreDep = Annotated[VectorStoreRetriever, Depends(lambda: chroma)]
