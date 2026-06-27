import asyncio
import hashlib
import math
import random
from collections.abc import Sequence

from openai import OpenAI

from app.core.config import get_settings


class OpenAIService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key) if self.settings.has_openai_key else None

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        if self.client is None:
            return [self._fallback_embedding(text) for text in texts]

        def _embed() -> list[list[float]]:
            response = self.client.embeddings.create(model=self.settings.embedding_model, input=list(texts))
            return [item.embedding for item in response.data]

        return await asyncio.to_thread(_embed)

    async def generate(self, system: str, prompt: str) -> str:
        if self.client is None:
            return self._fallback_answer(prompt)

        def _generate() -> str:
            response = self.client.responses.create(
                model=self.settings.openai_model,
                input=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
            return getattr(response, "output_text", "") or "I don't know."

        return await asyncio.to_thread(_generate)

    def _fallback_embedding(self, text: str) -> list[float]:
        dimensions = self.settings.fallback_embedding_dimensions
        vector = [0.0] * dimensions
        words = text.lower().split()
        for word in words:
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def _fallback_answer(self, prompt: str) -> str:
        seed = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8]
        random.seed(seed)
        excerpt = prompt[:1400].strip()
        return (
            "Demo mode: OPENAI_API_KEY is not configured, so this answer is generated from the "
            "retrieved context without calling OpenAI.\n\n"
            f"Relevant context excerpt:\n\n{excerpt}\n\n"
            "Configure OPENAI_API_KEY to enable the Responses API answer generator."
        )
