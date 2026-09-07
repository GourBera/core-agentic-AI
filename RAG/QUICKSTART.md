# RAG Quick Start Guide

## 5-Minute Setup

### 1. Install

```bash
cd RAG
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export OPENAI_API_KEY="sk-..."
# Or on Windows: set OPENAI_API_KEY=sk-...
```

### 3. Create Sample Documents

```bash
mkdir -p data/documents
echo "Transformers are the foundation of modern NLP." > data/documents/sample.txt
```

### 4. Run RAG

```python
from RAG.app import RAGApplication

# Initialize
app = RAGApplication()

# Ingest documents
app.ingest("./data/documents")

# Ask questions
result = app.answer("What are transformers?")
print(result['answer'])
```

## Common Tasks

### Task 1: Ingest from PDF

```python
from RAG.app import RAGApplication

app = RAGApplication()
app.ingest("./data/documents")  # Will read PDFs automatically
```

### Task 2: Customize Embedding Model

```python
from RAG.app import RAGApplication
from RAG.config import RAGConfig, EmbeddingConfig

config = RAGConfig(
    embedding=EmbeddingConfig(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
)
app = RAGApplication(config=config)
```

### Task 3: Use Different LLM

```python
from RAG.config import RAGConfig, LLMConfig

config = RAGConfig(
    llm=LLMConfig(
        provider="anthropic",
        model_name="claude-3-sonnet-20240229"
    )
)
app = RAGApplication(config=config)
```

### Task 4: Retrieval Only (No LLM)

```python
from RAG.app import RAGApplication

app = RAGApplication(use_llm=False)
app.ingest("./data/documents")

# Just retrieve, don't generate
docs = app.pipeline.retrieve("your question", top_k=5)
for doc, score in docs:
    print(f"Score: {score:.2%} - {doc.content[:100]}...")
```

### Task 5: Adjust Retrieval Quality

```python
from RAG.config import RAGConfig

config = RAGConfig(
    top_k=10,              # Get more documents
    similarity_threshold=0.3  # Lower threshold for more results
)
app = RAGApplication(config=config)
```

## Architecture Overview

```
Documents (PDF, TXT, MD)
        ↓
    Load & Parse
        ↓
    Split into Chunks
        ↓
    Generate Embeddings
        ↓
    Store in Vector DB
        ↓
    ←————— Query
        ↓
    Generate Embeddings
        ↓
    Retrieve Similar Docs
        ↓
    Generate Prompt
        ↓
    LLM Generation
        ↓
    Answer
```

## Next Steps

1. **Read full documentation**: See `README.md`
2. **Explore examples**: Run `python example.py`
3. **Deploy**: Follow `DEPLOYMENT.md`
4. **Customize**: Extend with your own components
5. **Monitor**: Set up logging and metrics

## Troubleshooting

**Q: Module import error?**
A: Install all dependencies: `pip install -r requirements.txt`

**Q: Slow performance?**
A: Use GPU or smaller model: `device="cuda"` or `all-MiniLM-L6-v2`

**Q: API key errors?**
A: Check environment: `echo $OPENAI_API_KEY`

**Q: No documents found?**
A: Check path: `ls data/documents/`

## Performance Tips

- Use smaller embeddings for speed: `all-MiniLM-L6-v2`
- Reduce chunk size for faster retrieval
- Enable GPU for embedding generation
- Cache embeddings to avoid recomputation
- Use Pinecone for large datasets

## API Examples

```python
# Initialize
from RAG import RAGApplication
app = RAGApplication()

# Ingest documents
chunks = app.ingest("./data/documents")

# Answer questions
result = app.answer("What is X?")

# Get stats
stats = app.get_pipeline_stats()

# Clear data
app.clear()
```

## File Structure

```
RAG/
├── config.py              # Configuration classes
├── document_loader.py     # Document loading
├── text_splitter.py       # Text chunking
├── embeddings.py          # Embedding models
├── vector_store.py        # Vector store implementations
├── llm.py                 # LLM providers
├── pipeline.py            # Core RAG pipeline
├── app.py                 # Application wrapper
├── example.py             # Usage examples
├── test_rag.py           # Unit tests
├── README.md              # Full documentation
├── DEPLOYMENT.md          # Deployment guide
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── __init__.py           # Package init
```

## Key Concepts

**Embeddings**: Numerical representations of text for similarity search
**Vector Store**: Database for storing and searching embeddings
**Retrieval**: Finding relevant documents for a query
**LLM**: Language model for generating responses
**RAG**: Retrieval-Augmented Generation - retrieve docs first, then generate

## Support

- Check README.md for detailed docs
- See DEPLOYMENT.md for production setup
- Run example.py for usage examples
- Review test_rag.py for test patterns
