"""Table chunking strategy - Table-aware splitting for tabular data."""

from typing import List

from ..metadata.models import ChunkingStrategyType, DocumentChunk, PreprocessedDocument
from .base import ChunkingStrategy


class TableChunker(ChunkingStrategy):
    """
    Chunk documents with table-aware strategy.
    
    Features:
    - Preserves table structure and integrity
    - Chunks per table or by table rows
    - Combines table headers with row data for context
    - Handles merged cells and complex tables
    
    Best for: Excel, HTML tables, CSV data
    """

    def __init__(
        self,
        rows_per_chunk: int = 10,
        include_header: bool = True,
        max_chunk_size: int = 2000,
    ):
        """
        Initialize table chunker.
        
        Args:
            rows_per_chunk: Number of table rows per chunk
            include_header: Whether to include headers in each chunk
            max_chunk_size: Maximum chunk size in characters
        """
        self.rows_per_chunk = rows_per_chunk
        self.include_header = include_header
        self.max_chunk_size = max_chunk_size

    def chunk(self, document: PreprocessedDocument) -> List[DocumentChunk]:
        """
        Split document with table-aware strategy.
        
        Args:
            document: Preprocessed document to chunk
            
        Returns:
            List of table-aware chunks
        """
        pass

    def get_strategy_type(self) -> ChunkingStrategyType:
        """Return ChunkingStrategyType.TABLE."""
        pass

    def _extract_tables(self) -> List[dict]:
        """Extract all tables from document."""
        pass

    def _chunk_large_table(self, table: dict) -> List[str]:
        """Split large table into row-based chunks."""
        pass

    def _format_table_chunk(self, header: list, rows: list) -> str:
        """Format table chunk with headers and context."""
        pass

    def _detect_table_structure(self, table: dict) -> dict:
        """Analyze table structure (headers, merged cells, etc.)."""
        pass

    def _create_table_context(self, table: dict) -> str:
        """Create contextual information for table."""
        pass
