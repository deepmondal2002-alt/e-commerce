import os
from pathlib import Path

from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

_DIR = Path(__file__).resolve().parent


def _get_vectorstore():
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=384,
    )
    return Chroma(
        collection_name="rag_base",
        embedding_function=embeddings,
        persist_directory=str(_DIR / "chroma_db"),
    )


@tool
def vector_store_search(query: str) -> str:
    """Search the vector store for documents relevant to the query."""
    vectorstore = _get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant documents found."
    return "\n\n".join([doc.page_content for doc in docs])
