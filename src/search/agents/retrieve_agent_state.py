from typing import List
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from src.search.agents.graph_wrapper import MessageState


class RelevanceScore(BaseModel):
    id: int = Field(
        description="Identifier for the related document"
    )
    relevant: bool = Field(
        description="Relevance score: True if relevant, or False if not relevant"
    )


class RelevanceScoreList(BaseModel):
    list: List[RelevanceScore] = Field(description="Relevance scores of documents")


class RetrieveAgentState(MessageState):
    query: str
    retrieved_documents: List[Document] = []
    reranked_documents: List[Document] = []
    relevant_documents: List[Document] = []
