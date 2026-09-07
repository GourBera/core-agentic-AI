# 7-Layer Production RAG Architecture

## Overview

This is a production-grade Retrieval-Augmented Generation (RAG) system built with clear separation of concerns across 7 distinct layers.

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER QUERY                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: QUERY PROCESSING                                      │
│  - Normalize query text                                          │
│  - Detect intent (question, command, statement)                 │
│  - Extract named entities                                       │
│  - Expand keywords with synonyms                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3a: EMBEDDINGS                                           │
│  - Sentence Transformers (all-MiniLM-L6-v2)                     │
│  - Generate 384-dim embeddings                                  │
│  - Batch processing with caching                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3b: VECTOR SEARCH (Pinecone)                             │
│  - Semantic search on 384-dim embeddings                        │
│  - Retrieve top-20 candidates                                   │
│  - Cosine similarity metric                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 5: PERMISSION FILTERING                                  │
│  - RBAC/ABAC access control                                     │
│  - Filter by user_id, team_id, access_level                     │
│  - Access levels: public (0) → internal (1) → team (2) → private (3)
│  - Result: ~5-10 documents                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 6: RERANKING                                             │
│  - Cross-encoder reranking (ms-marco-MiniLM-L-12-v2)            │
│  - Semantic relevance scoring                                   │
│  - Return top-5 re-ranked results                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 7: LLM GENERATION (Local Ollama)                         │
│  - Context-aware prompt engineering                             │
│  - Generate response with llama2/mistral                        │
│  - Confidence scoring                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FINAL RESPONSE + SOURCES                        │
└─────────────────────────────────────────────────────────────────┘
```

## Document Ingestion Flow

```
DOCUMENTS (.pdf, .docx, .txt, .md, .pptx)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: DOCUMENT PROCESSING                                   │
│  - Load documents from directory                                │
│  - Normalize & clean text                                       │
│  - Enrich with metadata (user_id, team_id, access_level)       │
│  - Supported formats: PDF, DOCX, TXT, MD, PPTX                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: CHUNKING STRATEGY (Hybrid)                            │
│  - OVERLAP CHUNKING:                                             │
│    • Recursive character splitting                              │
│    • Size: 1000 tokens, Overlap: 200 tokens                    │
│  - SEMANTIC CHUNKING:                                            │
│    • Sentence-aware splitting                                   │
│    • Size: 512 tokens, Threshold: 95th percentile              │
│  - HYBRID (60% semantic, 40% overlap)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3a: EMBEDDINGS                                           │
│  - Generate embeddings for each chunk                           │
│  - Sentence Transformers (384-dim)                              │
│  - Batch processing with caching                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3b: VECTOR STORAGE (Pinecone)                            │
│  - Upsert vectors with metadata                                 │
│  - Cosine similarity index                                      │
│  - Store: chunk content, document_id, chunk_index, user context │
│  - Result: Searchable knowledge base                            │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Document Processing (Layer 1)
- **Supported Formats**: PDF, DOCX, TXT, Markdown, PPTX
- **Normalization**: Text cleaning, whitespace normalization
- **Metadata Enrichment**: User ID, Team ID, Access Level
- **Implementation**: [document_loader.py](document_loader.py)

### 2. Hybrid Chunking (Layer 2)
- **Overlap Chunking**: Traditional recursive character splitting
  - Fixed chunk size with overlapping windows
  - Preserves context across chunk boundaries
- **Semantic Chunking**: AI-aware chunk boundaries
  - Splits on sentence boundaries
  - Respects semantic coherence
- **Hybrid Mode**: Combines both strategies
  - Configurable weighting (default: 60% semantic, 40% overlap)
- **Implementation**: [chunking_strategy.py](chunking_strategy.py)

### 3. Embeddings + Vector Storage (Layer 3)
- **Embedding Model**: Sentence Transformers (all-MiniLM-L6-v2)
  - 384-dimensional embeddings
  - Fast inference on CPU/GPU
  - Normalized embeddings for cosine similarity
- **Vector Database**: Pinecone
  - Serverless vector store
  - Sub-second search latency
  - Metadata filtering support
- **Implementation**: 
  - Embeddings: [embeddings.py](embeddings.py)
  - Storage: [vector_store.py](vector_store.py)

### 4. Query Processing (Layer 4)
- **Text Normalization**: Lowercase, whitespace cleanup
- **Intent Detection**: Identify query type (question, command, statement)
- **Entity Extraction**: Named entity recognition
- **Keyword Expansion**: Augment with synonyms and related terms
- **Implementation**: [query_processor.py](query_processor.py)

### 5. Permission Filtering (Layer 5)
- **RBAC/ABAC**: Role-based and attribute-based access control
- **Metadata Filters**:
  - `user_id`: Document owner
  - `team_id`: Team-level access
  - `access_level`: Hierarchical access levels
- **Access Levels** (hierarchical):
  - `public` (0): Everyone
  - `internal` (1): Organization members
  - `team` (2): Team members only
  - `private` (3): Creator only
- **Implementation**: [access_control.py](access_control.py)

### 6. Reranking (Layer 6)
- **Model**: Cross-Encoder (ms-marco-MiniLM-L-12-v2)
- **Purpose**: Re-score and rank documents by semantic relevance
- **Input**: Top-20 permission-filtered documents
- **Output**: Top-5 re-ranked documents
- **Implementation**: [reranker.py](reranker.py)

### 7. LLM Generation (Layer 7)
- **Model**: Local Ollama (llama2, mistral, etc.)
- **Advantages**:
  - No API costs
  - Data stays local
  - Full control over model
  - Streaming responses
- **Prompt Engineering**: Context-aware prompts with source attribution
- **Confidence Scoring**: Based on context relevance and response quality
- **Implementation**: [llm_client.py](llm_client.py)

## Configuration

All settings are defined in [config.py](config.py):

```python
# Environment Variables Required
PINECONE_API_KEY=your_api_key
PINECONE_ENVIRONMENT=prod
PINECONE_INDEX_NAME=rag-production

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

EMBEDDING_DEVICE=cuda  # or cpu
LOG_LEVEL=INFO
```

## Usage Example

```python
from config import RAGConfig
from pipeline import RAGPipeline
import asyncio

# Initialize
config = RAGConfig()
pipeline = RAGPipeline(config)

# Ingest documents
await pipeline.ingest_documents(
    documents_path="./documents",
    metadata={
        "user_id": "user123",
        "team_id": "team456",
        "access_level": "internal"
    }
)

# Query
response = await pipeline.query(
    query_text="What is machine learning?",
    user_context={
        "user_id": "user123",
        "team_id": "team456",
        "access_level": "internal"
    }
)

# Response includes:
# - query: Original query
# - processed_query: Query after Layer 4 processing
# - pipeline_metrics: Docs retrieved, filtered, ranked
# - response: LLM-generated answer
# - sources: Attribution with metadata
# - confidence: Confidence score
```

## Performance Characteristics

| Layer | Component | Latency | Notes |
|-------|-----------|---------|-------|
| 1 | Document Loading | ~100-500ms per doc | Depends on file size |
| 2 | Chunking | ~10-50ms per doc | Parallel processing |
| 3a | Embedding (batch) | ~5-20ms per doc | GPU accelerated |
| 3b | Vector Search | ~10-50ms | Sub-second Pinecone search |
| 4 | Query Processing | ~1-5ms | Lightweight text processing |
| 5 | Permission Filtering | ~1-10ms | Metadata filtering |
| 6 | Reranking | ~20-100ms | Cross-encoder inference |
| 7 | LLM Generation | 1-10 seconds | Ollama response generation |
| **Total** | **End-to-End Query** | **~1.5-11 seconds** | Dominated by LLM |

## Architecture Benefits

✅ **Modularity**: Each layer is independent and testable
✅ **Scalability**: Easy to scale individual components
✅ **Observability**: Structured logging at each layer
✅ **Security**: Fine-grained access control
✅ **Performance**: Optimized retrieval with reranking
✅ **Privacy**: Local LLM, no external API calls
✅ **Flexibility**: Easy to swap components (embeddings, LLM, etc.)

## File Structure

```
RAG/
├── pipeline.py                 # 7-layer orchestrator
├── config.py                   # Configuration management
│
├── document_loader.py          # Layer 1: Document Processing
├── chunking_strategy.py        # Layer 2: Chunking Strategy
├── embeddings.py               # Layer 3a: Embeddings
├── vector_store.py             # Layer 3b: Vector Storage (Pinecone)
├── query_processor.py          # Layer 4: Query Processing
├── access_control.py           # Layer 5: Permission Filtering
├── reranker.py                 # Layer 6: Reranking
├── llm_client.py               # Layer 7: LLM Generation
│
├── tests/                      # Test suite
├── ARCHITECTURE.md             # This file
└── README.md                   # Quick start guide
```

## Deployment

### Local Development
```bash
# Install dependencies
uv pip install -r requirements.txt

# Set environment variables
export PINECONE_API_KEY=your_key
export OLLAMA_BASE_URL=http://localhost:11434

# Start Ollama
ollama serve

# Run tests
pytest RAG/tests/
```

### Production
- Deploy pipeline as FastAPI service
- Use Kubernetes for orchestration
- Enable structured logging for monitoring
- Set up alerts on Layer 6 & 7 latencies

## Future Enhancements

- [ ] Support for multi-modal embeddings (text + images)
- [ ] Hybrid search (BM25 + dense vectors)
- [ ] Knowledge graph integration
- [ ] Fine-tuned embedding models per domain
- [ ] Advanced RAG techniques (HyDE, Fusion-in-the-loop)
- [ ] Multi-language support
- [ ] Streaming response generation
