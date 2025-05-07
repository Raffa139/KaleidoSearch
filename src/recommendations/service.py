from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from src.recommendations.models import ProductRecommendation, UserQuery, BinaryScore
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

    def get_recommendations(self, query: UserQuery) -> list[ProductRecommendation] | None:
        if not self._evaluate_user_query(query):
            return None

        documents = self._retrieve(query)
        if not self._rank_documents(query, documents):
            return None

        return self._map_documents_to_products(documents)

    def _evaluate_user_query(self, query: UserQuery) -> bool:
        prompt = EVAL_QUERY_PROMPT.format(query=query.query)
        response = self._llm.with_structured_output(BinaryScore).invoke(prompt)
        return response.score == "yes"

    def _retrieve(self, query: UserQuery) -> list[Document]:
        # TODO: Combine query & questions
        return self._vector_store.invoke(query.query)

    def _rank_documents(self, query: UserQuery, documents: list[Document]) -> bool:
        # TODO: Rank documents individually
        # TODO: Better formatting of documents
        prompt = RANK_DOCS_PROMPT.format(
            query=query.query,
            documents=", ".join(map(lambda d: d.page_content, documents))
        )
        response = self._llm.with_structured_output(BinaryScore).invoke(prompt)
        return response.score == "yes"

    def _map_documents_to_products(self, documents: list[Document]) -> list[ProductRecommendation]:
        ref_ids = [doc.metadata.get("ref_id") for doc in documents]
        products = self._product_service.find_by_ids(ref_ids)
        recommendations = []

        for document in documents:
            ref_id = document.metadata.get("ref_id")
            product = next(filter(lambda p: p.id == ref_id, products))
            recommendations.append(ProductRecommendation(
                **product.model_dump(),
                description=document.page_content
            ))

        return recommendations
