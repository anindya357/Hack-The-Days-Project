# DevDocs AI

An AI software engineer for documentation: crawl any docs site, learn it in minutes, answer questions, generate code, compare frameworks, summarize docs, and refresh changed pages.

## Stack

- Frontend: Next.js, React, Tailwind, React Flow
- Backend: FastAPI, LangGraph, LangChain splitters, OpenAI SDK, BeautifulSoup, ChromaDB
- Storage: PostgreSQL metadata, ChromaDB vectors
- Infra: Docker Compose, Nginx, GitHub Actions

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/health
- Nginx: http://localhost:8080
- ChromaDB: http://localhost:8001

The app runs in demo mode without `OPENAI_API_KEY`. Add a key to enable OpenAI embeddings and the Responses API.

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## API

- `POST /api/crawl` starts a crawl and indexing job
- `POST /api/chat` answers questions or summarizes docs
- `POST /api/compare` compares two frameworks or versions
- `POST /api/generate` generates grounded code
- `POST /api/update` recrawls and updates changed pages
- `GET /api/status` returns recent crawl jobs
- `GET /api/docs` lists indexed projects
- `GET /api/stats` returns dashboard metrics

## Demo Flow

1. Paste `https://python.langchain.com` into Crawler.
2. Watch progress move through discovery, crawling, embedding, and storage.
3. Ask `Explain LangGraph.` in Chat.
4. Generate `Create a LangChain RAG pipeline.` in Generate Code.
5. Compare `LangChain` and `LlamaIndex` in Compare.

## Deployment

1. Push to GitHub: `anindya357/Hack-The-Days-Project`.
2. GitHub Actions runs backend tests, frontend typecheck/build, and Docker image builds.
3. Deploy backend, ChromaDB, and PostgreSQL to Railway, Render, Azure Container Apps, GCP, or a VPS with Docker Compose and persistent volumes.
4. Deploy the frontend to Vercel or run it behind Nginx.
5. Put Nginx or your platform proxy in front of the services and configure HTTPS with Let's Encrypt.
