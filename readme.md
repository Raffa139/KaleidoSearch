# KaleidoSearch

## AI-Powered Personalized Product Discovery Engine

![Project Version](https://img.shields.io/badge/Version-1.0-%23181717)
![Project Status](https://img.shields.io/badge/Status-Development-blue)

## Tech Stack

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![ChromaDB](https://img.shields.io/badge/-ChromaDB-orange?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=flat-square&logo=googlegemini&logoColor=white)

## Overview

This project leverages AI and semantic search to help users discover products in a more intuitive
and personalized way. By utilizing natural language understanding and semantic search,
it aims to provide more relevant and personalized search results compared to traditional
keyword-based
approaches. Users can describe what they're looking for in their own words, and the engine will
intelligently surface relevant items from a product catalog and even guide the users through their
search endeavours.

## Features

* **Text-Based Semantic Search:** Users can search using natural language queries.
* **LLM Integration:** Enhanced query understanding, product description generation, and
  personalized explanations.
* **AI-Powered Recommendations:** Personalized product suggestions based on (future:
  explicit/implicit) preferences.
* **(Future): Attribute-Based Filtering:** Traditional filtering options to refine search results.
* **(Future): "More Like This" Suggestions:** Find similar products to those being viewed.
* **(Future): Visual Semantic Search:** Search using uploaded images.

## Getting Started

### Prerequisites

* Python 3.x
* Installation of necessary Python packages (see `requirements.txt`)
* Access to a vector database
* API key for your chosen LLM provider

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Raffa139/KaleidoSearch.git
   cd KaleidoSearch
   ```
2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   # Configure database settings in config file or environment variables
   ```
3. Set up your environment in `/backend/.env`:
   ```.env
   OPENAI_API_KEY="<Your-API-Key>"
   GOOGLE_API_KEY="<Your-API-Key>"
   
   AUTH_GOOGLE_CLIENT_ID="<Optional-Your-Google-Client-ID>"
   AUTH_SECRET_KEY="<Generate-Using-Openssl>"
   AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=60
   AUTH_ALGORITHM="HS256"
   
   DATASOURCE_URL="postgresql://kaleidosearch:secret@localhost:5432/kaleidosearch"
   CHROMA_HOST="localhost"
   CHROMA_PORT=5000
   CHROMA_COLLECTION="kaleido_search_products"
   
   LLM_MODEL="gemini-2.0-flash"
   LLM_PROVIDER="google_genai"
   ```
   > **Note to authentication:**
   > `AUTH_GOOGLE_CLIENT_ID` is only required if you plan to use Google as an ID provider. Here is
   how to setup your own Google client
   ID https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid.
   > The `AUTH_SECRET_KEY` can be generated using `openssl rand -hex 32`.

   > **Note ot LLMs:**
   > To use a LLM from OpenAI, it is sufficient to only put in the model name and omit provider
   name. For other LLM models/provider refer
   to https://python.langchain.com/docs/integrations/chat/.
4. Set up your environment in `/frontend/.env`:
   ```.env
   VITE_GOOGLE_CLIENT_ID="<Optional-Your-Google-Client-ID>"
   ```
   > **Note:**
   > `VITE_GOOGLE_CLIENT_ID` should be the same value as in the backend .env, it is only required if
   you plan to use Google as an ID provider. Here is how to setup your own Google client
   ID https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid.

### Running the Application

1. Create the DB docker container:
   ```bash
   cd setup/docker
   docker-compose up
   ```
2. Start the FastAPI server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

## Data

To populate the product catalog you can download amazon product metadata from the
[Amazon Reviews'23](https://amazon-reviews-2023.github.io/#grouped-by-category) page.
Choose a category of your likings (or all) and download the product metadata via the 'meta' link.

1. Put the downloaded product metadata files into the `/backend/data` directory
2. Provide the file names and max. token limit/minute in `/backend/.env`
   ```.env
   IMPORT_PRODUCT_CATALOGUES="<Filenames-Separated-By-Comma>"
   IMPORT_MAX_TOKENS_PER_MINUTE=100_000
   ```
3. Make sure the main application ran at least once to create the database schema and docker
   containers for DB & Vector Store are up and running
4. Run the `import_data.py` file inside `/backend/src/data_import`
   ```bash
   cd backend/src/data_import
   python import_data.py
   ```
5. Each catalog needs confirmation to proceed with the expensive persisting and embedding of the
   data, after products have been extracted
   ```bash
   Continue importing 39608 products? (Y/N): y
   ```
   ```bash
   python import_data.py --y # Skip confirmation mechanism & always proceed with the import
   ```
   > **Note:**
   > Embeddings are created using OpenAI's text-embedding-3-small, make sure to provide an OpenAI
   API-Key or go into `/backend/src/app/dependencies.py` and change the embedding model.

## Evaluate RAG

To evaluate RAG capabilities and compare actual with expected output, the file `evaluate_rag.py`
inside `/backend/src/data_import` can be executed.

```bash
cd backend/src/data_import
python evaluate_rag.py
```

It generates test queries based on the documents stored
inside chroma (import products before), by default it will use product descriptions from the first
catalog specified in `.env`. Each artificial query goes through the whole retrieve pipeline and the
actual vs. expected results will be shown in the console.

Generated test data is stored inside `/backend/data` following naming schema
`testset_{catalog_name}.jsonl`.

This evaluation can be used to compare f. ex. the performance of a reranker or query expansion.

## Future Enhancements

* Implement visual semantic search.
* Develop personalized recommendation algorithms based on user behavior.
* Add user accounts and preference management.
* Improve the UI/UX with more advanced filtering and visualization options.
