"""
Multi-format document ingestion architecture for RAG systems.

Provides extensible loaders, preprocessing strategies, and chunking techniques
for handling diverse document types (PDF, DOCX, PPTX, Excel, HTML, Images, Emails, Webpages, Scanned docs).

Core components:
- Loaders: Format-specific document extraction (9 types)
- Preprocessing: Normalization and enrichment strategies (6 strategies)
- Chunking: Format-aware chunking approaches (7 strategies)
- Factory: Main orchestrator for end-to-end pipeline
- Metadata: Data models and chunk management
"""

from .chunking import (
    ChunkingStrategy,
    ChunkingStrategySelector,
    HybridChunker,
    LineageChunker,
    OverlapChunker,
    SemanticChunker,
    SlideChunker,
    StructuralChunker,
    TableChunker,
)
from .factory import DocumentIngestionFactory
from .loaders import (
    DocumentLoader,
    DOCXLoader,
    EmailLoader,
    ExcelLoader,
    FileTypeRegistry,
    HTMLLoader,
    ImageLoader,
    PDFLoader,
    PPTXLoader,
    ScannedDocLoader,
    WebPageLoader,
)
from .metadata import (
    AccessLevel,
    AssetType,
    ChunkMetadata,
    ChunkingStrategyType,
    DocumentChunk,
    DocumentMetadata,
    DocumentSection,
    DocumentType,
    EmbeddedAsset,
    PreprocessedDocument,
    PreprocessingStrategyType,
    RawDocument,
    SectionType,
)
from .metadata.manager import ChunkMetadataManager
from .preprocessing import (
    BoilerplateRemover,
    LanguageDetector,
    MetadataEnricher,
    PreprocessingPipeline,
    PreprocessingStrategy,
    StructurePreserver,
    TableExtractor,
    TextNormalizer,
)

__all__ = [
    # Factory & Orchestration
    "DocumentIngestionFactory",
    # Loaders
    "DocumentLoader",
    "FileTypeRegistry",
    "PDFLoader",
    "DOCXLoader",
    "PPTXLoader",
    "ExcelLoader",
    "HTMLLoader",
    "ImageLoader",
    "EmailLoader",
    "WebPageLoader",
    "ScannedDocLoader",
    # Preprocessing
    "PreprocessingStrategy",
    "PreprocessingPipeline",
    "TextNormalizer",
    "LanguageDetector",
    "MetadataEnricher",
    "StructurePreserver",
    "BoilerplateRemover",
    "TableExtractor",
    # Chunking
    "ChunkingStrategy",
    "ChunkingStrategySelector",
    "OverlapChunker",
    "SemanticChunker",
    "HybridChunker",
    "StructuralChunker",
    "TableChunker",
    "LineageChunker",
    "SlideChunker",
    # Metadata & Models
    "DocumentType",
    "SectionType",
    "AssetType",
    "PreprocessingStrategyType",
    "ChunkingStrategyType",
    "AccessLevel",
    "DocumentMetadata",
    "EmbeddedAsset",
    "DocumentSection",
    "RawDocument",
    "PreprocessedDocument",
    "ChunkMetadata",
    "DocumentChunk",
    "ChunkMetadataManager",
]
