from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph
from src.products.service import ProductService
from src.recommendations.models import ProductRecommendation, RelevanceScoreList
from src.recommendations.query_agent.state import QueryEvaluation, QueryAgentState

EVAL_QUERY_PROMPT = (
    "You are a evaluator assessing relevance of a user query.\n"
    "Evaluate if the users query contains valid products, categories, or specific user needs "
    "related to e-commerce products.\n"
    "Guide the user with questions to improve the query and to add information to it.\n"
    "Once you gathered enough information consider the query to be valid and score it with True, "
    "score False otherwise.\n"
    "Also provide a cleaned-up version of the users query with the same semantic meaning and "
    "incorporating all answered questions, used for distance-based similarity search.\n"
    "There is always room for improvement, provide further guidance with questions, even if the "
    "query scored a True."
)

RANK_DOCS_PROMPT = (
    "You are a grader assessing relevance of retrieved documents to a user query.\n"
    "Here are the retrieved documents:\n\n{documents}\n\n"
    "Here is the user query: {query}\n\n"
    "If the documents contain keywords or semantic meaning related to the user query, grade it as "
    "relevant.\n"
    "Treat each document, identified by its id, separately and provide individual scores.\n"
    "Give a True or False to indicate whether the documents are relevant to the question."
)


class RecommendationService:
    def __init__(
            self,
            product_service: ProductService,
            llm: BaseChatModel,
            query_agent: CompiledStateGraph,
            vector_store: VectorStoreRetriever
    ):
        self._product_service = product_service
        self._llm = llm
        self._query_agent = query_agent
        self._vector_store = vector_store

    def evaluate_user_query(self, user_query: str, thread_id: str) -> QueryEvaluation:
        config = RunnableConfig(configurable={"thread_id": thread_id})
        past_messages = self._query_agent.get_state(config).values.get("messages")
        initial_messages = [SystemMessage(EVAL_QUERY_PROMPT)] if not past_messages else []

        return self._query_agent.invoke(
            input=QueryAgentState(messages=[*initial_messages, HumanMessage(user_query)]),
            config=config
        ).get("query_evaluation")

    def get_recommendations(self, query: str) -> list[ProductRecommendation] | None:
        documents = self._retrieve_relevant(query)
        if not documents:
            return None

        return self._map_documents_to_products(documents)

    def _retrieve_relevant(self, query: str) -> list[Document]:
        documents = self._retrieve(query)
        return self._filter_relevant_documents(query, documents)

    def _retrieve(self, query: str) -> list[Document]:
        return self._vector_store.invoke(query)

    def _filter_relevant_documents(self, query: str, documents: list[Document]) -> list[Document]:
        prompt = RANK_DOCS_PROMPT.format(
            query=query,
            documents="\n\n".join(map(
                lambda d: f"Id: {d.metadata.get('ref_id')}\nContent: {d.page_content}", documents
            ))
        )

        rankings = self._llm.with_structured_output(RelevanceScoreList).invoke(prompt)
        relevant_ids = [ranking.id for ranking in rankings.list if ranking.relevant]

        if not relevant_ids:
            return []

        return [d for d in documents if d.metadata.get("ref_id") in relevant_ids]

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
