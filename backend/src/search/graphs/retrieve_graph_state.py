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


class SummarizedContent(BaseModel):
    id: int = Field(
        description="Identifier for the related document/product"
    )
    title: str = Field(
        description="New short and concise product title based on description"
    )
    description: str = Field(
        description="New and enhanced product description"
    )


class SummarizedContentList(BaseModel):
    list: List[SummarizedContent] = Field(
        description="New and enhanced product descriptions and titles"
    )


class RetrieveGraphState(MessageState):
    query: str
    title_length: int = 7
    summary_length: int = 100
    rerank_documents: bool = False
    retrieved_documents: List[Document] = []
    relevant_documents: List[Document] = []
    summarized_documents: List[Document] = []
