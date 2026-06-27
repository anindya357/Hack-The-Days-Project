import math
from dataclasses import dataclass
from typing import Any

import chromadb

from app.core.config import get_settings
from app.services.openai_client import OpenAIService


@dataclass
class RetrievedChunk:
    id: str
    content: str
    metadata: dict[str, Any]
    score: float
    embedding: list[float] | None = None


class VectorStore:
    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.settings = get_settings()
        self.openai = openai_service or OpenAIService()
        if self.settings.chroma_is_remote:
            self.client = chromadb.HttpClient(host=self.settings.chroma_host, port=self.settings.chroma_port)
        else:
            self.client = chromadb.PersistentClient(path=self.settings.chroma_persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )

    async def upsert_chunks(self, chunks: list[dict], metadatas: list[dict]) -> None:
        if not chunks:
            return
        documents = [chunk["content"] for chunk in chunks]
        ids = [chunk["id"] for chunk in chunks]
        embeddings = await self.openai.embed_texts(documents)
        self.collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

    async def search(
        self,
        query: str,
        project_ids: list[str] | None = None,
        version: str | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        top_k = top_k or self.settings.retrieval_top_k
        query_embedding = (await self.openai.embed_texts([query]))[0]
        where = self._where(project_ids, version)
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=max(top_k, self.settings.retrieval_pool_k),
            where=where,
            include=["documents", "metadatas", "distances", "embeddings"],
        )
        candidates = self._parse_results(result)
        return self._mmr(query_embedding, candidates, top_k=top_k)

    def delete_project(self, project_id: str) -> None:
        self.collection.delete(where={"project_id": project_id})

    def _where(self, project_ids: list[str] | None, version: str | None) -> dict | None:
        clauses = []
        if project_ids:
            if len(project_ids) == 1:
                clauses.append({"project_id": project_ids[0]})
            else:
                clauses.append({"project_id": {"$in": project_ids}})
        if version:
            clauses.append({"version": version})
        if not clauses:
            return None
        if len(clauses) == 1:
            return clauses[0]
        return {"$and": clauses}

    def _parse_results(self, result: dict) -> list[RetrievedChunk]:
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        embeddings = result.get("embeddings", [[]])[0]
        chunks: list[RetrievedChunk] = []
        for idx, chunk_id in enumerate(ids):
            distance = distances[idx] if idx < len(distances) else 1.0
            chunks.append(
                RetrievedChunk(
                    id=chunk_id,
                    content=documents[idx],
                    metadata=metadatas[idx] or {},
                    score=max(0.0, 1.0 - float(distance)),
                    embedding=embeddings[idx] if idx < len(embeddings) else None,
                )
            )
        return chunks

    def _mmr(self, query_embedding: list[float], candidates: list[RetrievedChunk], top_k: int, lambda_mult: float = 0.65) -> list[RetrievedChunk]:
        selected: list[RetrievedChunk] = []
        remaining = candidates[:]
        while remaining and len(selected) < top_k:
            best = max(
                remaining,
                key=lambda item: lambda_mult * self._cosine(query_embedding, item.embedding)
                - (1 - lambda_mult) * max([self._cosine(item.embedding, chosen.embedding) for chosen in selected] or [0.0]),
            )
            selected.append(best)
            remaining.remove(best)
        return selected

    def _cosine(self, left: list[float] | None, right: list[float] | None) -> float:
        if left is None or right is None:
            return 0.0
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
        right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
        return dot / (left_norm * right_norm)
