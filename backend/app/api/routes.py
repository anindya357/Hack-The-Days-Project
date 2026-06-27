from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from app.core.config import get_settings
from app.db.repository import MetadataRepository
from app.db.session import SessionLocal, get_db
from app.models.schemas import (
    ApiHealth,
    ChatRequest,
    ChatResponse,
    CompareRequest,
    CompareResponse,
    CrawlRequest,
    CrawlResponse,
    DashboardStats,
    GenerateRequest,
    JobStatus,
    ProjectSummary,
    UpdateRequest,
)
from app.services.jobs import job_manager

router = APIRouter()


async def run_crawl_job(job_id: str, root_url: str, project_name: str | None, version: str, max_pages: int | None) -> None:
    from app.agents.graph import DevDocsSupervisor

    db = SessionLocal()
    try:
        supervisor = DevDocsSupervisor(db)
        await supervisor.crawl_project(job_id, root_url, project_name, version, max_pages)
    finally:
        db.close()


@router.get("/health", response_model=ApiHealth)
def health() -> ApiHealth:
    settings = get_settings()
    return ApiHealth(
        status="ok",
        app=settings.app_name,
        services={
            "openai": "configured" if settings.has_openai_key else "demo-mode",
            "chroma": f"{settings.chroma_host}:{settings.chroma_port}" if settings.chroma_is_remote else settings.chroma_persist_dir,
        },
    )


@router.post("/crawl", response_model=CrawlResponse)
def crawl(payload: CrawlRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> CrawlResponse:
    from app.agents.graph import DevDocsSupervisor

    supervisor = DevDocsSupervisor(db)
    root_url = str(payload.url)
    host = urlparse(root_url).netloc
    project = supervisor.repo.upsert_project(root_url, payload.project_name or host, payload.version)
    job = job_manager.create("Crawler queued")
    background_tasks.add_task(
        run_crawl_job,
        job.job_id,
        root_url,
        payload.project_name,
        payload.version,
        payload.max_pages,
    )
    return CrawlResponse(job_id=job.job_id, project_id=project.id, status=job.status, message=job.message)


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    from app.agents.graph import DevDocsSupervisor

    supervisor = DevDocsSupervisor(db)
    answer, citations, confidence, retrieved = await supervisor.answer(
        payload.question,
        project_ids=payload.project_ids,
        version=payload.version,
        mode=payload.mode,
    )
    return ChatResponse(answer=answer, citations=citations, confidence=confidence, retrieved_chunks=retrieved)


@router.post("/compare", response_model=CompareResponse)
async def compare(payload: CompareRequest, db: Session = Depends(get_db)) -> CompareResponse:
    from app.agents.graph import DevDocsSupervisor

    supervisor = DevDocsSupervisor(db)
    comparison, citations, confidence = await supervisor.compare(payload.left, payload.right, payload.project_ids, payload.version)
    return CompareResponse(comparison=comparison, citations=citations, confidence=confidence)


@router.post("/generate", response_model=ChatResponse)
async def generate(payload: GenerateRequest, db: Session = Depends(get_db)) -> ChatResponse:
    from app.agents.graph import DevDocsSupervisor

    supervisor = DevDocsSupervisor(db)
    answer, citations, confidence, retrieved = await supervisor.generate_code(payload.request, payload.project_ids, payload.version)
    return ChatResponse(answer=answer, citations=citations, confidence=confidence, retrieved_chunks=retrieved)


@router.post("/update", response_model=CrawlResponse)
def update(payload: UpdateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> CrawlResponse:
    from app.agents.graph import DevDocsSupervisor

    repo = MetadataRepository(db)
    url = str(payload.url) if payload.url else (repo.project_url(payload.project_id) if payload.project_id else None)
    if not url:
        raise HTTPException(status_code=400, detail="Provide either project_id or url")
    supervisor = DevDocsSupervisor(db)
    project = supervisor.repo.upsert_project(url, url.split("//")[-1].split("/")[0], "latest")
    job = job_manager.create("Update queued")
    background_tasks.add_task(run_crawl_job, job.job_id, url, project.name, project.version, payload.max_pages)
    return CrawlResponse(job_id=job.job_id, project_id=project.id, status=job.status, message=job.message)


@router.get("/status", response_model=list[JobStatus])
def status() -> list[JobStatus]:
    return job_manager.latest()


@router.get("/status/{job_id}", response_model=JobStatus)
def status_by_id(job_id: str) -> JobStatus:
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/docs", response_model=list[ProjectSummary])
def docs(db: Session = Depends(get_db)) -> list[ProjectSummary]:
    return MetadataRepository(db).list_projects()


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db)) -> DashboardStats:
    return MetadataRepository(db).stats()
