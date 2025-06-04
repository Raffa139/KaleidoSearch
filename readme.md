# Kaleido Search

## AI-Powered Personalized Product Discovery Engine

![Project Version](https://img.shields.io/badge/Version-1.0-%23181717)
![Project Status](https://img.shields.io/badge/Status-Demo-blue)

## Tech Stack

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![React Router](https://img.shields.io/badge/React%20Router-CA4245?style=flat-square&logo=reactrouter&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![ChromaDB](https://img.shields.io/badge/-ChromaDB-orange?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=flat-square&logo=googlegemini&logoColor=white)

## Overview

Kaleido Search is an AI-powered product discovery engine that utilizes natural language
understanding and semantic search to provide intuitive and personalized product recommendations. It
allows users to describe desired products in their own words, intelligently surfacing relevant items
and guiding them through the search process.

## Features

* **Frontend**: Fully featured user interface.
* **Google Login**: Seamless authentication via Google.
* **User Accounts**: Personalized profiles with data from Google.
* **Text-Based Semantic Search**: Users can search using natural language queries.
* **Query Understanding**: Enhanced interpretation of user queries.
* **Guided Search**: Assists users in product discovery by providing helpful questions.
* **Optional Reranking**: Can be turned on to improve search result relevance.
* **Description Generation**: AI-generated product summaries.
* **Search History**: Records all past user searches.
* **Product Bookmarks**: Saves favorite products.

## Screenshots

### Login page

![](docs/login.png)

### Home page

![](docs/home.png)

### Search interface while search in progress

![](docs/searching.png)

### Search interface with results

![](docs/search-results.png)

### Bookmarks page

![](docs/bookmarks.png)

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Raffa139/KaleidoSearch.git
   cd KaleidoSearch
   ```
2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   cd frontend
   npm i
   ```
4. Set up your environment in `/backend/.env`:
   ```.env
   OPENAI_API_KEY="<Your-API-Key>"
   GOOGLE_API_KEY="<Your-API-Key>"
   
   AUTH_GOOGLE_CLIENT_ID="<Your-Google-Client-ID>"
   AUTH_SECRET_KEY="<Generate-Using-Openssl>"
   AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=60
   AUTH_ALGORITHM="HS256"
   
   DATASOURCE_URL="postgresql://kaleidosearch:secret@localhost:5432/kaleidosearch"
   CHROMA_HOST="localhost"
   CHROMA_PORT=5000
   CHROMA_COLLECTION="kaleido_search_products"

   SEARCH_MAX_RESULTS=4
   
   LLM_MODEL="gemini-2.0-flash"
   LLM_PROVIDER="google_genai"
   ```
   > **Note to authentication:**
   > As currently Google is the only supported auth provider `AUTH_GOOGLE_CLIENT_ID` is required. It
   comes with some extra steps to setup your own Google client
   ID https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid.
   > The `AUTH_SECRET_KEY` can be generated using `openssl rand -hex 32`.

   > **Note ot LLMs:**
   > To use a LLM from OpenAI, it is sufficient to only put in the model name and omit provider
   name `LLM_MODEL="gpt-4o-mini"`. For other LLM models/provider refer
   to https://python.langchain.com/docs/integrations/chat/.
5. Set up your environment in `/frontend/.env`:
   ```.env
   VITE_GOOGLE_CLIENT_ID="<Your-Google-Client-ID>"
   ```
   > **Note:**
   > `VITE_GOOGLE_CLIENT_ID` must be the same value as in the backend environment. Here is how to
   setup your own Google client
   ID https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid.

### Running the Application

1. Creating docker containers for Postgres & Chroma:
   ```bash
   cd setup/docker
   docker-compose up
   ```
2. Start the FastAPI server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

### Importing Data

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
   containers for Postgres & Chroma are up and running.
4. Run the `import_data.py` file inside `/backend/src/data_import`
   ```bash
   cd backend/src/data_import
   python import_data.py
   ```
5. Each catalog needs confirmation to proceed with the expensive persisting and embedding of data.
   ```bash
   Continue importing 39608 products? (Y/N): y
   ```
   ```bash
   python import_data.py --y # Skip confirmation mechanism & always proceed with the import
   ```
   > **Note:**
   > Embeddings are created using OpenAI's text-embedding-3-small, make sure to provide an OpenAI
   API-Key or go into `/backend/src/app/dependencies.py` and change the embedding model.

### Evaluate RAG

To evaluate RAG capabilities and compare actual with expected output, the file `evaluate_rag.py`
inside `/backend/src/data_import` can be executed.

```bash
cd backend/src/data_import
python evaluate_rag.py
```

It generates test queries based on the documents stored inside Chroma (import products before), by
default it will use product descriptions from the first catalog specified in `.env`. Each artificial
query goes through the whole retrieve pipeline and the actual vs. expected results will be shown in
the console.

Generated test data is stored inside `/backend/data` following naming schema
`testset_{catalog_name}.jsonl`.

This evaluation can be used to compare f. ex. the performance of a reranker or query expansion.

## Future Enhancements

* Attribute-Based filtering for traditional filtering options to refine search results.
* Extract keywords during import to use in traditional filtering.
* Import products from different sources or from web scraping.
* "More Like This" suggestions to find similar products to those being viewed.
* Develop personalized recommendation algorithms based on user behavior.
* Implement visual semantic search.
