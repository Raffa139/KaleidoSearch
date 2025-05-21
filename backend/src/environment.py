import os
from dotenv import load_dotenv

load_dotenv()


def datasource_url() -> str:
    return os.getenv("DATASOURCE_URL")


def chroma_host() -> str:
    return os.getenv("CHROMA_HOST")


def chroma_port() -> int:
    return int(os.getenv("CHROMA_PORT"))


def chroma_collection() -> str:
    return os.getenv("CHROMA_COLLECTION")


def gemini_api_key() -> str:
    return os.getenv("GEMINI_API_KEY")


def openai_api_key() -> str:
    return os.getenv("OPENAI_API_KEY")


def llm_model() -> str:
    return os.getenv("LLM_MODEL")


def llm_provider() -> str:
    return os.getenv("LLM_PROVIDER")


def product_catalogues() -> list[str]:
    return [s.strip() for s in os.getenv("IMPORT_PRODUCT_CATALOGUES", "").split(",") if s.strip()]


def max_tokens_minute() -> int:
    return int(os.getenv("IMPORT_MAX_TOKENS_PER_MINUTE"))
