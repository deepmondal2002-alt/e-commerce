import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


def load_documents(path: str) -> list:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"No such file: {file_path}")
    if file_path.suffix.lower() == ".pdf":
        return PyPDFLoader(str(file_path)).load()
    return TextLoader(str(file_path), encoding="utf-8").load()


def build_index(documents: list, embeddings):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    return DocArrayInMemorySearch.from_documents(chunks, embeddings), chunks


def build_clients() -> tuple:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GOOGLE_API_KEY is not set")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key,
    )
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0,
    )
    return embeddings, llm


def answer_question(store, llm, question: str, top_k: int) -> str:
    hits = store.similarity_search(question, k=top_k)
    context = "\n\n".join(
        f"[{i + 1}] (page {doc.metadata.get('page', 'n/a')})\n{doc.page_content}"
        for i, doc in enumerate(hits)
    )
    return llm.invoke(
        "Answer using only the context below.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    ).content


def main() -> None:
    parser = argparse.ArgumentParser(description="production-rag")
    parser.add_argument("path", nargs="?", default="data/sample.txt")
    parser.add_argument("--question", default="Summarise the document.")
    parser.add_argument("--top-k", type=int, default=4)
    args = parser.parse_args()

    embeddings, llm = build_clients()

    documents = load_documents(args.path)
    store, chunks = build_index(documents, embeddings)

    answer = answer_question(store, llm, args.question, args.top_k)

    print(f"loaded {len(documents)} document(s), {len(chunks)} chunk(s)")
    print(f"answer: {answer}")


if __name__ == "__main__":
    main()