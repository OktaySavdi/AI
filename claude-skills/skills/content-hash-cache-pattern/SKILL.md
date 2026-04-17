---
name: "content-hash-cache-pattern"
description: >
  SHA-256 content hash caching for file processing pipelines. Avoids reprocessing
  unchanged files. Activate when building file processing or ETL pipelines.
metadata:
  version: 1.0.0
  category: engineering
---

# Content Hash Cache Pattern Skill

## Pattern Overview

Instead of timestamp-based caching, hash file content. This ensures:
- Files are reprocessed only when content actually changes
- Renames or timestamp changes don't trigger unnecessary work
- Cache is portable across machines

## Python Implementation

```python
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass

@dataclass
class CacheEntry:
    content_hash: str
    result: dict

class ContentHashCache:
    def __init__(self, cache_path: Path) -> None:
        self._path = cache_path
        self._store: dict[str, CacheEntry] = self._load()

    def _load(self) -> dict[str, CacheEntry]:
        if not self._path.exists():
            return {}
        with self._path.open() as f:
            data = json.load(f)
        return {k: CacheEntry(**v) for k, v in data.items()}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w") as f:
            json.dump({k: vars(v) for k, v in self._store.items()}, f)

    @staticmethod
    def hash_file(path: Path) -> str:
        sha = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha.update(chunk)
        return sha.hexdigest()

    def get(self, path: Path) -> dict | None:
        current_hash = self.hash_file(path)
        entry = self._store.get(str(path))
        if entry and entry.content_hash == current_hash:
            return entry.result
        return None

    def set(self, path: Path, result: dict) -> None:
        current_hash = self.hash_file(path)
        self._store[str(path)] = CacheEntry(content_hash=current_hash, result=result)
        self._save()
```

## Usage in a Pipeline

```python
cache = ContentHashCache(Path(".cache/processed.json"))

def process_files(files: list[Path]) -> list[dict]:
    results = []
    for file in files:
        cached = cache.get(file)
        if cached:
            results.append(cached)
            continue

        result = expensive_process(file)
        cache.set(file, result)
        results.append(result)
    return results
```

## Shell Implementation

```bash
CACHE_DIR=".cache/hashes"
mkdir -p "$CACHE_DIR"

process_if_changed() {
    local file="$1"
    local hash
    hash=$(sha256sum "$file" | cut -d' ' -f1)
    local cache_file="$CACHE_DIR/${hash}.done"

    if [[ -f "$cache_file" ]]; then
        echo "CACHED: $file"
        return 0
    fi

    process_file "$file"
    touch "$cache_file"
}
```

## When to Use This Pattern

- Processing large files that rarely change (configs, binaries, CSVs)
- ETL pipelines where re-running is expensive
- Build systems (like Make's approach, but portable)
- LLM pipelines where API calls are expensive — hash before calling
