import hashlib
import uuid
from collections import Counter
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document, Project, Question
from app.models.schemas import DashboardStats, ProjectSummary


def stable_id(*parts: str, length: int = 48) -> str:
    digest = hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()
    return digest[:length]


class MetadataRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_project(self, root_url: str, name: str, version: str) -> Project:
        project_id = stable_id(root_url, version, length=32)
        project = self.db.get(Project, project_id)
        if project is None:
            project = Project(id=project_id, root_url=root_url, name=name, version=version)
            self.db.add(project)
        else:
            project.name = name
            project.root_url = root_url
            project.version = version
            project.updated_at = datetime.utcnow()
        self.db.commit()
        return project

    def document_changed(self, project_id: str, url: str, version: str, content_hash: str) -> bool:
        document_id = stable_id(project_id, url, version, length=48)
        document = self.db.get(Document, document_id)
        return document is None or document.content_hash != content_hash

    def replace_document(
        self,
        project_id: str,
        url: str,
        title: str | None,
        version: str,
        content_hash: str,
        token_count: int,
        chunks: list[dict],
    ) -> Document:
        document_id = stable_id(project_id, url, version, length=48)
        document = self.db.get(Document, document_id)
        if document is None:
            document = Document(
                id=document_id,
                project_id=project_id,
                url=url,
                title=title,
                version=version,
                content_hash=content_hash,
                token_count=token_count,
            )
            self.db.add(document)
        else:
            document.title = title
            document.content_hash = content_hash
            document.token_count = token_count
            document.updated_at = datetime.utcnow()
            self.db.query(Chunk).filter(Chunk.document_id == document_id).delete()

        for chunk in chunks:
            self.db.add(
                Chunk(
                    id=chunk["id"],
                    document_id=document_id,
                    project_id=project_id,
                    url=url,
                    title=title,
                    content=chunk["content"],
                    version=version,
                    token_count=chunk.get("token_count", 0),
                )
            )
        self.db.commit()
        return document

    def record_question(self, question: str, mode: str, token_usage: int = 0) -> None:
        self.db.add(Question(id=uuid.uuid4().hex, question=question, mode=mode, token_usage=token_usage))
        self.db.commit()

    def list_projects(self) -> list[ProjectSummary]:
        projects = self.db.execute(select(Project)).scalars().all()
        summaries: list[ProjectSummary] = []
        for project in projects:
            doc_count = self.db.scalar(select(func.count(Document.id)).where(Document.project_id == project.id)) or 0
            chunk_count = self.db.scalar(select(func.count(Chunk.id)).where(Chunk.project_id == project.id)) or 0
            summaries.append(
                ProjectSummary(
                    id=project.id,
                    name=project.name,
                    root_url=project.root_url,
                    version=project.version,
                    document_count=doc_count,
                    chunk_count=chunk_count,
                    updated_at=project.updated_at,
                )
            )
        return summaries

    def stats(self) -> DashboardStats:
        projects = self.db.scalar(select(func.count(Project.id))) or 0
        documents = self.db.scalar(select(func.count(Document.id))) or 0
        chunks = self.db.scalar(select(func.count(Chunk.id))) or 0
        questions = self.db.scalar(select(func.count(Question.id))) or 0
        token_usage = self.db.scalar(select(func.coalesce(func.sum(Question.token_usage), 0))) or 0
        return DashboardStats(
            projects=projects,
            documents=documents,
            chunks=chunks,
            questions=questions,
            embeddings=chunks,
            token_usage=token_usage,
        )

    def project_url(self, project_id: str) -> str | None:
        project = self.db.get(Project, project_id)
        return project.root_url if project else None

    def common_versions(self) -> Counter[str]:
        return Counter(self.db.execute(select(Project.version)).scalars().all())
