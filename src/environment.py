import os
from dotenv import load_dotenv

load_dotenv()


def datasource_url() -> str:
    return os.getenv("DATASOURCE_URL")


def product_catalogues() -> list[str]:
    return [s.strip() for s in os.getenv("PRODUCT_CATALOGUES", "").split(",") if s.strip()]
