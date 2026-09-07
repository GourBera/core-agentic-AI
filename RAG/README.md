# Production-Grade RAG Pipeline

A comprehensive, production-ready Retrieval-Augmented Generation (RAG) pipeline with modular architecture, multiple backend support, and enterprise-grade features.

## Features

- **Document Ingestion**: Support for TXT, Markdown, and PDF files
- **Text Chunking**: Smart chunking with configurable overlap
- **Embeddings**: Multiple embedding model support (Sentence Transformers, OpenAI)
- **Vector Stores**: Chromadb, Pinecone, and extensible architecture
- **LLM Integration**: Support for OpenAI, Anthropic, HuggingFace, and local models
- **Logging & Monitoring**: Comprehensive logging for production use
- **Caching**: Embedding caching for performance
- **Error Handling**: Robust error handling and validation
- **Configuration Management**: Dataclass-based configuration system
- **Modularity**: Easily swap components (embeddings, vector store, LLM)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   RAG Application                       │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Document   │  │     Text     │  │  Embeddings  │ │
│  │    Loader    │→ │   Splitter   │→ │   Generator  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         ↓                                      ↓        │
│  ┌──────────────────────────────────────────────────┐ │
│  │           Vector Store (Chromadb/Pinecone)      │ │
│  └──────────────────────────────────────────────────┘ │
│         ↑                                      ↑        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Retriever   │  │    Prompt    │  │     LLM      │ │
│  │              │→ │   Generator  │→ │  (OpenAI)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **With uv** (preferred):
```bash
uv pip install -r requirements.txt
```

3. **Optional dependencies**:
```bash
# For OpenAI integration
pip install openai

# For Anthropic integration
pip install anthropic

# For HuggingFace models
pip install transformers torch
```

## Quick Start

### Basic Usage

```python
from RAG import RAGApplication

# Initialize RAG app
rag_app = RAGApplication()

# Ingest documents
rag_app.ingest("./data/documents")

# Answer a question
result = rag_app.answer("What are transformers?")
print(result['answer'])
print(result['sources'])
```

### Custom Configuration

```python
from RAG import RAGApplication, RAGConfig
from RAG.config import EmbeddingConfig, ChunkingConfig

config = RAGConfig(
    embedding=EmbeddingConfig(model_name="all-mpnet-base-v2"),
    chunking=ChunkingConfig(chunk_size=1024, chunk_overlap=128),
    top_k=5,
    similarity_threshold=0.5,
)

rag_app = RAGApplication(config=config)
```

### Retrieval Only (No LLM)

```python
from RAG import RAGPipeline

pipeline = RAGPipeline()
pipeline.ingest_documents("./data/documents")

# Retrieve without generating
results = pipeline.retrieve("Your question here", top_k=5)
for doc, score in results:
    print(f"[Score: {score:.2%}] {doc.content[:100]}...")
```

## Configuration

### RAGConfig

```python
@dataclass
class RAGConfig:
    embedding: EmbeddingConfig       # Embedding model config
    vector_store: VectorStoreConfig  # Vector store config
    chunking: ChunkingConfig         # Text chunking config
    llm: LLMConfig                   # LLM config
    top_k: int = 5                   # Number of documents to retrieve
    similarity_threshold: float = 0.5 # Minimum similarity score
    documents_dir: Path = "./data/documents"
    log_level: str = "INFO"
```

### Embedding Models

- `sentence-transformers/all-MiniLM-L6-v2` (fast, 384 dims)
- `sentence-transformers/all-mpnet-base-v2` (accurate, 768 dims)
- OpenAI `text-embedding-3-small`, `text-embedding-3-large`

### Vector Stores

- **Chromadb** (default, in-memory + persistent)
- **Pinecone** (cloud-based)
- Extensible for Weaviate, Milvus, Qdrant, etc.

### LLMs

- **OpenAI**: GPT-3.5-turbo, GPT-4, etc.
- **Anthropic**: Claude models
- **HuggingFace**: Open-source models
- **Local**: Ollama, LLaMA, Mistral, etc.

## API Reference

### RAGApplication

```python
class RAGApplication:
    def ingest(documents_path: str) -> int
        """Ingest documents, return number of chunks created."""
    
    def answer(query: str, top_k: Optional[int]) -> Dict
        """Answer query with RAG, return answer + sources."""
    
    def get_pipeline_stats() -> Dict
        """Get pipeline statistics."""
    
    def clear()
        """Clear all data from vector store."""
```

### RAGPipeline

```python
class RAGPipeline:
    def ingest_documents(documents_path: str) -> int
        """Ingest documents from directory."""
    
    def retrieve(query: str, top_k: Optional[int]) -> List[Tuple[Document, float]]
        """Retrieve relevant documents."""
    
    def query(query: str, top_k: Optional[int]) -> Dict
        """Execute full RAG pipeline (retrieve + prompt generation)."""
    
    def generate_prompt(query: str, retrieved_docs: List) -> str
        """Generate prompt from query and context."""
```

## Supported Document Formats

- **TXT**: Plain text files
- **Markdown**: .md files
- **PDF**: PDF documents (requires PyPDF2)
- **Extensible**: Add custom loaders by subclassing `DocumentLoader`

## Examples

See `example.py` for complete examples including:

1. Basic RAG pipeline usage
2. Custom configuration
3. Retrieval-only mode
4. Sample document creation

Run examples:
```bash
python example.py
```

## Production Considerations

### Performance

- Use Pinecone for large-scale deployments (>1M documents)
- Cache embeddings to reduce API calls
- Batch process documents during ingestion
- Use smaller embedding models for speed vs. accuracy tradeoff

### Reliability

- Implement retry logic for API calls
- Monitor vector store health
- Log all operations for debugging
- Validate document ingestion success

### Security

- Store API keys in environment variables
- Use managed vector stores (Pinecone) for sensitive data
- Implement access controls on document storage
- Validate and sanitize input

### Scalability

- Horizontally scale LLM inference with load balancers
- Use cloud-based vector stores (Pinecone, Weaviate Cloud)
- Implement async document ingestion
- Monitor embeddings cache size

## Troubleshooting

### Out of Memory

```python
# Use smaller embedding model
config = RAGConfig(
    embedding=EmbeddingConfig(model_name="all-MiniLM-L6-v2")
)
```

### Slow Ingestion

```python
# Reduce chunk size
config = RAGConfig(
    chunking=ChunkingConfig(chunk_size=512, chunk_overlap=50)
)
```

### Poor Retrieval Quality

```python
# Increase top_k and lower threshold
config = RAGConfig(
    top_k=10,
    similarity_threshold=0.3
)
```

## Extending the Pipeline

### Add Custom Embedding Model

```python
from RAG.embeddings import EmbeddingModel

class CustomEmbedding(EmbeddingModel):
    def embed(self, text: str) -> List[float]:
        # Your implementation
        pass
```

### Add Custom Vector Store

```python
from RAG.vector_store import VectorStore

class CustomVectorStore(VectorStore):
    def add_documents(self, documents, embeddings):
        # Your implementation
        pass
```

### Add Custom LLM

```python
from RAG.llm import LLM

class CustomLLM(LLM):
    def generate(self, prompt: str) -> str:
        # Your implementation
        pass
```

## Roadmap

- [ ] Streaming responses
- [ ] Query expansion techniques
- [ ] Hybrid search (BM25 + semantic)
- [ ] Citation tracking
- [ ] Multi-modal support (images, tables)
- [ ] Fine-tuning embeddings
- [ ] GraphRAG support
- [ ] Web UI dashboard

## License

MIT

## Contributing

Contributions welcome! Please submit PRs with tests and documentation.

## Support

For issues and questions:
1. Check existing documentation
2. Review examples
3. Check troubleshooting section
4. Open an issue with details
