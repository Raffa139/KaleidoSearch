from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from src.recommendations.models import ProductRecommendation, UserQuery, BinaryScore, \
    BinaryScoreList
from src.products.service import ProductService

EVAL_QUERY_PROMPT = (
    "You are a evaluator assessing relevance of a user query.\n"
    "Evaluate if the users query contains valid products, categories, or specific user needs "
    "related to e-commerce products.\n"
    "Here is the user query: {query}\n\n"
    "Give a binary 'yes' or 'no' score to indicate whether the query is valid."
)

RANK_DOCS_PROMPT = (
    "You are a grader assessing relevance of retrieved documents to a user query.\n"
    "Here are the retrieved documents: \n\n{documents}\n\n"
    "Here is the user query: {query}\n\n"
    "If the documents contain keywords or semantic meaning related to the user query, grade it as "
    "relevant.\n"
    "Treat each document, identified by its id, separately and provide individual scores.\n"
    "Give a binary 'yes' or 'no' score to indicate whether the documents are relevant to the "
    "question."
)

AGGR_QUERY_PROMPT = (
    "Given the following user query and questions answered by the user, related to products, "
    "categories or specific user needs in e-commerce, combine them into one full query.\n"
    "Optimize the query for distance-based similarity search of a vector database.\n"
    "Only provide the new query, do not include any other content, explanations or examples.\n"
    "Here is the user query: {query}\n\n"
    "Here are the questions in the format (Q=question, A=user answer): \n\n{questions}\n\n"
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

        full_query = query if not query.questions else self._aggregate_user_query(query)
        documents = self._retrieve_relevant(full_query)
        if not documents:
            return None

        return self._map_documents_to_products(documents)

    def _evaluate_user_query(self, query: UserQuery) -> bool:
        prompt = EVAL_QUERY_PROMPT.format(query=query.query)
        response = self._llm.with_structured_output(BinaryScore).invoke(prompt)
        return response.score == "yes"

    def _retrieve_relevant(self, query: UserQuery) -> list[Document]:
        documents = self._retrieve(query)
        return self._filter_relevant_documents(query, documents)

    def _retrieve(self, query: UserQuery) -> list[Document]:
        return self._vector_store.invoke(query.query)

    def _filter_relevant_documents(
            self, query: UserQuery, documents: list[Document]
    ) -> list[Document]:
        # TODO: Better formatting of documents
        prompt = RANK_DOCS_PROMPT.format(
            query=query.query,
            documents="\n\n".join(map(
                lambda d: f"Id: {d.metadata.get('ref_id')}\nContent: {d.page_content}", documents
            ))
        )

        rankings = self._llm.with_structured_output(BinaryScoreList).invoke(prompt)
        relevant_ids = [ranking.id for ranking in rankings.list if ranking.score == "yes"]

        if not relevant_ids:
            return []

        return [d for d in documents if d.metadata.get("ref_id") in relevant_ids]

    def _aggregate_user_query(self, query: UserQuery) -> UserQuery:
        prompt = AGGR_QUERY_PROMPT.format(
            query=query.query,
            questions="\n\n".join(map(
                lambda q: f"Q: {q.question}\nA: {q.answer}", query.questions
            ))
        )

        response = self._llm.invoke(prompt)
        return UserQuery(query=response.content)

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
