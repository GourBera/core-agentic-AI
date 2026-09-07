# RAG Pipeline Deployment Guide

## Local Development Setup

### Prerequisites

- Python 3.10+
- pip or uv
- Git

### Installation Steps

1. **Clone the repository**:
```bash
git clone https://github.com/GourBera/core-agentic-AI.git
cd core-agentic-AI/RAG
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
# Using pip
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt
```

4. **Setup environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Create sample data directory**:
```bash
mkdir -p data/documents
mkdir -p data/vectorstore
mkdir -p data/cache
```

### Running Examples

```bash
python example.py
```

## Production Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY RAG/ ./RAG

ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

CMD ["python", "-m", "RAG.app"]
```

Build and run:
```bash
docker build -t rag-pipeline .
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY rag-pipeline
```

### Kubernetes Deployment

Create `deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-pipeline
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-pipeline
  template:
    metadata:
      labels:
        app: rag-pipeline
    spec:
      containers:
      - name: rag-pipeline
        image: rag-pipeline:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        ports:
        - containerPort: 8000
```

Deploy:
```bash
kubectl apply -f deployment.yaml
```

### Azure Deployment

1. **Create App Service**:
```bash
az appservice plan create \
  --name rag-plan \
  --resource-group my-rg \
  --sku B2 \
  --is-linux

az webapp create \
  --name rag-pipeline \
  --resource-group my-rg \
  --plan rag-plan \
  --runtime "PYTHON|3.11"
```

2. **Configure application settings**:
```bash
az webapp config appsettings set \
  --name rag-pipeline \
  --resource-group my-rg \
  --settings OPENAI_API_KEY=$OPENAI_API_KEY LOG_LEVEL=INFO
```

3. **Deploy code**:
```bash
cd /Users/gourbera/Core AI
git remote add azure <azure-repo-url>
git push azure main
```

## API Server Deployment

### FastAPI Integration

Create `server.py`:
```python
from fastapi import FastAPI
from pydantic import BaseModel
from RAG.app import RAGApplication
import logging

app = FastAPI(title="RAG API")
rag_app = RAGApplication()
logger = logging.getLogger(__name__)

class Query(BaseModel):
    text: str
    top_k: int = 5

@app.post("/ingest")
async def ingest_documents(path: str):
    """Ingest documents from path."""
    try:
        chunks = rag_app.ingest(path)
        return {"status": "success", "chunks": chunks}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/query")
async def query(query: Query):
    """Execute RAG query."""
    try:
        result = rag_app.answer(query.text, top_k=query.top_k)
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/stats")
async def get_stats():
    """Get pipeline statistics."""
    return rag_app.get_pipeline_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run server:
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## Performance Tuning

### Vector Store Optimization

```python
# Use batch indexing for large datasets
config.vector_store.batch_size = 256

# Use GPU if available
config.embedding.model_kwargs["device"] = "cuda"
```

### Embedding Caching

```python
from RAG.embeddings import EmbeddingCache

cache = EmbeddingCache(cache_size=50000)
# Cache reduces API calls and improves performance
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

# Process documents in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(rag_app.ingest, doc) 
               for doc in documents]
```

## Monitoring & Logging

### Structured Logging

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
```

### Metrics Collection

```python
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@measure_time
def expensive_operation():
    # Your code here
    pass
```

## Security Best Practices

### API Key Management

```python
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")
```

### Input Validation

```python
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    text: str
    top_k: int = 5
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v
    
    @validator('top_k')
    def top_k_valid(cls, v):
        if v < 1 or v > 100:
            raise ValueError('top_k must be between 1 and 100')
        return v
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/query")
@limiter.limit("10/minute")
async def query(request: QueryRequest):
    # Your code here
    pass
```

## Backup & Recovery

### Vector Store Backup

```python
import shutil
from pathlib import Path

def backup_vectorstore(backup_dir: str):
    """Backup vector store."""
    vectorstore_dir = Path("./data/vectorstore")
    backup_path = Path(backup_dir) / "vectorstore_backup"
    shutil.copytree(vectorstore_dir, backup_path)
    logger.info(f"Backup created at {backup_path}")

# Schedule daily backups
import schedule

schedule.every().day.at("02:00").do(backup_vectorstore, "./backups")
```

### Database Recovery

```python
def restore_vectorstore(backup_dir: str):
    """Restore vector store from backup."""
    vectorstore_dir = Path("./data/vectorstore")
    backup_path = Path(backup_dir) / "vectorstore_backup"
    
    vectorstore_dir.rmdir()
    shutil.copytree(backup_path, vectorstore_dir)
    logger.info("Vector store restored from backup")
```

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'openai'"**
   - Solution: `pip install openai`

2. **"CUDA out of memory"**
   - Solution: Use CPU or smaller model
   - Config: `device="cpu"` or use `all-MiniLM-L6-v2`

3. **"Slow retrieval speed"**
   - Solution: Use smaller chunks or reduce top_k
   - Add embedding caching

4. **"Poor answer quality"**
   - Solution: Increase top_k, lower similarity_threshold
   - Use better embedding model

## Performance Benchmarks

Typical performance metrics (with GPU):

| Operation | Time | Notes |
|-----------|------|-------|
| Document ingestion | 50 docs/s | With chunking |
| Query retrieval | 100ms | Top-5 retrieval |
| LLM generation | 1-2s | Depends on model |
| Batch embedding | 1000 texts/s | GPU accelerated |

## Support

For deployment issues:
1. Check logs: `tail -f app.log`
2. Verify environment variables: `env | grep RAG`
3. Test components individually
4. Check resource limits (memory, CPU)
