from typing import List
from pydantic import BaseModel, Field
from backend.src.search.graphs.graph_wrapper import MessageState


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


class ProductSummary(BaseModel):
    id: int
    ai_title: str
    ai_description: str


class SummarizeGraphState(MessageState):
    product_ids: List[int]
    title_length: int = 7
    summary_length: int = 100
    summarized_products: List[ProductSummary] = []
