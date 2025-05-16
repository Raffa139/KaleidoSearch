from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from src.products.service import ProductService
from src.users.service import UserService
from src.search.models import ProductRecommendation, QueryEvaluationOut, BaseUserSearch
from src.search.agents.search_agent import SearchAgentGraph, SearchAgentState, QueryEvaluation
from src.search.agents.retrieve_agent import RetrieveAgentGraph, RetrieveAgentState




class SearchService:
    def __init__(
            self,
            product_service: ProductService,
            user_service: UserService,
            search_agent: SearchAgentGraph,
            retrieve_agent: RetrieveAgentGraph
    ):
        self._product_service = product_service
        self._user_service = user_service
        self._search_agent = search_agent
        self._retrieve_agent = retrieve_agent

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

        if relevant_documents := self._retrieve_agent.invoke(
                RetrieveAgentState(query=query)
        ).relevant_documents:
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
