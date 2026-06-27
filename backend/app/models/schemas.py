from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl


class CrawlRequest(BaseModel):
    url: HttpUrl
    project_name: str | None = None
    version: str = "latest"
    max_pages: int | None = Field(default=None, ge=1, le=500)


class CrawlResponse(BaseModel):
    job_id: str
    project_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    stage: str
    progress: int = Field(ge=0, le=100)
    message: str
    pages_found: int = 0
    pages_indexed: int = 0
    error: str | None = None
    started_at: datetime
    finished_at: datetime | None = None


class ChatRequest(BaseModel):
    question: str
    project_ids: list[str] | None = None
    version: str | None = None
    mode: Literal["answer", "summarize"] = "answer"


class Citation(BaseModel):
    url: str
    title: str | None = None
    chunk_id: str | None = None
    score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float
    retrieved_chunks: int


class CompareRequest(BaseModel):
    left: str
    right: str
    project_ids: list[str] | None = None
    version: str | None = None


class CompareResponse(BaseModel):
    comparison: str
    citations: list[Citation]
    confidence: float


class GenerateRequest(BaseModel):
    request: str
    project_ids: list[str] | None = None
    version: str | None = None


class UpdateRequest(BaseModel):
    project_id: str | None = None
    url: HttpUrl | None = None
    max_pages: int | None = Field(default=None, ge=1, le=500)


class ProjectSummary(BaseModel):
    id: str
    name: str
    root_url: str
    version: str
    document_count: int = 0
    chunk_count: int = 0
    updated_at: datetime | None = None


class DashboardStats(BaseModel):
    projects: int
    documents: int
    chunks: int
    questions: int
    embeddings: int
    token_usage: int


class ApiHealth(BaseModel):
    status: str
    app: str
    services: dict[str, Any]
