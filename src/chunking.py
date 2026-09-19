from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        sentences = re.split(r'(?<=\. )|(?<=\! )|(?<=\? )|(?<=\.\n)', text)
        
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = "".join(sentences[i : i + self.max_sentences_per_chunk])
            chunk = chunk.strip()
            if chunk:
                chunks.append(chunk)
                
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [current_text]
            
        sep = remaining_separators[0]
        next_separators = remaining_separators[1:]
        
        if sep == "":
            parts = list(current_text)
        else:
            parts = current_text.split(sep)
            
        if len(parts) == 1:
            return self._split(current_text, next_separators)
            
        chunks = []
        current_chunk = []
        current_len = 0
        sep_len = len(sep)
        
        for part in parts:
            if len(part) > self.chunk_size:
                if current_chunk:
                    chunks.append(sep.join(current_chunk))
                    current_chunk = []
                    current_len = 0
                
                chunks.extend(self._split(part, next_separators))
            else:
                new_len = current_len + (sep_len if current_len > 0 else 0) + len(part)
                if new_len > self.chunk_size:
                    chunks.append(sep.join(current_chunk))
                    current_chunk = [part]
                    current_len = len(part)
                else:
                    current_chunk.append(part)
                    current_len = new_len
                    
        if current_chunk:
            chunks.append(sep.join(current_chunk))
            
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # TODO: implement cosine similarity formula
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(x * x for x in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return _dot(vec_a, vec_b) / (mag_a * mag_b)


class HeadingChunker:
    """
    Split text by Markdown headings (#).
    Each section starts with the heading. If a section is too long, 
    it falls back to RecursiveChunker but prepends the heading to each chunk.
    """
    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self.recursive = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
            
        parts = re.split(r'(?=\n#+ )', "\n" + text.strip())
        
        chunks = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if len(part) <= self.chunk_size:
                chunks.append(part)
            else:
                lines = part.split("\n", 1)
                heading = ""
                if lines[0].startswith("#"):
                    heading = lines[0] + "\n"
                    content = lines[1] if len(lines) > 1 else ""
                else:
                    content = part
                    
                sub_chunks = self.recursive.chunk(content)
                for sc in sub_chunks:
                    chunks.append(heading + sc.strip() if heading else sc.strip())
                    
        return chunks


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        if not text:
            return {
                "fixed_size": {"count": 0, "avg_length": 0.0, "chunks": []},
                "by_sentences": {"count": 0, "avg_length": 0.0, "chunks": []},
                "recursive": {"count": 0, "avg_length": 0.0, "chunks": []}
            }

        fixed_chunks = FixedSizeChunker(chunk_size=chunk_size).chunk(text)
        sentence_chunks = SentenceChunker().chunk(text)
        recursive_chunks = RecursiveChunker(chunk_size=chunk_size).chunk(text)
        
        def _stats(chunks):
            if not chunks:
                return {"count": 0, "avg_length": 0.0, "chunks": []}
            return {
                "count": len(chunks),
                "avg_length": sum(len(c) for c in chunks) / len(chunks),
                "chunks": chunks
            }
            
        return {
            "fixed_size": _stats(fixed_chunks),
            "by_sentences": _stats(sentence_chunks),
            "recursive": _stats(recursive_chunks)
        }
