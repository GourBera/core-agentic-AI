"""Data models and enums for document ingestion pipeline."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DocumentType(str, Enum):
    """Supported document types for ingestion."""
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    HTML = "html"
    IMAGE = "image"
    EMAIL = "email"
    WEBPAGE = "webpage"
    SCANNED_DOC = "scanned_doc"


class SectionType(str, Enum):
    """Types of document sections."""
    SLIDE = "slide"
    SHEET = "sheet"
    PAGE = "page"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    HEADING = "heading"
    LIST_ITEM = "list_item"
    EMAIL_MESSAGE = "email_message"
    EMAIL_ATTACHMENT = "email_attachment"
    TEXT_BLOCK = "text_block"


class AssetType(str, Enum):
    """Types of embedded assets."""
    IMAGE = "image"
    ATTACHMENT = "attachment"
    TABLE = "table"
    CHART = "chart"
    DIAGRAM = "diagram"
    FORMULA = "formula"


class PreprocessingStrategyType(str, Enum):
    """Available preprocessing strategies."""
    TEXT_NORMALIZER = "text_normalizer"
    LANGUAGE_DETECTOR = "language_detector"
    METADATA_ENRICHER = "metadata_enricher"
    STRUCTURE_PRESERVER = "structure_preserver"
    BOILERPLATE_REMOVER = "boilerplate_remover"
    TABLE_EXTRACTOR = "table_extractor"


class ChunkingStrategyType(str, Enum):
    """Available chunking strategies."""
    OVERLAP = "overlap"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    STRUCTURAL = "structural"
    TABLE = "table"
    LINEAGE = "lineage"
    SLIDE = "slide"


class AccessLevel(int, Enum):
    """Access control levels for chunks."""
    PUBLIC = 0
    INTERNAL = 1
    TEAM = 2
    PRIVATE = 3


@dataclass
class DocumentMetadata:
    """Metadata for raw documents."""
    document_id: str
    file_name: str
    source_path: str
    file_size: int
    mime_type: str
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    author: Optional[str] = None
    language: Optional[str] = None
    encoding: str = "utf-8"
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddedAsset:
    """Represents embedded content (images, attachments, etc.)."""
    asset_id: str
    asset_type: AssetType
    content: bytes | str
    mime_type: str
    file_name: Optional[str] = None
    size: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentSection:
    """Represents a structured section within a document."""
    section_id: str
    section_type: SectionType
    title: Optional[str] = None
    content: str = ""
    index: int = 0
    level: int = 0  # Nesting level (0 = top-level)
    parent_id: Optional[str] = None
    nested_sections: List["DocumentSection"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedded_assets: List[EmbeddedAsset] = field(default_factory=list)


@dataclass
class RawDocument:
    """Raw extracted content before preprocessing."""
    document_id: str
    document_type: DocumentType
    raw_content: str
    sections: List[DocumentSection] = field(default_factory=list)
    embedded_assets: List[EmbeddedAsset] = field(default_factory=list)
    metadata: DocumentMetadata = None
    source_path: str = ""
    extraction_timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = DocumentMetadata(
                document_id=self.document_id,
                file_name="",
                source_path=self.source_path,
                file_size=len(self.raw_content.encode('utf-8')),
                mime_type="text/plain"
            )


@dataclass
class PreprocessedDocument:
    """Document after preprocessing and normalization."""
    document_id: str
    document_type: DocumentType
    processed_content: str
    sections: List[DocumentSection]
    embedded_assets: List[EmbeddedAsset]
    metadata: DocumentMetadata
    source_document: RawDocument
    preprocessing_steps_applied: List[PreprocessingStrategyType] = field(default_factory=list)
    processing_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChunkMetadata:
    """Metadata for individual chunks."""
    document_type: DocumentType
    file_name: str
    source_path: str
    language: str
    created_date: Optional[datetime] = None
    author: Optional[str] = None
    page_or_section_num: Optional[int] = None
    has_embedded_assets: bool = False
    confidence_score: Optional[float] = None  # For OCR/extraction confidence
    access_level: AccessLevel = AccessLevel.INTERNAL
    # Tracking information
    chunk_strategy: ChunkingStrategyType = ChunkingStrategyType.HYBRID
    source_section_id: Optional[str] = None
    embedded_asset_refs: List[str] = field(default_factory=list)
    custom_attrs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentChunk:
    """Represents a chunk of a document ready for embedding."""
    chunk_id: str
    content: str
    document_id: str
    chunk_index: int
    strategy_type: ChunkingStrategyType
    metadata: ChunkMetadata
    embedded_references: List[str] = field(default_factory=list)
    creation_timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary for serialization."""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "strategy_type": self.strategy_type.value,
            "metadata": {
                "document_type": self.metadata.document_type.value,
                "file_name": self.metadata.file_name,
                "source_path": self.metadata.source_path,
                "language": self.metadata.language,
                "created_date": self.metadata.created_date.isoformat() if self.metadata.created_date else None,
                "author": self.metadata.author,
                "page_or_section_num": self.metadata.page_or_section_num,
                "has_embedded_assets": self.metadata.has_embedded_assets,
                "confidence_score": self.metadata.confidence_score,
                "access_level": self.metadata.access_level.value,
                "chunk_strategy": self.metadata.chunk_strategy.value,
                "source_section_id": self.metadata.source_section_id,
                "embedded_asset_refs": self.metadata.embedded_asset_refs,
                "custom_attrs": self.metadata.custom_attrs,
            },
            "embedded_references": self.embedded_references,
            "creation_timestamp": self.creation_timestamp.isoformat(),
        }
