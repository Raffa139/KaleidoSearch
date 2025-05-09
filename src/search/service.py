from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph
from src.products.service import ProductService
from src.users.service import UserService
from src.search.models import ProductRecommendation, RelevanceScoreList
from src.search.agent.state import QueryEvaluation, SearchAgentState

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
    more specific information. Focus on open-ended questions that encourage detail. Examples:
        * "Could you tell me more about what kind of [product category] you're looking for?"
        * "Are there any specific features or characteristics that are important to you?"
        * "Who is this for, or what will you be using it for?"
        * "Do you have a budget in mind?"
        * "Are there any brands you prefer or want to avoid?"
    * **Even if the query is valid (True):** Continue to gently encourage the user to provide 
    even more detail for better recommendations. Offer further clarifying questions. Examples:
        * "To help me find the perfect [product category] for you, are there any specific 
        materials you have in mind?"
        * "Are there any particular styles or designs you are interested in?"
        * "Is there anything else I should know about your preferences?"

4.  **Cleaned-up Query:** Provide a cleaned-up version of the user's query. This version should:
    * Retain the semantic meaning of the original query.
    * Incorporate the information provided by the user in response to your questions.
    * Be suitable for distance-based similarity search in a vector store.
    * Example: If the user initially says "I need a laptop" and then answers "for gaming under 
    $1000", the cleaned-up query would be "gaming laptop under $1000".
    * Be None if the user's query and responses contain absolutely no discernible information 
    related to e-commerce products or needs (e.g., "test", "hello there", "what's the weather 
    like?"), then the cleaned query should be None.

**Output Format:**

Your response should be structured as follows:

**Query Score**: True or False

**Questions**:
    * Question 1
    * Question 2
    * Question 3
    * Question 4

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
            user_query: str,
            user_id: int,
            thread_id: int | None
    ) -> QueryEvaluation:
        new_thread_id = self._user_service.create_thread(user_id).id if not thread_id else None
        thread_id = thread_id if thread_id else new_thread_id

        config = self.__get_agent_config(thread_id)
        past_messages = self._search_agent.get_state(config).values.get("messages")
        initial_messages = [SystemMessage(EVAL_QUERY_PROMPT)] if not past_messages else []

        try:
            return self._search_agent.invoke(
                input=SearchAgentState(messages=[*initial_messages, HumanMessage(user_query)]),
                config=config
            ).get("query_evaluation")
        except Exception:
            if new_thread_id:
                self._user_service.delete_thread(new_thread_id)
            raise

    def get_recommendations(self, thread_id: int) -> list[ProductRecommendation] | None:
        config = self.__get_agent_config(thread_id)
        query_evaluation = self._search_agent.get_state(config).values.get("query_evaluation")
        query = query_evaluation.cleaned_query if query_evaluation else None

        if not query:
            return None

        relevant_documents = self._retrieve_relevant(query)
        if not relevant_documents:
            return []

        return self._map_documents_to_products(relevant_documents)

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

    def __get_agent_config(self, thread_id: int) -> RunnableConfig:
        return RunnableConfig(configurable={"thread_id": thread_id})
