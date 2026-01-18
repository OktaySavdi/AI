# RAG with Memvid + Ollama 🧠

Retrieval-Augmented Generation (RAG) implementation using **Memvid** for knowledge storage and **self-hosted Ollama** models for inference.

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAG PIPELINE                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐          │
│  │  Documents   │───▶│     Memvid       │───▶│   .mv2 File      │          │
│  │  (PDF, TXT)  │    │   (Indexing)     │    │ (Single File DB) │          │
│  └──────────────┘    └──────────────────┘    └────────┬─────────┘          │
│                                                        │                    │
│                                                        ▼                    │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐          │
│  │    Query     │───▶│  Memvid Search   │───▶│  Retrieved Docs  │          │
│  │   (User)     │    │ (Semantic+Lexical)│   │   (Context)      │          │
│  └──────────────┘    └──────────────────┘    └────────┬─────────┘          │
│                                                        │                    │
│                                                        ▼                    │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐          │
│  │   Answer     │◀───│   Ollama LLM     │◀───│  Context + Query │          │
│  │  (Response)  │    │ (qwen/deepseek)  │    │   (Prompt)       │          │
│  └──────────────┘    └──────────────────┘    └──────────────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 What is Memvid?

**Memvid** is a single-file memory system for AI that packages:
- Your documents
- Embeddings (vector representations)
- Search indices (semantic + lexical)
- Metadata

All into a **single `.mv2` file** - no external database needed!

### Why Memvid over ChromaDB/Pinecone?

| Feature | Memvid | ChromaDB | Pinecone |
|---------|--------|----------|----------|
| **Setup** | Single file | Local server | Cloud service |
| **Portability** | Copy one file | Export/import | API only |
| **Dependencies** | Minimal | Python + SQLite | Internet required |
| **Cost** | Free | Free | $$$ |
| **Offline** | ✅ Yes | ✅ Yes | ❌ No |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Ollama running at `http://20.10.192.136:11434`
- Node.js 18+ (for memvid-cli)

### Installation

```bash
cd /Users/Documents/Scripts/AI/RAG

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Or install manually
pip install memvid-sdk requests python-dotenv
```

### Install Memvid CLI (Optional)

```bash
# Via npm
npm install -g memvid-cli

# Or via Docker
docker pull memvid/cli
```

---

## 📁 Project Structure

```
RAG/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env                         # Configuration (Ollama URL, model)
├── rag_example.py              # Main RAG implementation (library)
├── ingest_documents.py         # Document ingestion CLI tool
├── query_rag.py                # Interactive query CLI tool
├── knowledge/                   # Source documents to index
│   ├── kubernetes/
│   │   ├── pods.md
│   │   ├── deployments.md
│   │   └── services.md
│   └── terraform/
│       ├── basics.md
│       └── azure.md
└── memories/                    # Generated .mv2 files
    └── infrastructure.mv2
```

---

## 📖 Files Reference

### `rag_example.py` - Core RAG Library

**Purpose**: Main RAG implementation containing all classes for document retrieval and LLM interaction.

**Classes**:
| Class | Description |
|-------|-------------|
| `RAGConfig` | Configuration dataclass for Ollama URL, model, memory file |
| `OllamaClient` | HTTP client for Ollama API (generate, embed) |
| `MemvidMemory` | Wrapper for Memvid operations (create, add, search) |
| `InfrastructureRAG` | Main RAG orchestrator combining search + LLM |

**Key Update**: The SDK uses `mem.put(text=content, title=..., uri=..., tags=...)` with keyword arguments, and `mem.find(query, k=top_k)` returns a dict with a `hits` key containing results.

**Usage as Library**:
```python
from rag_example import InfrastructureRAG, RAGConfig

# Initialize with default config (.env)
rag = InfrastructureRAG()

# Or with custom config
config = RAGConfig(
    ollama_url="http://20.10.192.136:11434",
    model="qwen2.5-coder:32b",
    memory_file="./memories/infrastructure.mv2",
    top_k=5
)
rag = InfrastructureRAG(config=config)

# Ask a question (retrieves context + generates answer)
answer = rag.ask("How do I create a Kubernetes deployment?")
print(answer)

# Only retrieve relevant documents (no LLM)
docs = rag.retrieve("kubernetes pod")
for doc in docs:
    print(f"- {doc['content'][:100]}...")

# Interactive chat mode
rag.chat()  # Starts REPL loop
```

**Run as Script**:
```bash
# Start interactive chat
python rag_example.py

# With custom memory file
python rag_example.py --memory ./memories/k8s.mv2

# With different model
python rag_example.py --model deepseek-coder-v2:16b
```

---

### `ingest_documents.py` - Document Ingestion Tool

**Purpose**: Reads documents (MD, TXT, PDF, DOCX), chunks them, and stores in Memvid memory file.

**Classes**:
| Class | Description |
|-------|-------------|
| `Document` | Dataclass for document content + metadata |
| `DocumentLoader` | Loads files from disk (supports multiple formats) |
| `TextChunker` | Splits documents into overlapping chunks |
| `MemvidIngester` | Creates/updates Memvid memory with chunks |

**CLI Arguments**:
| Argument | Default | Description |
|----------|---------|-------------|
| `--input` | `./knowledge` | Input folder or file path |
| `--output` | `./memories/infrastructure.mv2` | Output memory file |
| `--chunk-size` | `500` | Characters per chunk |
| `--overlap` | `100` | Overlap between chunks |
| `--extensions` | `.md,.txt,.pdf,.docx` | File types to process |

**Usage Examples**:
```bash
# Ingest default knowledge folder
python ingest_documents.py

# Ingest specific folder
python ingest_documents.py --input ./docs/runbooks --output ./memories/runbooks.mv2

# Ingest single file
python ingest_documents.py --input ./docs/kubernetes-guide.pdf

# Custom chunk settings (larger chunks for code)
python ingest_documents.py --chunk-size 1000 --overlap 200

# Only markdown files
python ingest_documents.py --extensions ".md"
```

**Usage as Library**:
```python
from ingest_documents import DocumentLoader, TextChunker, MemvidIngester

# Load documents
loader = DocumentLoader(extensions=[".md", ".txt"])
docs = loader.load_folder("./knowledge")

# Chunk documents
chunker = TextChunker(chunk_size=500, overlap=100)
chunks = chunker.chunk_documents(docs)

# Ingest into Memvid
ingester = MemvidIngester("./memories/my-memory.mv2")
count = ingester.ingest(chunks)

print(f"Ingested {count} chunks")
```

---

### `query_rag.py` - Interactive Query Tool

**Purpose**: CLI tool for querying the RAG system interactively or with single queries.

**CLI Arguments**:
| Argument | Default | Description |
|----------|---------|-------------|
| `--memory` | `./memories/infrastructure.mv2` | Memory file to query |
| `--model` | `qwen2.5-coder:32b` | Ollama model to use |
| `--query` | (none) | Single query (skips interactive mode) |
| `--top-k` | `5` | Number of documents to retrieve |
| `--no-llm` | `false` | Only retrieve docs, no LLM generation |

**Usage Examples**:
```bash
# Interactive mode (REPL)
python query_rag.py
> How do I create a Kubernetes deployment?
> What is a Terraform module?
> exit

# Single query
python query_rag.py --query "How do I scale pods?"

# Query different memory file
python query_rag.py --memory ./memories/runbooks.mv2 --query "Database backup procedure"

# Use different model
python query_rag.py --model deepseek-coder-v2:16b --query "Explain Ansible roles"

# Only retrieve (no LLM generation) - useful for debugging
python query_rag.py --no-llm --query "kubernetes"

# More context (retrieve 10 docs instead of 5)
python query_rag.py --top-k 10 --query "terraform azure"
```

**Interactive Commands**:
```
> help          Show available commands
> /model X      Switch to model X
> /memory X     Switch to memory file X
> /topk N       Set top-k to N
> /debug        Toggle debug mode (show retrieved docs)
> exit          Quit interactive mode
```

---

### Knowledge Files (Sample Data)

| File | Description |
|------|-------------|
| `knowledge/kubernetes/pods.md` | Kubernetes Pods reference |
| `knowledge/kubernetes/deployments.md` | Kubernetes Deployments guide |
| `knowledge/kubernetes/services.md` | Kubernetes Services types |
| `knowledge/terraform/basics.md` | Terraform fundamentals |
| `knowledge/terraform/azure.md` | Terraform for Azure examples |

**Add Your Own**:
```bash
# Add your documentation
cp ~/docs/my-runbook.md ./knowledge/
cp -r ~/docs/ansible/ ./knowledge/ansible/

# Re-ingest
python ingest_documents.py
```

---

## 🔧 Configuration

Create `.env` file:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://20.10.192.136:11434
OLLAMA_MODEL=qwen2.5-coder:32b

# Alternative models
# OLLAMA_MODEL=deepseek-coder-v2:16b
# OLLAMA_MODEL=k8s-assistant

# Memvid Configuration
MEMVID_MEMORY_FILE=./memories/infrastructure.mv2

# RAG Settings
RAG_TOP_K=5
RAG_SNIPPET_CHARS=500
```

---

## 💡 Usage Examples

### 1. Ingest Documents

```bash
# Ingest all markdown files from knowledge folder
python ingest_documents.py --input ./knowledge --output ./memories/infrastructure.mv2

# Ingest specific file
python ingest_documents.py --input ./docs/kubernetes-guide.pdf --output ./memories/k8s.mv2
```

### 2. Query with RAG

```bash
# Interactive mode
python query_rag.py

# Single query
python query_rag.py --query "How do I create a Kubernetes deployment?"

# With specific memory file
python query_rag.py --memory ./memories/infrastructure.mv2 --query "Explain Terraform modules"
```

### 3. Full RAG Example

```python
from rag_example import InfrastructureRAG

# Initialize RAG system
rag = InfrastructureRAG(
    memory_file="./memories/infrastructure.mv2",
    ollama_url="http://20.10.192.136:11434",
    model="qwen2.5-coder:32b"
)

# Query
response = rag.ask("How do I scale a Kubernetes deployment to 5 replicas?")
print(response)
```

---

## 🐳 Using Memvid CLI with Docker

```bash
# Create a new memory
docker run --rm -v $(pwd):/data memvid/cli create infrastructure.mv2

# Add documents
docker run --rm -v $(pwd):/data memvid/cli put infrastructure.mv2 --input ./knowledge/

# Search
docker run --rm -v $(pwd):/data memvid/cli find infrastructure.mv2 --query "kubernetes deployment"

# Stats
docker run --rm -v $(pwd):/data memvid/cli stats infrastructure.mv2
```

---

## 📊 How RAG Works

### Step 1: Document Ingestion
```
Documents → Chunking → Embedding → Memvid Index → .mv2 File
```

### Step 2: Query Processing
```
User Query → Embedding → Semantic Search → Top-K Results
```

### Step 3: Answer Generation
```
Context (Retrieved Docs) + Query → LLM Prompt → Generated Answer
```

### RAG Prompt Template

```
You are an Infrastructure Specialist assistant. Answer the question based ONLY on the following context.
If the context doesn't contain relevant information, say "I don't have information about that."

Context:
{retrieved_documents}

Question: {user_query}

Answer:
```

---

## 🎯 Use Cases

### 1. Kubernetes Knowledge Base
- Index K8s documentation, runbooks, troubleshooting guides
- Query: "How do I debug CrashLoopBackOff?"

### 2. Terraform Module Library
- Index your Terraform modules and examples
- Query: "Show me how to create an Azure VM with Terraform"

### 3. Ansible Playbook Assistant
- Index playbooks and roles
- Query: "How do I configure NTP with Ansible?"

### 4. Incident Runbooks
- Index past incident reports and resolutions
- Query: "What was the fix for the database connection timeout?"

---

## 🔗 Integration with Infrastructure Agent

You can integrate this RAG system with your existing Infrastructure Specialist Agent:

```python
# In infrastructure_specialist.py
from rag_example import InfrastructureRAG

class InfrastructureSpecialist:
    def __init__(self):
        # Initialize RAG for knowledge retrieval
        self.rag = InfrastructureRAG(
            memory_file="./memories/infrastructure.mv2"
        )
    
    def execute_task(self, task: str):
        # First, retrieve relevant context
        context = self.rag.retrieve(task)
        
        # Include context in LLM prompt
        enhanced_prompt = f"""
        Relevant knowledge:
        {context}
        
        Task: {task}
        """
        
        # Execute with enhanced context
        return self._call_llm(enhanced_prompt)
```

---

## 📈 Performance Tips

1. **Chunk Size**: Optimal chunk size is 500-1000 characters
2. **Overlap**: Use 100-200 character overlap between chunks
3. **Top-K**: Start with 5, increase if answers lack detail
4. **Model Selection**:
   - `qwen2.5-coder:32b` - Best for code/IaC questions
   - `deepseek-coder-v2:16b` - Faster, good for general queries

---

## 🛠️ Troubleshooting

### Memvid SDK Issues
```bash
# Install Python SDK (required)
pip install memvid-sdk

# Verify installation
python3 -c "import memvid_sdk; print('SDK installed')"
```

### Memvid CLI not found
```bash
# Check installation
which memvid
npm list -g memvid-cli

# Use Docker instead
alias memvid='docker run --rm -v $(pwd):/data memvid/cli'
```

### Ollama connection refused
```bash
# Check Ollama is running
curl http://20.10.192.136:11434/api/tags

# Check firewall
nc -zv 20.10.192.136 11434
```

### Memory file corrupted
```bash
# Verify integrity
memvid verify infrastructure.mv2

# Rebuild from source
rm infrastructure.mv2
python ingest_documents.py --input ./knowledge --output ./memories/infrastructure.mv2
```

---

## 📚 Resources

- **Memvid Documentation**: https://docs.memvid.com
- **Memvid GitHub**: https://github.com/memvid/memvid
- **Ollama API**: https://ollama.com/docs/api
- **RAG Best Practices**: https://www.pinecone.io/learn/retrieval-augmented-generation/

---

## 🔮 Future Enhancements

- [ ] Add PDF ingestion support
- [ ] Implement conversation memory
- [ ] Add source citations in responses
- [ ] Multi-memory file search
- [ ] Web UI for document management
- [ ] Integration with LangFuse for RAG tracing

---

**Maintained by**: Oktay Savdi  
**Last Updated**: January 2026
