import os
from dotenv import load_dotenv

load_dotenv()


def datasource_url():
    return os.getenv("DATASOURCE_URL")


def gemini_api_key():
    return os.getenv("GEMINI_API_KEY")
