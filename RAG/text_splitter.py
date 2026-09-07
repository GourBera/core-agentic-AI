"""Text chunking and splitting utilities."""

import logging
import re
from typing import List
from abc import ABC, abstractmethod

from document_loader import Document

logger = logging.getLogger(__name__)


class TextSplitter(ABC):
    """Base class for text splitters."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        """Initialize splitter."""
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be non-negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks."""
        pass

    def create_chunks(self, documents: List[Document]) -> List[Document]:
        """Create chunks from documents."""
        chunked_documents = []
        chunk_id = 0

        for doc in documents:
            text_chunks = self.split_text(doc.content)

            for chunk_text in text_chunks:
                chunk_doc = Document(
                    content=chunk_text,
                    metadata={
                        **doc.metadata,
                        "original_source": doc.source,
                        "chunk_size": len(chunk_text),
                    },
                    source=doc.source,
                    chunk_id=chunk_id,
                )
                chunked_documents.append(chunk_doc)
                chunk_id += 1

        logger.info(f"Created {len(chunked_documents)} chunks from {len(documents)} documents")
        return chunked_documents


class RecursiveCharacterSplitter(TextSplitter):
    """Split text recursively by progressively smaller separators."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        separators: List[str] = None,
    ):
        """Initialize splitter with custom separators."""
        super().__init__(chunk_size, chunk_overlap)
        self.separators = separators or [
            "\n\n",
            "\n",
            " ",
            "",
        ]

    def split_text(self, text: str) -> List[str]:
        """Split text using recursive separators."""
        final_chunks = []
        separator = self.separators[-1]

        for _s in self.separators:
            if _s == "":
                separator = _s
                break
            if _s in text:
                separator = _s
                break

        # Split by separator
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)

        # Merge small splits and ignore empty ones
        good_splits = [s for s in splits if len(s) > self.chunk_overlap]

        # Recursively merge splits if necessary
        if good_splits:
            merged_text = self._merge_splits(good_splits, separator)
            final_chunks.extend(merged_text)
        else:
            if good_splits:
                final_chunks.extend(good_splits)
            else:
                final_chunks = [text]

        return final_chunks

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """Merge splits to maintain chunk size."""
        separator_len = len(separator)
        good_splits = []
        current_doc = []
        total = 0

        for s in splits:
            _len = len(s)
            if total + _len + separator_len > self.chunk_size:
                if current_doc:
                    doc = separator.join(current_doc)
                    if doc:
                        good_splits.append(doc)
                    current_doc = []
                    total = 0
            if _len > self.chunk_size:
                if current_doc:
                    doc = separator.join(current_doc)
                    if doc:
                        good_splits.append(doc)
                    current_doc = []
                good_splits.append(s)
            else:
                current_doc.append(s)
                total += _len + separator_len

        if current_doc:
            doc = separator.join(current_doc)
            if doc:
                good_splits.append(doc)

        # Add overlap to chunks
        if self.chunk_overlap > 0:
            overlapped_chunks = []
            for i, chunk in enumerate(good_splits):
                if i > 0 and self.chunk_overlap > 0:
                    prev_chunk = good_splits[i - 1]
                    overlap_text = prev_chunk[-self.chunk_overlap :]
                    chunk = overlap_text + separator + chunk
                overlapped_chunks.append(chunk)
            return overlapped_chunks

        return good_splits


class SimpleLineSplitter(TextSplitter):
    """Split text by lines."""

    def split_text(self, text: str) -> List[str]:
        """Split text by lines."""
        lines = text.split("\n")
        chunks = []
        current_chunk = []
        current_length = 0

        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            if current_length + line_length > self.chunk_size and current_chunk:
                chunks.append("\n".join(current_chunk))
                # Add overlap
                if self.chunk_overlap > 0:
                    current_chunk = current_chunk[-max(1, self.chunk_overlap // len(line)) :]
                    current_length = sum(len(l) + 1 for l in current_chunk)
                else:
                    current_chunk = []
                    current_length = 0

            current_chunk.append(line)
            current_length += line_length

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks
