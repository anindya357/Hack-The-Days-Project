import pytest

from app.services.openai_client import OpenAIService


@pytest.mark.asyncio
async def test_fallback_embeddings_are_deterministic(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    service = OpenAIService()
    first = await service.embed_texts(["agentic documentation"])
    second = await service.embed_texts(["agentic documentation"])
    assert first == second
    assert len(first[0]) == service.settings.fallback_embedding_dimensions
