import os
import chromadb
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.definitions import DATA_DIR
from src.environment import openai_api_key
from src.data_import.stopwatch import Stopwatch

"""
Evaluation of embedding models
  * sentence-transformers/all-MiniLM-L6-v2
  * sentence-transformers/all-mpnet-base-v2
  * intfloat/multilingual-e5-small
  * intfloat/multilingual-e5-large-instruct (Not working)
  * Snowflake/snowflake-arctic-embed-m-v2.0 (Not working)
  * openai/text-embedding-3-small
"""

TEST_DATA_FILE = "f_105_metas.csv"
TEST_QUERY = "neutralize itching from stings and bites"


def test_data() -> list[str]:
    with open(os.path.join(DATA_DIR, TEST_DATA_FILE), encoding="utf-8") as file:
        data = [line for line in file]
    return data


def test_documents() -> list[Document]:
    return [Document(page_content=data) for data in test_data()]


def init_chroma(embeddings: Embeddings) -> Chroma:
    return Chroma(
        client=chromadb.EphemeralClient(),
        collection_name="test_kaleido_search_products",
        embedding_function=embeddings
    )


def all_minilm_l6_v2() -> tuple[str, Embeddings]:
    model_name = "all-MiniLM-L6-v2"
    return model_name, HuggingFaceEmbeddings(model_name=f"sentence-transformers/{model_name}")


def all_mpnet_base_v2() -> tuple[str, Embeddings]:
    model_name = "all-mpnet-base-v2"
    return model_name, HuggingFaceEmbeddings(model_name=f"sentence-transformers/{model_name}")


def multilingual_e5_small() -> tuple[str, Embeddings]:
    model_name = "multilingual-e5-small"
    return model_name, HuggingFaceEmbeddings(
        model_name=f"intfloat/{model_name}",
        encode_kwargs={"normalize_embeddings": True}
    )


def text_embedding_3_small() -> tuple[str, Embeddings]:
    model_name = "text-embedding-3-small"
    return model_name, OpenAIEmbeddings(model=model_name)


# def multilingual_e5_large_instruct() -> tuple[str, Embeddings]:
#    model_name = "multilingual-e5-large-instruct"
#    return model_name, HuggingFaceInstructEmbeddings(
#        query_instruction=(
#            "Given a e-commerce product related query, retrieve relevant passages that fulfill "
#            "the query: "),
#        model_name=f"intfloat/{model_name}",
#        encode_kwargs={"normalize_embeddings": True, "convert_to_tensor": True}
#    )


# def snowflake_arctic_embed_m_v2() -> tuple[str, Embeddings]:
#    model_name = "snowflake-arctic-embed-m-v2.0"
#    return model_name, HuggingFaceEmbeddings(
#        model_name=f"Snowflake/{model_name}",
#        model_kwargs={"trust_remote_code": True}
#    )


def eval_model(model: str, embeddings: Embeddings):
    watch = Stopwatch()
    print(f"Evaluate model {model}")

    chroma = init_chroma(embeddings)
    chroma.add_documents(test_documents())
    print(f"Embedded documents in: {watch}")

    results = chroma.similarity_search(TEST_QUERY)
    results_file = f"{model}.csv"

    with open(os.path.join(DATA_DIR, results_file), mode="w", encoding="utf-8") as file:
        file.writelines([doc.page_content for doc in results] + [f"Runtime: {watch.stop()}ms"])

    print(f"Results written to {results_file}")


def main():
    model_name, embeddings = text_embedding_3_small()
    eval_model(model_name, embeddings)


if __name__ == '__main__':
    main()
