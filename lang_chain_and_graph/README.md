# LangChain + LangGraph + Ollama

A local development environment using LangChain, LangGraph, and Ollama for building AI applications.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Modern Python package manager
- [Ollama](https://ollama.ai) - Local LLM runtime

## Setup

### 1. Initialize the environment with uv

```bash
cd /Users/gourbera/Core\ AI/lang_chain_and_graph

# Create and activate the virtual environment
uv venv

# Activate the environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

### 2. Install dependencies

```bash
uv pip install -e .

# For development tools (optional)
uv pip install -e ".[dev]"
```

### 3. Set up Ollama locally

Make sure Ollama is running on your local machine:

```bash
ollama serve
```

In another terminal, pull a model:

```bash
ollama pull llama2      # or another model like mistral, neural-chat, etc.
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```bash
cat > .env << 'EOF'
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
EOF
```

## Usage

### Basic LLM Chat

```python
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama2", base_url="http://localhost:11434")
response = llm.invoke("What is LangChain?")
print(response)
```

### With LangGraph (Agentic workflows)

```python
from langgraph.graph import StateGraph
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama2")
# Build your agentic graph here
```

## Project Structure

- `basic1.py` - Getting started example
- `pyproject.toml` - Project configuration with uv
- `.env` - Environment variables (create locally, don't commit)

## Available Ollama Models

Popular open-source models available via Ollama:
- `llama2` - Meta's Llama 2
- `mistral` - Mistral 7B
- `neural-chat` - Intel's Neural Chat
- `dolphin-mixtral` - Dolphin fine-tuned Mixtral
- `orca-mini` - Lightweight option

See https://ollama.ai/library for more models.

## Common Commands

```bash
# List installed models
ollama list

# Run a model directly (for testing)
ollama run llama2

# Check Ollama status
curl http://localhost:11434/api/tags
```

## Troubleshooting

- **Connection refused**: Ensure Ollama is running (`ollama serve`)
- **Model not found**: Pull the model with `ollama pull <model-name>`
- **Out of memory**: Try a smaller model like `orca-mini` or increase system resources

## References

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Ollama Model Library](https://ollama.ai/library)
