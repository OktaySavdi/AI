# Open Notebook — Ollama Installation Guide

**Open Notebook** is an open-source, self-hosted alternative to Google's Notebook LM.
It supports 18+ AI providers including Ollama, giving you 100% local, private, zero-cost AI.

- GitHub: https://github.com/lfnovo/open-notebook
- Website: https://www.open-notebook.ai

---

## What Is Open Notebook?

| Feature | Open Notebook | Google Notebook LM |
|---|---|---|
| Privacy | Self-hosted, your data | Google cloud only |
| AI Provider | 18+ (Ollama, OpenAI, Anthropic…) | Google models only |
| Cost | Pay per use / free with Ollama | Free tier + subscription |
| API Access | Full REST API | None |
| Podcast speakers | 1–4 custom profiles | 2 only |
| Deployment | Docker, local, cloud | Google hosted only |

**Ollama support**: LLM ✅ · Embeddings ✅ · Speech-to-text ❌ · Text-to-speech ❌

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS/Windows) or Docker Engine (Linux)
- Docker Compose v2 (`docker compose` command)
- At least 8 GB RAM (16 GB recommended for larger models)
- Sufficient disk space for models (7B ≈ 4–5 GB, 14B ≈ 8–9 GB, 32B ≈ 18–20 GB)

---

## Option A — Bundled Ollama (Recommended for New Users)

This setup runs Ollama inside Docker alongside Open Notebook. Everything is managed in one `docker-compose.yml`.

### Step 1: Create the docker-compose.yml

```bash
mkdir open-notebook && cd open-notebook
curl -o docker-compose.yml \
  https://raw.githubusercontent.com/lfnovo/open-notebook/main/examples/docker-compose-ollama.yml
```

Or create it manually:

```yaml
---
services:
  surrealdb:
    image: surrealdb/surrealdb:v2
    command: start --log info --user root --pass root rocksdb:/mydata/mydatabase.db
    environment:
      - SURREAL_EXPERIMENTAL_GRAPHQL=true
    ports:
      - "8000:8000"
    pull_policy: always
    restart: always
    user: root
    volumes:
      - ./surreal_data:/mydata

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    pull_policy: always
    restart: always
    volumes:
      - ollama_models:/root/.ollama

  open_notebook:
    depends_on:
      - ollama
      - surrealdb
    environment:
      # REQUIRED: change to your own secret (min 16 characters)
      - OPEN_NOTEBOOK_ENCRYPTION_KEY=change-me-to-a-secret-string
      # Database
      - SURREAL_URL=ws://surrealdb:8000/rpc
      - SURREAL_USER=root
      - SURREAL_PASSWORD=root
      - SURREAL_NAMESPACE=open_notebook
      - SURREAL_DATABASE=open_notebook
      # Ollama — internal Docker network address
      - OLLAMA_BASE_URL=http://ollama:11434
    image: lfnovo/open_notebook:v1-latest
    ports:
      - "8502:8502"
      - "5055:5055"
    pull_policy: always
    restart: always
    volumes:
      - ./notebook_data:/app/data

volumes:
  ollama_models:
```

### Step 2: Set the Encryption Key

Edit `docker-compose.yml` and replace the encryption key:

```yaml
- OPEN_NOTEBOOK_ENCRYPTION_KEY=my-super-secret-key-123
```

Use any random string of 16+ characters. This encrypts stored API credentials.

### Step 3: Start Services

```bash
docker compose up -d
```

Wait 20–30 seconds for all containers to be healthy.

### Step 4: Pull an Ollama Model

```bash
# Pull a model into the running Ollama container
docker exec open-notebook-ollama-1 ollama pull mistral

# Or use a larger model if you have the VRAM/RAM
docker exec open-notebook-ollama-1 ollama pull qwen2.5:14b
docker exec open-notebook-ollama-1 ollama pull llama3.2:latest
docker exec open-notebook-ollama-1 ollama pull nomic-embed-text   # for embeddings
```

> **Note**: The container name may vary. Check with `docker ps` and look for the Ollama container name.

### Step 5: Open the UI

Navigate to http://localhost:8502

---

## Option B — External Ollama (Already Running on Another Host)

Use this if Ollama is already running on your machine, a remote server, or an H100 node.

### Step 1: Get the standard docker-compose.yml

```bash
mkdir open-notebook && cd open-notebook
curl -o docker-compose.yml \
  https://raw.githubusercontent.com/lfnovo/open-notebook/main/docker-compose.yml
```

### Step 2: Add the Ollama URL environment variable

Edit `docker-compose.yml` and add to the `open_notebook` service `environment` block:

```yaml
environment:
  - OPEN_NOTEBOOK_ENCRYPTION_KEY=my-super-secret-key-123
  - SURREAL_URL=ws://surrealdb:8000/rpc
  - SURREAL_USER=root
  - SURREAL_PASSWORD=root
  - SURREAL_NAMESPACE=open_notebook
  - SURREAL_DATABASE=open_notebook
  # Point to your external Ollama instance
  - OLLAMA_BASE_URL=http://192.168.1.100:11434
```

Replace `192.168.1.100` with your Ollama host IP or hostname.

> **Greentube H100**: Use `OLLAMA_BASE_URL=http://20.7.200.42:11434`

### Step 3: Start Open Notebook

```bash
docker compose up -d
```

---

## Configuring Ollama in the UI

After the UI loads at http://localhost:8502:

1. Go to **Settings** → **API Keys**
2. Click **Add Credential**
3. Select **Ollama** as the provider
4. Enter the URL:
   - Bundled Ollama: `http://ollama:11434`
   - External Ollama: `http://<your-host>:11434`
5. Click **Save** → **Test Connection** → **Discover Models** → **Register Models**

The discovered models are now available for chat, embeddings, and transformations.

---

## Recommended Models

### General Purpose LLM

| Model | Size on Disk | Min RAM | Best For |
|---|---|---|---|
| `mistral:latest` | ~4 GB | 8 GB | General use, fast |
| `llama3.2:latest` | ~2 GB | 8 GB | Fast, lightweight |
| `qwen2.5:7b` | ~4.5 GB | 8 GB | Strong multilingual |
| `qwen2.5:14b` | ~9 GB | 16 GB | Better quality |
| `qwen2.5-coder:32b` | ~18 GB | 32 GB | Code + reasoning |
| `qwen3.5:latest` | ~varies | 16 GB | Reasoning models |
| `deepseek-r1:14b` | ~9 GB | 16 GB | Reasoning / research |

### Embeddings (Required for Vector Search)

| Model | Pull Command |
|---|---|
| `nomic-embed-text` | `ollama pull nomic-embed-text` |
| `mxbai-embed-large` | `ollama pull mxbai-embed-large` |
| `bge-m3` | `ollama pull bge-m3` |

> You need a **separate embedding model** in addition to your LLM. Configure the embedding model in Settings → Default Models → Embedding Model.

---

## GPU Acceleration

### NVIDIA GPU (CUDA)

```yaml
# Add to the ollama service in docker-compose.yml
ollama:
  image: ollama/ollama:latest
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
  ports:
    - "11434:11434"
  volumes:
    - ollama_models:/root/.ollama
  restart: always
```

Requires [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) installed on the host.

### Apple Silicon (Metal)

Ollama on macOS uses Metal automatically. No additional configuration needed. Run Ollama natively (not in Docker) for best performance:

```bash
# Install Ollama natively on macOS
brew install ollama
ollama serve

# In a separate terminal, pull a model
ollama pull mistral
```

Then use Option B above with `OLLAMA_BASE_URL=http://host.docker.internal:11434`.

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPEN_NOTEBOOK_ENCRYPTION_KEY` | Yes | — | Secret key for encrypting stored API credentials |
| `SURREAL_URL` | Yes | `ws://surrealdb:8000/rpc` | SurrealDB WebSocket URL |
| `SURREAL_USER` | Yes | `root` | Database username |
| `SURREAL_PASSWORD` | Yes | `root` | Database password |
| `SURREAL_NAMESPACE` | Yes | `open_notebook` | Database namespace |
| `SURREAL_DATABASE` | Yes | `open_notebook` | Database name |
| `OLLAMA_BASE_URL` | No | — | Base URL of Ollama instance |
| `CHUNK_SIZE` | No | `1500` | Token chunk size for document ingestion |
| `CHUNK_OVERLAP` | No | `150` | Token overlap between chunks |
| `BASIC_AUTH_USERNAME` | No | — | Enable HTTP basic auth |
| `BASIC_AUTH_PASSWORD` | No | — | HTTP basic auth password |
| `CORS_ORIGINS` | No | — | Allowed CORS origins for the API |

---

## Ports

| Port | Service | Description |
|---|---|---|
| `8502` | Open Notebook UI | Main web interface |
| `5055` | Open Notebook API | REST API + Swagger docs at `/docs` |
| `8000` | SurrealDB | Database (internal only recommended) |
| `11434` | Ollama | Model serving endpoint |

---

## Verify Everything Is Running

```bash
# Check container status
docker compose ps

# Check Ollama models available
curl http://localhost:11434/api/tags

# Check Open Notebook API
curl http://localhost:5055/health

# View logs if something is wrong
docker compose logs open_notebook
docker compose logs ollama
docker compose logs surrealdb
```

---

## Common Issues

### Ollama model not appearing in UI

The model must be pulled before it shows up. After pulling, click **Discover Models** again in Settings.

```bash
docker exec <ollama-container-name> ollama list
```

### Container name for `docker exec`

```bash
docker ps --format "table {{.Names}}\t{{.Image}}" | grep ollama
```

### Slow first response

The first inference loads the model into memory (cold start). Subsequent requests are fast. Expected wait: 5–30 seconds depending on model size and hardware.

### Out of memory (OOM) errors

Use a smaller model or increase Docker memory limit in Docker Desktop → Settings → Resources.

### Cannot connect to external Ollama from Docker container

Docker containers cannot reach `localhost` or `127.0.0.1` on the host. Use:
- macOS/Windows: `http://host.docker.internal:11434`
- Linux: the host's LAN IP (e.g., `http://192.168.1.x:11434`)

---

## Upgrade Open Notebook

```bash
docker compose pull
docker compose up -d
```

Data is persisted in `./surreal_data/` and `./notebook_data/` volumes.

---

## Useful Commands

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Restart a single service
docker compose restart open_notebook

# Pull a new model
docker exec $(docker ps -qf "ancestor=ollama/ollama") ollama pull <model>

# List available models in Ollama
docker exec $(docker ps -qf "ancestor=ollama/ollama") ollama list

# Remove a model to free disk space
docker exec $(docker ps -qf "ancestor=ollama/ollama") ollama rm <model>

# View all logs
docker compose logs -f

# Clean up everything (WARNING: deletes data volumes)
docker compose down -v
```

---

## References

- [Official Installation Guide](https://github.com/lfnovo/open-notebook/blob/main/docs/1-INSTALLATION/index.md)
- [Environment Reference](https://github.com/lfnovo/open-notebook/blob/main/docs/5-CONFIGURATION/environment-reference.md)
- [Ollama Model Library](https://ollama.com/library)
- [Discord Community](https://discord.gg/37XJPXfz2w)
