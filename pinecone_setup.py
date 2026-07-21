import os
from dotenv import load_dotenv
import pinecone
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

load_dotenv()

Settings.llm = Ollama(model="llama3.2", request_timeout=120.0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "doc-v1"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=pinecone.ServerlessSpec(cloud="aws", region="us-east-1"),
    )

pinecone_index = pc.Index(index_name)
vs = PineconeVectorStore(pinecone_index=pinecone_index)
sc = StorageContext.from_defaults(vector_store=vs)

index = VectorStoreIndex.from_vector_store(vs)
retriever = index.as_retriever(similarity_top_k=5)
query_engine = RetrieverQueryEngine.from_args(retriever=retriever)

response = query_engine.query("Your question here")
print(response)
