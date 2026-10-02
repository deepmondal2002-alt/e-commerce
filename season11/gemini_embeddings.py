import os

from google import genai
from google.genai import types
from langchain_core.embeddings import Embeddings


class GeminiEmbeddings(Embeddings):
    def __init__(
        self,
        model: str = "models/gemini-embedding-2",
        api_key: str | None = None,
        output_dimensionality: int | None = None,
        task_type: str | None = None,
    ):
        self.client = genai.Client(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        self.model = model
        self.output_dimensionality = output_dimensionality
        self.task_type = task_type

    def _config(self, task_type: str | None = None) -> types.EmbedContentConfig | None:
        resolved = task_type or self.task_type
        if resolved is None and self.output_dimensionality is None:
            return None
        return types.EmbedContentConfig(
            task_type=resolved,
            output_dimensionality=self.output_dimensionality,
        )

    def _embed(self, texts: list[str], task_type: str | None = None) -> list[list[float]]:
        all_embeddings = []
        batch_size = 100
        config = self._config(task_type)
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            # Replace empty strings with a single space to avoid 400 errors
            batch_texts = [t if t.strip() else " " for t in batch_texts]
            contents = [types.Content(parts=[types.Part(text=t)]) for t in batch_texts]
            result = self.client.models.embed_content(
                model=self.model,
                contents=contents,
                config=config,
            )
            all_embeddings.extend([list(e.values) for e in result.embeddings])
        return all_embeddings

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, task_type="RETRIEVAL_DOCUMENT")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], task_type="RETRIEVAL_QUERY")[0]
