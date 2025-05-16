from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from src.products.service import ProductService
from src.users.service import UserService
from src.search.models import ProductRecommendation, RelevanceScoreList, QueryEvaluationOut, \
    BaseUserSearch
from src.search.agent.state import SearchAgentState, QueryEvaluation
from src.search.agent.graph import SearchAgentGraph

RANK_DOCS_PROMPT = (
    """
You are an expert grader tasked with evaluating the relevance of retrieved documents to a given 
user query. Your goal is to determine, for each document individually, whether it shares 
significant semantic meaning or keywords with the query.

Each document is presented in the following format:

Document ID: [document_id]
Content: [document_content]

Here are the retrieved documents:

{documents}

Here is the user query:

{query}

For each document listed above, carefully analyze its content and compare it to the user query. 
Consider both the presence of specific keywords and the overall semantic similarity.

Provide your evaluation for each document, where 'True' indicates that the document is highly 
relevant to the user query (sharing significant semantic meaning or keywords), and 'False' 
indicates that the document is not relevant. Ensure you provide a True/False evaluation for every 
document presented.
    """
)


class SearchService:
    def __init__(
            self,
            product_service: ProductService,
            user_service: UserService,
            llm: BaseChatModel,
            search_agent: SearchAgentGraph,
            vector_store: VectorStoreRetriever
    ):
        self._product_service = product_service
        self._user_service = user_service
        self._llm = llm
        self._search_agent = search_agent
        self._vector_store = vector_store

    def evaluate_user_query(
            self,
            user_search: BaseUserSearch,
            user_id: int,
            thread_id: int | None
    ) -> QueryEvaluationOut:
        new_thread_id = self._user_service.create_thread(user_id).id if not thread_id else None
        config = self.__get_agent_config(thread_id if thread_id else new_thread_id)

        try:
            return self._evaluate_user_query(user_search, config)
        except Exception:
            if new_thread_id:
                self._user_service.delete_thread(new_thread_id)
            raise

    def get_recommendations(self, thread_id: int) -> list[ProductRecommendation] | None:
        config = self.__get_agent_config(thread_id)
        state = self._search_agent.get_state(config)
        query_evaluation = state.query_evaluation if state else None
        query = query_evaluation.cleaned_query if query_evaluation else None

        if not query:
            raise ValueError("User search needs refinement")

        if relevant_documents := self._retrieve_relevant(query):
            return self._map_documents_to_products(relevant_documents)

        return []

    def _evaluate_user_query(
            self,
            user_search: BaseUserSearch,
            config: RunnableConfig
    ) -> QueryEvaluationOut:
        if not user_search.has_content():
            raise ValueError("No query and no answers given, indicate at least one of the two")

        if not self.__user_answers_valid(user_search, config):
            raise ValueError("Answer IDs missmatch question IDs")

        if user_query := user_search.query:
            query_evaluation = self._invoke_search_agent(user_query, config)

        if formatted_answers := user_search.format_answers():
            query_evaluation = self._invoke_search_agent(formatted_answers, config)

        thread_id = config.get("configurable").get("thread_id")
        return QueryEvaluationOut(**query_evaluation.model_dump(), thread_id=thread_id)

    def _invoke_search_agent(self, query: str, config: RunnableConfig) -> QueryEvaluation:
        return self._search_agent.invoke(
            SearchAgentState(messages=[HumanMessage(query)]), config
        ).query_evaluation

    def _retrieve_relevant(self, query: str) -> list[Document]:
        documents = self._retrieve(query)
        return self._filter_relevant_documents(query, documents)

    def _retrieve(self, query: str) -> list[Document]:
        return self._vector_store.invoke(query)

    def _filter_relevant_documents(self, query: str, documents: list[Document]) -> list[Document]:
        prompt = RANK_DOCS_PROMPT.format(
            query=query,
            documents="\n\n".join(map(
                lambda d: f"Document ID: {d.metadata.get('ref_id')}\nContent: {d.page_content}",
                documents
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

    def __user_answers_valid(self, user_search: BaseUserSearch, config: RunnableConfig) -> bool:
        if not user_search.get_answers():
            return True

        state = self._search_agent.get_state(config)
        query_evaluation = state.query_evaluation if state else None
        follow_up_questions = query_evaluation.follow_up_questions if query_evaluation else []
        answered_questions = query_evaluation.answered_questions if query_evaluation else []
        all_question_ids = list(map(lambda q: q.id, follow_up_questions + answered_questions))
        answer_ids = list(map(lambda a: a.id, user_search.get_answers()))
        return all([answer_id in all_question_ids for answer_id in answer_ids])

    def __get_agent_config(self, thread_id: int) -> RunnableConfig:
        return RunnableConfig(configurable={"thread_id": thread_id})
