from jmespath import search
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

VECTOR_STORE = None
RAG_CHAIN = None

TEST_MODE = os.getenv("TEST_MODE", "false") == "true"

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag():
    docs = TextLoader("data/company_policy.md", encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=120).split_documents(docs)
    store = FAISS.from_documents(chunks, GoogleGenerativeAIEmbeddings(model="gemini-embedding-001"))
    retriever = store.as_retriever(search_kwargs={"k": 4})
    prompt = ChatPromptTemplate.from_templete(
         """You are a company policy assistant. Answer ONLY from the context.
If the answer is not present, say: \"I could not find that information in the policy.\"

Context:
{context}

Question:
{question}
"""
    )
    llm = GoogleGenerativeAI(
        model="gemini-2.5-flash", temperature=0)
    chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm)
    return store,chain

@asynccontextmanager
async def lifespan(app : FastAPI):
    global VECTOR_STORE, RAG_CHAIN

    if TEST_MODE:
        print("Running in TEST_MODE - skipping RAG initilization")
        yield
        return


    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("Google api key not configured")

    VECTOR_STORE,RAG_CHAIN =build_rag()
    yield
    
@app.get("/health")
def health():
    return {
        "status":"healthy",
        "rag_ready": RAG_CHAIN is not None,
        "test_mode": TEST_MODE,
    }

