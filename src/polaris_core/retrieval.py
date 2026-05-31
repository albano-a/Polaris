from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from polaris_core.models import Document

TOKEN_PATTERN = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def chunk_text(text: str, max_words: int = 180, overlap: int = 30) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(max_words - overlap, 1)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + max_words]).strip()
        if chunk:
            chunks.append(chunk)
        if start + max_words >= len(words):
            break
    return chunks


@dataclass
class RetrievalResult:
    document_id: str
    document_name: str
    chunk: str
    score: float


@dataclass
class LocalRetriever:
    documents: list[Document] = field(default_factory=list)
    chunk_words: int = 180
    chunk_overlap: int = 30

    @classmethod
    def from_directory(
        cls,
        directory: str | Path,
        patterns: tuple[str, ...] = ("*.txt", "*.md", "*.rst"),
    ) -> "LocalRetriever":
        root = Path(directory)
        if root.is_file():
            return cls.from_path(root)

        documents: list[Document] = []
        if not root.exists():
            return cls(documents=documents)

        for pattern in patterns:
            for path in sorted(root.glob(pattern)):
                if path.is_file():
                    documents.append(read_document(path))
        return cls(documents=documents)

    @classmethod
    def from_path(
        cls,
        path: str | Path,
        patterns: tuple[str, ...] = ("*.txt", "*.md", "*.rst"),
    ) -> "LocalRetriever":
        source = Path(path)
        if source.is_dir():
            return cls.from_directory(source, patterns=patterns)
        if not source.exists() or not source.is_file():
            return cls(documents=[])
        return cls(documents=[read_document(source)])

    def add_document(self, document: Document) -> None:
        self.documents.append(document)

    def search(self, query: str, top_k: int = 6) -> list[RetrievalResult]:
        query_terms = tokenize(query)
        if not query_terms or not self.documents:
            return []

        query_set = set(query_terms)
        candidates: list[tuple[Document, str, list[str]]] = []
        document_frequency: dict[str, int] = {}

        for document in self.documents:
            for chunk in chunk_text(document.text, self.chunk_words, self.chunk_overlap):
                terms = tokenize(chunk)
                if not terms:
                    continue
                term_set = set(terms)
                for term in query_set & term_set:
                    document_frequency[term] = document_frequency.get(term, 0) + 1
                candidates.append((document, chunk, terms))

        if not candidates:
            return []

        scored: list[RetrievalResult] = []
        total_chunks = len(candidates)
        for document, chunk, terms in candidates:
            score = self._score(query_terms, terms, document_frequency, total_chunks)
            if score > 0:
                scored.append(
                    RetrievalResult(
                        document_id=document.id,
                        document_name=document.name,
                        chunk=chunk,
                        score=score,
                    )
                )

        scored.sort(key=lambda result: result.score, reverse=True)
        return scored[:top_k]

    def _score(
        self,
        query_terms: list[str],
        chunk_terms: list[str],
        document_frequency: dict[str, int],
        total_chunks: int,
    ) -> float:
        chunk_counts: dict[str, int] = {}
        for term in chunk_terms:
            chunk_counts[term] = chunk_counts.get(term, 0) + 1

        score = 0.0
        for term in query_terms:
            frequency = chunk_counts.get(term, 0)
            if frequency == 0:
                continue
            df = document_frequency.get(term, 1)
            idf = math.log((1 + total_chunks) / (1 + df)) + 1
            score += frequency * idf
        return score


def read_document(path: Path) -> Document:
    return Document(
        id=str(path.resolve()),
        name=path.name,
        text=path.read_text(encoding="utf-8", errors="replace"),
        metadata={"path": str(path)},
    )
