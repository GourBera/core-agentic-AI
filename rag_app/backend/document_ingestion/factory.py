"""Main factory orchestrator for document ingestion pipeline."""

import logging
import uuid
from pathlib import Path
from typing import List, Optional, Union

from .chunking import ChunkingStrategySelector, HybridChunker
from .loaders import FileTypeRegistry
from .metadata.manager import ChunkMetadataManager
from .metadata.models import DocumentChunk, PreprocessedDocument, RawDocument
from .preprocessing import PreprocessingPipeline

logger = logging.getLogger(__name__)


class DocumentIngestionFactory:
    """
    Main orchestrator for multi-format document ingestion.
    
    Coordinates all layers of the ingestion pipeline:
    1. Type detection and loading
    2. Preprocessing and normalization
    3. Chunking
    4. Metadata enrichment
    
    Provides extensible hooks for adding new file types and techniques.
    """

    def __init__(
        self,
        file_type_registry: Optional[FileTypeRegistry] = None,
        preprocessing_pipeline: Optional[PreprocessingPipeline] = None,
        chunking_selector: Optional[ChunkingStrategySelector] = None,
        metadata_manager: Optional[ChunkMetadataManager] = None,
    ):
        """
        Initialize ingestion factory.
        
        Args:
            file_type_registry: Registry for loaders (uses singleton if None)
            preprocessing_pipeline: Pipeline for preprocessing strategies
            chunking_selector: Strategy selector for chunking
            metadata_manager: Manager for chunk metadata
        """
        self.file_type_registry = file_type_registry or FileTypeRegistry()
        self.preprocessing_pipeline = preprocessing_pipeline or PreprocessingPipeline()
        self.chunking_selector = chunking_selector or ChunkingStrategySelector()
        self.metadata_manager = metadata_manager or ChunkMetadataManager()
        
        logger.info("DocumentIngestionFactory initialized")

    def ingest(
        self,
        source_path: Union[str, Path],
        document_id: Optional[str] = None,
        access_level: int = 1,
        **kwargs
    ) -> List[DocumentChunk]:
        """
        End-to-end document ingestion pipeline.
        
        Workflow:
        1. Detect document type from file extension
        2. Load document using appropriate loader
        3. Apply preprocessing strategies
        4. Chunk using format-aware strategy
        5. Enrich metadata
        
        Args:
            source_path: Path to document file
            document_id: Optional document identifier (auto-generated if None)
            access_level: Access control level for chunks
            **kwargs: Additional options for loaders/strategies
            
        Returns:
            List of DocumentChunk objects ready for embedding
            
        Raises:
            FileNotFoundError: If source file not found
            ValueError: If document type unsupported or ingestion fails
        """
        # Generate document ID if not provided
        if document_id is None:
            document_id = str(uuid.uuid4())

        logger.info(f"Starting ingestion for: {source_path} (ID: {document_id})")

        # Step 1: Type detection and loading
        source = Path(source_path)
        document_type = self.file_type_registry.get_document_type(source)
        
        if document_type is None:
            raise ValueError(
                f"Unsupported document type: {source.suffix}. "
                f"Supported: {self.file_type_registry.get_supported_extensions()}"
            )

        logger.debug(f"Detected type: {document_type.value}")

        # Get loader and load document
        loader = self.file_type_registry.get_loader(document_type)
        raw_documents = loader.load(source)
        logger.info(f"Loaded {len(raw_documents)} raw documents")

        # Step 2 & 3: Preprocess and chunk
        all_chunks: List[DocumentChunk] = []
        
        for raw_doc in raw_documents:
            # Set document ID
            raw_doc.document_id = document_id

            # Preprocess
            preprocessed_doc = self.preprocessing_pipeline.execute(raw_doc)
            logger.debug(
                f"Applied {len(preprocessed_doc.preprocessing_steps_applied)} "
                f"preprocessing strategies"
            )

            # Select chunking strategy
            strategy = self._select_chunking_strategy(document_type)
            logger.debug(f"Using chunking strategy: {strategy.get_strategy_type().value}")

            # Chunk
            chunks = strategy.chunk(preprocessed_doc)
            logger.info(f"Created {len(chunks)} chunks")

            # Step 5: Enrich metadata and register
            for chunk in chunks:
                chunk.metadata.access_level = access_level
                self.metadata_manager.register_chunk(chunk)
                all_chunks.append(chunk)

        logger.info(
            f"Ingestion complete: {len(all_chunks)} chunks from "
            f"{len(raw_documents)} documents"
        )
        
        return all_chunks

    def ingest_batch(
        self,
        source_paths: List[Union[str, Path]],
        **kwargs
    ) -> List[DocumentChunk]:
        """
        Ingest multiple documents.
        
        Args:
            source_paths: List of document paths
            **kwargs: Additional options passed to ingest()
            
        Returns:
            Combined list of all chunks from all documents
        """
        all_chunks: List[DocumentChunk] = []
        
        for source_path in source_paths:
            try:
                chunks = self.ingest(source_path, **kwargs)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Failed to ingest {source_path}: {e}")
                if kwargs.get("fail_fast", False):
                    raise

        return all_chunks

    def register_loader(
        self,
        document_type,
        loader_class,
        extensions: List[str],
    ) -> None:
        """
        Register a new document loader.
        
        Args:
            document_type: DocumentType enum value
            loader_class: Loader class to register
            extensions: File extensions (e.g., ['.pdf'])
        """
        self.file_type_registry.register(document_type, loader_class, extensions)
        logger.info(f"Registered loader for {document_type.value}")

    def register_preprocessing_strategy(self, strategy) -> None:
        """
        Add preprocessing strategy to pipeline.
        
        Args:
            strategy: PreprocessingStrategy instance
        """
        self.preprocessing_pipeline.add_strategy(strategy)
        logger.info(f"Registered preprocessing: {strategy.__class__.__name__}")

    def register_chunking_strategy(self, document_type, strategy_class) -> None:
        """
        Register chunking strategy for document type.
        
        Args:
            document_type: Document type key
            strategy_class: ChunkingStrategy class
        """
        self.chunking_selector.register(document_type, strategy_class)
        logger.info(f"Registered chunking strategy for {document_type}")

    def _select_chunking_strategy(self, document_type):
        """
        Select appropriate chunking strategy for document type.
        
        Args:
            document_type: DocumentType enum value
            
        Returns:
            ChunkingStrategy instance
        """
        try:
            return self.chunking_selector.select(document_type.value)
        except ValueError:
            logger.warning(
                f"No specific strategy for {document_type.value}, "
                f"using default HybridChunker"
            )
            return HybridChunker()

    def get_ingestion_stats(self) -> dict:
        """
        Get ingestion statistics.
        
        Returns:
            Dictionary with ingestion stats
        """
        return {
            "metadata_manager_stats": self.metadata_manager.get_statistics(),
            "supported_types": [t.value for t in self.file_type_registry.get_supported_types()],
            "supported_extensions": self.file_type_registry.get_supported_extensions(),
            "preprocessing_strategies": len(self.preprocessing_pipeline.strategies),
        }
