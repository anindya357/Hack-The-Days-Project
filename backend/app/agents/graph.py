from datetime import datetime
from typing import TypedDict

try:
    from langgraph.graph import END, START, StateGraph
except Exception:  # pragma: no cover - keeps app importable if langgraph is absent during static checks
    END = START = None
    StateGraph = None

from sqlalchemy.orm import Session

from app.core.prompts import ANSWER_PROMPT, CODE_PROMPT, COMPARE_PROMPT, DOC_ASSISTANT_SYSTEM, SUMMARY_PROMPT
from app.crawler.service import DocumentationCrawler
from app.db.repository import MetadataRepository
from app.models.schemas import Citation
from app.rag.chunking import Chunker
from app.rag.vectorstore import RetrievedChunk, VectorStore
from app.services.jobs import job_manager
from app.services.openai_client import OpenAIService


class AgentState(TypedDict, total=False):
    task: str
    question: str
    needs_crawl: bool
    needs_code: bool
    answer: str


class DevDocsSupervisor:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = MetadataRepository(db)
        self.openai = OpenAIService()
        self.vectorstore = VectorStore(self.openai)
        self.crawler = DocumentationCrawler()
        self.chunker = Chunker()
        self.graph = self._build_graph()

    async def crawl_project(
        self,
        job_id: str,
        root_url: str,
        project_name: str | None,
        version: str,
        max_pages: int | None,
    ) -> None:
        project = self.repo.upsert_project(root_url, project_name or self._name_from_url(root_url), version)

        async def progress(stage: str, progress_value: int, message: str) -> None:
            job_manager.update(job_id, status="running", stage=stage, progress=progress_value, message=message)

        try:
            pages = await self.crawler.crawl(root_url, max_pages=max_pages, on_progress=progress)
            job_manager.update(job_id, pages_found=len(pages), stage="embedding", progress=55, message="Embedding documentation chunks...")

            indexed = 0
            for page_index, page in enumerate(pages):
                if not self.repo.document_changed(project.id, page.url, version, page.content_hash):
                    continue

                chunks = self.chunker.split(project.id, page.url, version, page.markdown)
                metadatas = [
                    {
                        "project_id": project.id,
                        "document_url": page.url,
                        "url": page.url,
                        "title": page.title,
                        "version": version,
                        "chunk_index": chunk["chunk_index"],
                    }
                    for chunk in chunks
                ]
                await self.vectorstore.upsert_chunks(chunks, metadatas)
                self.repo.replace_document(
                    project_id=project.id,
                    url=page.url,
                    title=page.title,
                    version=version,
                    content_hash=page.content_hash,
                    token_count=self.chunker.count_tokens(page.markdown),
                    chunks=chunks,
                )
                indexed += 1
                progress_value = 55 + int(((page_index + 1) / max(len(pages), 1)) * 40)
                job_manager.update(job_id, progress=progress_value, pages_indexed=indexed, message=f"Indexed {indexed} changed pages")

            job_manager.update(
                job_id,
                status="completed",
                stage="completed",
                progress=100,
                message="Completed",
                pages_indexed=indexed,
                finished_at=datetime.utcnow(),
            )
        except Exception as exc:
            job_manager.update(
                job_id,
                status="failed",
                stage="failed",
                progress=100,
                message="Crawl failed",
                error=str(exc),
                finished_at=datetime.utcnow(),
            )

    async def answer(self, question: str, project_ids: list[str] | None, version: str | None, mode: str = "answer") -> tuple[str, list[Citation], float, int]:
        chunks = await self.vectorstore.search(question, project_ids=project_ids, version=version)
        context = self._format_context(chunks)
        prompt_template = SUMMARY_PROMPT if mode == "summarize" else ANSWER_PROMPT
        prompt = prompt_template.format(question=question, request=question, context=context)
        answer = await self.openai.generate(DOC_ASSISTANT_SYSTEM, prompt)
        citations = self._citations(chunks)
        confidence = self._confidence(chunks)
        self.repo.record_question(question, mode)
        return answer, citations, confidence, len(chunks)

    async def compare(self, left: str, right: str, project_ids: list[str] | None, version: str | None) -> tuple[str, list[Citation], float]:
        left_chunks = await self.vectorstore.search(left, project_ids=project_ids, version=version)
        right_chunks = await self.vectorstore.search(right, project_ids=project_ids, version=version)
        prompt = COMPARE_PROMPT.format(
            left=left,
            right=right,
            left_context=self._format_context(left_chunks),
            right_context=self._format_context(right_chunks),
        )
        answer = await self.openai.generate(DOC_ASSISTANT_SYSTEM, prompt)
        citations = self._citations(left_chunks + right_chunks)
        confidence = self._confidence(left_chunks + right_chunks)
        self.repo.record_question(f"Compare {left} vs {right}", "compare")
        return answer, citations, confidence

    async def generate_code(self, request: str, project_ids: list[str] | None, version: str | None) -> tuple[str, list[Citation], float, int]:
        chunks = await self.vectorstore.search(request, project_ids=project_ids, version=version)
        prompt = CODE_PROMPT.format(request=request, context=self._format_context(chunks))
        answer = await self.openai.generate(DOC_ASSISTANT_SYSTEM, prompt)
        citations = self._citations(chunks)
        confidence = self._confidence(chunks)
        self.repo.record_question(request, "generate")
        return answer, citations, confidence, len(chunks)

    def _build_graph(self):
        if StateGraph is None:
            return None

        def planner(state: AgentState) -> AgentState:
            question = state.get("question", "").lower()
            return {
                **state,
                "needs_crawl": question.startswith("crawl ") or "index " in question,
                "needs_code": any(term in question for term in ["code", "generate", "example"]),
            }

        def route_after_plan(state: AgentState) -> str:
            return "crawler" if state.get("needs_crawl") else "retriever"

        graph = StateGraph(AgentState)
        graph.add_node("planner", planner)
        graph.add_node("crawler", lambda state: state)
        graph.add_node("retriever", lambda state: state)
        graph.add_node("answer_generator", lambda state: state)
        graph.add_node("code_agent", lambda state: state)
        graph.add_edge(START, "planner")
        graph.add_conditional_edges("planner", route_after_plan, {"crawler": "crawler", "retriever": "retriever"})
        graph.add_edge("crawler", "retriever")
        graph.add_edge("retriever", "answer_generator")
        graph.add_conditional_edges("answer_generator", lambda state: "code_agent" if state.get("needs_code") else END)
        graph.add_edge("code_agent", END)
        return graph.compile()

    def _format_context(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No retrieved context."
        blocks = []
        for index, chunk in enumerate(chunks, start=1):
            title = chunk.metadata.get("title") or "Untitled"
            url = chunk.metadata.get("url") or chunk.metadata.get("document_url") or "unknown"
            blocks.append(f"[{index}] {title}\nURL: {url}\nScore: {chunk.score:.3f}\n{chunk.content}")
        return "\n\n---\n\n".join(blocks)

    def _citations(self, chunks: list[RetrievedChunk]) -> list[Citation]:
        seen: set[str] = set()
        citations: list[Citation] = []
        for chunk in chunks:
            url = chunk.metadata.get("url") or chunk.metadata.get("document_url")
            if not url or url in seen:
                continue
            seen.add(url)
            citations.append(Citation(url=url, title=chunk.metadata.get("title"), chunk_id=chunk.id, score=chunk.score))
        return citations

    def _confidence(self, chunks: list[RetrievedChunk]) -> float:
        if not chunks:
            return 0.0
        average = sum(chunk.score for chunk in chunks) / len(chunks)
        coverage = min(len(chunks) / 5, 1.0)
        return round(max(0.0, min(0.98, average * 0.75 + coverage * 0.25)), 2)

    def _name_from_url(self, url: str) -> str:
        return url.replace("https://", "").replace("http://", "").split("/")[0]
