import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.db.repository import stable_id


class Chunker:
    def __init__(self) -> None:
        settings = get_settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n```", "\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def split(self, project_id: str, url: str, version: str, markdown: str) -> list[dict]:
        chunks = self.splitter.split_text(markdown)
        result: list[dict] = []
        for index, content in enumerate(chunks):
            content = content.strip()
            if not content:
                continue
            result.append(
                {
                    "id": stable_id(project_id, url, version, str(index), content[:64], length=64),
                    "content": content,
                    "token_count": self.count_tokens(content),
                    "chunk_index": index,
                }
            )
        return result

    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))
