from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever

from src.products.models import ProductBase
from src.products.service import ProductService

EVAL_QUERY_PROMPT = (
    "You are a evaluator assessing relevance of a user query.\n"
    "Evaluate if the users query contains valid products, categories, or specific user needs "
    "related to e-commerce products."
    "Here is the user query: {query} \n"
    "Give a binary 'yes' or 'no' score to indicate whether the query is valid."
)

RANK_DOCS_PROMPT = (
    "You are a grader assessing relevance of retrieved documents to a user query.\n"
    "Here are the retrieved documents: \n\n{documents}\n\n"
    "Here is the user query: {query} \n"
    "If the documents contain keywords or semantic meaning related to the user query, grade it as "
    "relevant.\n"
    "Give a binary 'yes' or 'no' score to indicate whether the documents are relevant to the "
    "question."
)


class BinaryScore(BaseModel):
    score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


class Question(BaseModel):
    question: str
    answer: str


class UserQuery(BaseModel):
    query: str
    questions: list[Question] | None = None


class ProductRecommendation(ProductBase):
    description: str


class RecommendationService:
    def __init__(
            self,
            product_service: ProductService,
            llm: BaseChatModel,
            vector_store: VectorStoreRetriever
    ):
        self._product_service = product_service
        self._llm = llm
        self._vector_store = vector_store

    def get_recommendations(self, query: UserQuery) -> list[str] | None:
        if not self._evaluate_user_query(query):
            return None

        documents = self._retrieve(query)
        if not self._rank_documents(query, documents):
            return None

        return documents

    def _evaluate_user_query(self, query: UserQuery) -> bool:
        prompt = EVAL_QUERY_PROMPT.format(query=query.query)
        response = self._llm.with_structured_output(BinaryScore).invoke(prompt)
        return response.score == "yes"

    def _retrieve(self, query: UserQuery) -> list[str]:
        # TODO: Combine query & questions
        documents = self._vector_store.invoke(query.query)
        ref_ids = [doc.metadata.get("ref_id") for doc in documents]
        return [doc.page_content for doc in documents]

    def _rank_documents(self, query: UserQuery, documents: list[str]) -> bool:
        # TODO: Rank documents individually
        # TODO: Better formatting of documents
        prompt = RANK_DOCS_PROMPT.format(query=query.query, documents=", ".join(documents))
        response = self._llm.with_structured_output(BinaryScore).invoke(prompt)
        return response.score == "yes"
