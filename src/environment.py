import os
from dotenv import load_dotenv

load_dotenv()


def datasource_url() -> str:
    return os.getenv("DATASOURCE_URL")


def gemini_api_key() -> str:
    return os.getenv("GEMINI_API_KEY")


def openai_api_key() -> str:
    return os.getenv("OPENAI_API_KEY")


def product_catalogues() -> list[str]:
    return [s.strip() for s in os.getenv("PRODUCT_CATALOGUES", "").split(",") if s.strip()]
