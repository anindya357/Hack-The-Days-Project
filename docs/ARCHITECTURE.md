# DevDocs AI Architecture

DevDocs AI is a full-stack agentic documentation assistant.

```text
User
  |
Next.js Frontend
  |
FastAPI Backend
  |
LangGraph Supervisor Agent
  |-- Crawler Agent
  |-- RAG Agent
  |-- Search Agent
  |-- Code Agent
  |
OpenAI Responses API
  |
OpenAI text-embedding-3-large
  |
ChromaDB + PostgreSQL
```

## Agent Flow

```text
START
  |
Planner
  |
Need Crawl?
  |
Crawler Agent
  |
Embedding Agent
  |
Store
  |
Retriever
  |
Answer Generator
  |
Need Code?
  |
Code Agent
  |
END
```

## RAG Pipeline

```text
Website -> Crawler -> HTML -> Cleaner -> Markdown -> Chunking -> Embedding -> ChromaDB -> Retriever -> LLM -> Answer
```

Defaults:

- Chunk size: `800`
- Chunk overlap: `150`
- Embedding model: `text-embedding-3-large`
- Retrieval: top `5`, with MMR selection from a larger candidate pool
