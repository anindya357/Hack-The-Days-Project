import asyncio
import hashlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
try:
    from markdownify import markdownify as to_markdown
except ImportError:  # pragma: no cover - requirements include markdownify; fallback keeps dev imports friendly
    def to_markdown(html: str, **_: object) -> str:
        return BeautifulSoup(html, "html.parser").get_text("\n")

from app.core.config import get_settings

ProgressCallback = Callable[[str, int, str], Awaitable[None] | None]


@dataclass
class CrawledPage:
    url: str
    title: str
    markdown: str
    content_hash: str


class DocumentationCrawler:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def crawl(
        self,
        root_url: str,
        max_pages: int | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> list[CrawledPage]:
        max_pages = max_pages or self.settings.crawl_max_pages
        root = self._normalize(root_url)
        root_host = urlparse(root).netloc
        queue: list[str] = [root]
        seen: set[str] = set()
        pages: list[CrawledPage] = []

        await self._progress(on_progress, "discover", 5, "Discovering pages...")

        async with httpx.AsyncClient(
            timeout=self.settings.crawl_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "DevDocsAI/1.0 documentation crawler"},
        ) as client:
            while queue and len(pages) < max_pages:
                url = queue.pop(0)
                if url in seen:
                    continue
                seen.add(url)

                try:
                    response = await client.get(url)
                    content_type = response.headers.get("content-type", "")
                    if response.status_code >= 400 or "text/html" not in content_type:
                        continue
                except httpx.HTTPError:
                    continue

                page = self._clean_page(str(response.url), response.text)
                if page.markdown.strip():
                    pages.append(page)

                for link in self._extract_links(str(response.url), response.text, root_host):
                    if link not in seen and link not in queue and len(seen) + len(queue) < max_pages * 3:
                        queue.append(link)

                progress = min(45, 5 + int((len(pages) / max_pages) * 40))
                await self._progress(on_progress, "crawl", progress, f"{len(pages)} pages found")
                await asyncio.sleep(0)

        await self._progress(on_progress, "crawl", 50, f"{len(pages)} pages crawled")
        return pages

    def _clean_page(self, url: str, html: str) -> CrawledPage:
        soup = BeautifulSoup(html, "html.parser")
        for selector in [
            "script",
            "style",
            "noscript",
            "nav",
            "footer",
            "header",
            "aside",
            "[aria-hidden='true']",
            ".sidebar",
            ".toc",
            ".table-of-contents",
            ".breadcrumb",
        ]:
            for node in soup.select(selector):
                node.decompose()

        title = (soup.title.string.strip() if soup.title and soup.title.string else url).strip()
        main = soup.find("main") or soup.find("article") or soup.body or soup

        for code in main.find_all("code"):
            if code.string:
                code.string = code.string.replace("\xa0", " ")

        markdown = to_markdown(str(main), heading_style="ATX", bullets="-")
        markdown = "\n".join(line.rstrip() for line in markdown.splitlines())
        markdown = self._collapse_blank_lines(markdown)
        content_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        return CrawledPage(url=self._normalize(url), title=title, markdown=markdown, content_hash=content_hash)

    def _extract_links(self, base_url: str, html: str, root_host: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: list[str] = []
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            absolute = self._normalize(urljoin(base_url, href))
            parsed = urlparse(absolute)
            if parsed.netloc != root_host:
                continue
            if any(parsed.path.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".zip"]):
                continue
            links.append(absolute)
        return links

    def _normalize(self, url: str) -> str:
        clean, _ = urldefrag(url)
        parsed = urlparse(clean)
        path = parsed.path.rstrip("/") or "/"
        return parsed._replace(path=path, query=parsed.query.rstrip("&")).geturl()

    def _collapse_blank_lines(self, text: str) -> str:
        lines = []
        blank = False
        for line in text.splitlines():
            is_blank = not line.strip()
            if is_blank and blank:
                continue
            lines.append(line)
            blank = is_blank
        return "\n".join(lines).strip()

    async def _progress(self, callback: ProgressCallback | None, stage: str, progress: int, message: str) -> None:
        if callback is None:
            return
        result = callback(stage, progress, message)
        if result is not None:
            await result
