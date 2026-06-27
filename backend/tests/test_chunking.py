from app.rag.chunking import Chunker


def test_chunker_creates_stable_chunks():
    chunker = Chunker()
    chunks = chunker.split("project", "https://example.com", "latest", "hello world\n\n" * 200)
    assert chunks
    assert all("id" in chunk for chunk in chunks)
    assert all(len(chunk["content"]) > 0 for chunk in chunks)
