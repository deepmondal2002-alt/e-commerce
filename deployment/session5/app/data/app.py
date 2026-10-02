import os
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from main import answer_question, build_clients, build_index, load_documents

DOCUMENT_PATH = os.getenv("DOCUMENT_PATH", "data/sample.txt")

app = FastAPI(title="production-rag", version="1.0.0")


class QueryRequest(BaseModel):
    question: str = "Summarise the document."
    top_k: int = Field(default=4, ge=1, le=20)


@lru_cache(maxsize=1)
def get_index() -> tuple:
    try:
        documents = load_documents(DOCUMENT_PATH)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    embeddings, llm = build_clients()
    store, chunks = build_index(documents, embeddings)
    return store, llm, len(documents), len(chunks)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "document": DOCUMENT_PATH}


@app.post("/query")
def query(request: QueryRequest) -> dict:
    store, llm, document_count, chunk_count = get_index()
    return {
        "question": request.question,
        "documents": document_count,
        "chunks": chunk_count,
        "answer": answer_question(store, llm, request.question, request.top_k),
    }
