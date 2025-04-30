import os
from dotenv import load_dotenv

load_dotenv()


def datasource_url():
    return os.getenv("DATASOURCE_URL")
