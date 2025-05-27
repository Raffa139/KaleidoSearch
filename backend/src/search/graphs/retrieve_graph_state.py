from typing import List
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from backend.src.search.graphs.graph_wrapper import MessageState


class RelevanceScore(BaseModel):
    id: int = Field(
        description="Identifier for the related document"
    )
    relevant: bool = Field(
        description="Relevance score: True if relevant, or False if not relevant"
    )


class RelevanceScoreList(BaseModel):
    list: List[RelevanceScore] = Field(description="Relevance scores of documents")


class RetrieveGraphState(MessageState):
    query: str
    rerank_documents: bool = False
    retrieved_documents: List[Document] = []
    relevant_documents: List[Document] = []
