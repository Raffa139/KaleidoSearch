from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from .manual_agent import evaluate_user_query, retrieve, rank_documents

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/", response_model=list[str])
def get_recommendations(q: str):
    if not evaluate_user_query(q):
        raise HTTPException(status_code=400)

    documents = retrieve(q)
    if not rank_documents(q, documents):
        raise HTTPException(status_code=400)

    return documents
