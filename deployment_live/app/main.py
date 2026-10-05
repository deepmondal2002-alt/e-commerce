import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

load_dotenv()

POLICY_PATH = Path(__file__).resolve().parent.parent / "data" / "company_policy.md"

VECTOR_STORE = None
RAG_CHAIN = None

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag():
    docs = TextLoader(str(POLICY_PATH), encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=700, chunk_overlap=120
    ).split_documents(docs)
    store = FAISS.from_documents(
        chunks, GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    )
    retriever = store.as_retriever(search_kwargs={"k": 4})
    prompt = ChatPromptTemplate.from_template(
        """You are a company policy assistant. Answer ONLY from the context.
If the answer is not present, say: "I could not find that information in the policy."

Context:
{context}

Question:
{question}
"""
    )
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
    )
    return store, chain


@asynccontextmanager
async def lifespan(app: FastAPI):
    global VECTOR_STORE, RAG_CHAIN

    if TEST_MODE:
        print("Running in TEST_MODE - skipping RAG initialization")
        yield
        return

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("Google api key not configured")

    VECTOR_STORE, RAG_CHAIN = build_rag()
    yield


app = FastAPI(title="Company Policy RAG", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "rag_ready": RAG_CHAIN is not None,
        "test_mode": TEST_MODE,
    }


@app.post("/ask")
def ask(request: AskRequest):
    if RAG_CHAIN is None:
        raise HTTPException(status_code=503, detail="RAG pipeline is not ready")
    answer = RAG_CHAIN.invoke(request.question)
    return {"question": request.question, "answer": getattr(answer, "content", answer)}