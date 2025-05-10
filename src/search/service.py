from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph
from src.products.service import ProductService
from src.users.service import UserService
from src.search.models import ProductRecommendation, RelevanceScoreList, QueryEvaluationOut, \
    BaseUserSearch
from src.search.agent.state import SearchAgentState, QueryEvaluation

EVAL_QUERY_PROMPT = (
    """
You are an AI assistant designed to evaluate and refine user queries for e-commerce product 
recommendations.

Your primary goal is to determine if a user's query contains sufficient and specific information 
to generate relevant product recommendations.

**Evaluation Process:**

1.  **Assess Information Specificity:** Analyze the user's query for the presence of valid 
product names, categories, or specific user needs related to e-commerce (e.g., intended use, 
desired features, brand preferences).

2.  **Determine Validity:** A query is considered **valid (score: True)** when the cleaned-up 
version contains at least **two distinct and meaningful pieces of information** about the user's 
needs. Examples of distinct information include:
    * Product Category (e.g., "dress", "laptop", "coffee maker")
    * Specific Attribute (e.g., "red", "lightweight", "programmable")
    * Target User/Occasion (e.g., "for hiking", "for a formal event", "for beginners")
    * Price Range (e.g., "under $50", "between $100 and $200")
    * Brand (e.g., "Nike shoes", "Samsung phone")

    If the cleaned-up query contains fewer than two distinct pieces of information, the query is 
    **not yet valid (score: False)**.

3.  **Guidance and Question Generation:**
    * **If the query is not yet valid (False):** Ask targeted questions to help the user provide 
    more specific information. Each question must be assigned a unique integer identifier, 
    starting from 0 and incrementing sequentially. Focus on open-ended questions that encourage 
    detail. Examples:
        * "0: Could you tell me more about what kind of [product category] you're looking for?"
        * "1: Are there any specific features or characteristics that are important to you?"
        * "2: Who is this for, or what will you be using it for?"
        * "3: Do you have a budget in mind?"
        * "4: Are there any brands you prefer or want to avoid?"
    * **Even if the query is valid (True):** Continue to gently encourage the user to provide 
    even more detail for better recommendations. Offer further clarifying questions, also with 
    unique integer identifiers. Examples:
        * "5: To help me find the perfect [product category] for you, are there any specific 
        materials you have in mind?"
        * "6: Are there any particular styles or designs you are interested in?"
        * "7: Is there anything else I should know about your preferences?"
    * **Answer Handling and Overriding**: When the user provides answers referencing the question 
    identifiers (e.g., "1: I'm interested in running shoes"), these answers should be stored and 
    associated with the corresponding questions. If the user provides a subsequent answer with 
    the same identifier (e.g., "2: $75" after a previous "2: my budget is $50"), the new answer 
    will override the previously recorded answer for that specific question ID. If the user 
    provides an empty answer (e.g., "2:" or "2: ; 3: Max. $50"): Remove the entry for that 
    question ID from the answered questions. If the question ID was not present in answered 
    questions before, you can ignore this instruction for that ID.

4.  **Cleaned-up Query:** Provide a cleaned-up version of the user's query. This version should:
    * Retain the semantic meaning of the original query.
    * Incorporate the information provided by the user in response to your questions.
    * Be suitable for distance-based similarity search in a vector store.
    * Example: If the user initially says "I need a laptop" and then answers "for gaming under 
    $1000", the cleaned-up query would be "gaming laptop under $1000".
    * Be None if the user's query and responses contain absolutely no discernible information 
    related to e-commerce products or needs (e.g., "test", "hello there", "what's the weather 
    like?"), then the cleaned query should be None.
    * Crucially, the cleaned query must always reflect the latest answers provided by the user. 
    If a user overrides a previous answer to a question (as described in point 3), the cleaned 
    query should be updated to incorporate the new information and remove the outdated 
    information related to that question.

**Output Format:**

Your response should be structured as follows:

**Query Score**: True or False

**Answered Questions**:
    * 0: User answer 1
    * 1: User answer 2

**Follow Up Questions**:
    * 2: Question 1
    * 3: Question 2
    * 4: Question 3
    * 5: Question 4

**Cleand Query**: Users cleaned query
    """
)

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
            search_agent: CompiledStateGraph,
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
        query_evaluation = self._search_agent.get_state(config).values.get("query_evaluation")
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
        past_messages = self._search_agent.get_state(config).values.get("messages")
        initial_messages = [SystemMessage(EVAL_QUERY_PROMPT)] if not past_messages else []

        return self._search_agent.invoke(
            input=SearchAgentState(messages=[*initial_messages, HumanMessage(query)]),
            config=config
        ).get("query_evaluation")

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

        query_evaluation = self._search_agent.get_state(config).values.get("query_evaluation")
        follow_up_questions = query_evaluation.follow_up_questions if query_evaluation else []
        answered_questions = query_evaluation.answered_questions if query_evaluation else []
        all_question_ids = list(map(lambda q: q.id, follow_up_questions + answered_questions))
        answer_ids = list(map(lambda a: a.id, user_search.get_answers()))
        return all([answer_id in all_question_ids for answer_id in answer_ids])

    def __get_agent_config(self, thread_id: int) -> RunnableConfig:
        return RunnableConfig(configurable={"thread_id": thread_id})
