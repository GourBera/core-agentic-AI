"""Unit tests for RAG pipeline components."""

import pytest
from pathlib import Path
from RAG.config import RAGConfig
from RAG.document_loader import Document, TextFileLoader
from RAG.text_splitter import RecursiveCharacterSplitter
from RAG.embeddings import SentenceTransformerEmbedding


class TestDocumentLoading:
    """Test document loading functionality."""

    def test_text_file_loader(self, tmp_path):
        """Test loading a text file."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_content = "This is a test document.\nWith multiple lines."
        test_file.write_text(test_content)

        # Load document
        loader = TextFileLoader()
        docs = loader.load(str(test_file))

        assert len(docs) == 1
        assert docs[0].content == test_content
        assert docs[0].source == str(test_file)

    def test_text_file_not_found(self):
        """Test loading non-existent file."""
        loader = TextFileLoader()
        with pytest.raises(FileNotFoundError):
            loader.load("./nonexistent_file.txt")


class TestTextSplitting:
    """Test text splitting functionality."""

    def test_recursive_character_splitter(self):
        """Test recursive character splitter."""
        text = "This is a test. " * 100  # Create long text
        splitter = RecursiveCharacterSplitter(chunk_size=100, chunk_overlap=10)

        chunks = splitter.split_text(text)

        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 150  # Allow some tolerance

    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        text = "Word " * 100  # Create text with repeated words
        splitter = RecursiveCharacterSplitter(chunk_size=50, chunk_overlap=10)

        chunks = splitter.split_text(text)

        # Verify overlap exists between consecutive chunks
        if len(chunks) > 1:
            # Last 10 chars of first chunk should appear in second chunk
            first_chunk_ending = chunks[0][-10:]
            assert first_chunk_ending in chunks[1]

    def test_document_chunking(self):
        """Test chunking documents."""
        docs = [
            Document(
                content="Test content. " * 50,
                metadata={"source": "test.txt"},
                source="test.txt",
            )
        ]

        splitter = RecursiveCharacterSplitter(chunk_size=100, chunk_overlap=10)
        chunked_docs = splitter.create_chunks(docs)

        assert len(chunked_docs) > 1
        for chunk in chunked_docs:
            assert chunk.source == "test.txt"
            assert "original_source" in chunk.metadata


class TestEmbeddings:
    """Test embedding functionality."""

    def test_sentence_transformer_initialization(self):
        """Test initializing sentence transformer."""
        embedding = SentenceTransformerEmbedding(
            model_name="all-MiniLM-L6-v2",
            device="cpu",
        )

        assert embedding.model_name == "all-MiniLM-L6-v2"
        assert embedding.get_embedding_dimension() > 0

    def test_embedding_generation(self):
        """Test generating embeddings."""
        embedding = SentenceTransformerEmbedding(device="cpu")
        text = "This is a test sentence."

        result = embedding.embed(text)

        assert isinstance(result, list)
        assert len(result) == embedding.get_embedding_dimension()
        assert all(isinstance(x, float) for x in result)

    def test_batch_embedding(self):
        """Test batch embedding generation."""
        embedding = SentenceTransformerEmbedding(device="cpu")
        texts = [
            "This is the first test.",
            "This is the second test.",
            "This is the third test.",
        ]

        results = embedding.embed_batch(texts)

        assert len(results) == len(texts)
        for result in results:
            assert len(result) == embedding.get_embedding_dimension()


class TestRAGConfig:
    """Test configuration management."""

    def test_default_config(self, tmp_path):
        """Test default configuration."""
        config = RAGConfig(
            documents_dir=tmp_path / "docs",
            cache_dir=tmp_path / "cache",
        )

        assert config.top_k == 5
        assert config.similarity_threshold == 0.5
        assert config.chunking.chunk_size == 1000

    def test_config_directory_creation(self, tmp_path):
        """Test that config creates necessary directories."""
        docs_dir = tmp_path / "docs"
        cache_dir = tmp_path / "cache"

        config = RAGConfig(
            documents_dir=docs_dir,
            cache_dir=cache_dir,
        )

        assert docs_dir.exists()
        assert cache_dir.exists()

    def test_invalid_chunk_size(self):
        """Test validation of chunk sizes."""
        with pytest.raises(ValueError):
            RecursiveCharacterSplitter(chunk_size=0, chunk_overlap=10)

    def test_invalid_chunk_overlap(self):
        """Test validation of chunk overlap."""
        with pytest.raises(ValueError):
            RecursiveCharacterSplitter(chunk_size=100, chunk_overlap=100)


@pytest.fixture
def tmp_path(tmp_path):
    """Provide temporary directory."""
    return tmp_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
