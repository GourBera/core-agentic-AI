"""Document loading and processing utilities."""

import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a document or chunk."""
    content: str
    metadata: Dict[str, Any]
    source: str = ""
    chunk_id: int = 0


class DocumentLoader(ABC):
    """Base class for document loaders."""

    @abstractmethod
    def load(self, source: str) -> List[Document]:
        """Load documents from source."""
        pass


class TextFileLoader(DocumentLoader):
    """Load documents from text files."""

    def load(self, source: str) -> List[Document]:
        """Load text file."""
        try:
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {source}")

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return [
                Document(
                    content=content,
                    metadata={"file_path": str(path), "file_size": path.stat().st_size},
                    source=str(path),
                )
            ]
        except Exception as e:
            logger.error(f"Error loading text file {source}: {e}")
            raise


class PDFLoader(DocumentLoader):
    """Load documents from PDF files."""

    def load(self, source: str) -> List[Document]:
        """Load PDF file."""
        try:
            import PyPDF2

            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {source}")

            documents = []
            with open(path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    documents.append(
                        Document(
                            content=text,
                            metadata={
                                "file_path": str(path),
                                "page": page_num + 1,
                                "total_pages": len(pdf_reader.pages),
                            },
                            source=str(path),
                        )
                    )
            return documents
        except ImportError:
            logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            raise
        except Exception as e:
            logger.error(f"Error loading PDF {source}: {e}")
            raise


class DirectoryLoader(DocumentLoader):
    """Load documents from a directory."""

    def __init__(self, file_extensions: List[str] = None):
        """Initialize with supported file extensions."""
        self.file_extensions = file_extensions or [".txt", ".md", ".pdf"]
        self.loaders = {
            ".txt": TextFileLoader(),
            ".md": TextFileLoader(),
            ".pdf": PDFLoader(),
        }

    def load(self, source: str) -> List[Document]:
        """Load all documents from directory."""
        documents = []
        directory = Path(source)

        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {source}")

        for ext in self.file_extensions:
            for file_path in directory.glob(f"*{ext}"):
                try:
                    loader = self.loaders.get(ext)
                    if loader:
                        docs = loader.load(str(file_path))
                        documents.extend(docs)
                        logger.info(f"Loaded {len(docs)} documents from {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {e}")

        logger.info(f"Total documents loaded: {len(documents)}")
        return documents
