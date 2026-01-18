#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) with Memvid + Ollama

This module provides a complete RAG implementation using:
- Memvid for document storage and retrieval (.mv2 single-file memory)
- Ollama for LLM inference (self-hosted models)

Author: Oktay Savdi
Date: January 2026
"""

import os
import json
import requests
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class RAGConfig:
    """Configuration for RAG system"""
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://20.10.192.136:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:32b")
    memory_file: str = os.getenv("MEMVID_MEMORY_FILE", "./memories/infrastructure.mv2")
    top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    snippet_chars: int = int(os.getenv("RAG_SNIPPET_CHARS", "500"))
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "100"))


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._verify_connection()
    
    def _verify_connection(self):
        """Verify Ollama server is accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = [m["name"] for m in response.json().get("models", [])]
            print(f"✅ Connected to Ollama at {self.base_url}")
            print(f"   Available models: {', '.join(models[:5])}...")
            
            # Check if requested model is available
            if not any(self.model in m for m in models):
                print(f"⚠️  Warning: Model '{self.model}' may not be available")
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            raise
    
    def generate(self, prompt: str, system: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Generate response from Ollama"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama generation failed: {e}")
            raise
    
    def embed(self, text: str) -> List[float]:
        """Get embeddings from Ollama (if model supports it)"""
        payload = {
            "model": self.model,
            "prompt": text
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("embedding", [])
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Embedding not available: {e}")
            return []


class MemvidMemory:
    """
    Wrapper for Memvid memory operations.
    
    Note: This implementation uses the memvid-cli via subprocess
    as a fallback if the Python SDK is not available.
    """
    
    def __init__(self, memory_file: str):
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self._sdk_available = self._check_sdk()
    
    def _check_sdk(self) -> bool:
        """Check if memvid SDK is available"""
        try:
            import memvid_sdk
            return True
        except ImportError:
            print("⚠️  memvid-sdk not found, using CLI fallback")
            return False
    
    def create(self) -> bool:
        """Create a new memory file"""
        if self._sdk_available:
            try:
                import memvid_sdk
                # SDK implementation
                self.mem = memvid_sdk.create(str(self.memory_file))
                print(f"✅ Created memory: {self.memory_file}")
                return True
            except Exception as e:
                print(f"❌ Failed to create memory: {e}")
                return False
        else:
            # CLI fallback
            import subprocess
            try:
                result = subprocess.run(
                    ["memvid", "create", str(self.memory_file)],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    print(f"✅ Created memory: {self.memory_file}")
                    return True
                else:
                    print(f"❌ CLI error: {result.stderr}")
                    return False
            except FileNotFoundError:
                print("❌ memvid CLI not found. Install with: npm install -g memvid-cli")
                return False
    
    def add_document(self, content: str, title: Optional[str] = None,
                     uri: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> bool:
        """Add a document to memory"""
        if self._sdk_available:
            try:
                import memvid_sdk
                mem = memvid_sdk.open(str(self.memory_file))
                options = {}
                if title:
                    options["title"] = title
                if uri:
                    options["uri"] = uri
                if tags:
                    options["tags"] = tags
                
                mem.put(content.encode(), **options)
                mem.commit()
                return True
            except Exception as e:
                print(f"❌ Failed to add document: {e}")
                return False
        else:
            # For CLI, write to temp file and ingest
            import subprocess
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                temp_path = f.name
            
            try:
                result = subprocess.run(
                    ["memvid", "put", str(self.memory_file), "--input", temp_path],
                    capture_output=True, text=True, timeout=60
                )
                os.unlink(temp_path)
                return result.returncode == 0
            except Exception as e:
                os.unlink(temp_path)
                print(f"❌ CLI error: {e}")
                return False
    
    def search(self, query: str, top_k: int = 5, 
               snippet_chars: int = 500) -> List[Dict[str, Any]]:
        """Search memory for relevant documents"""
        if self._sdk_available:
            try:
                import memvid_sdk
                mem = memvid_sdk.open(str(self.memory_file))
                response = mem.find(
                    query=query,
                    k=top_k
                )
                return [
                    {
                        "text": hit.get("text", ""),
                        "title": hit.get("title", ""),
                        "score": hit.get("score", 0.0),
                        "uri": hit.get("uri", "")
                    }
                    for hit in response.get("hits", [])
                ]
            except Exception as e:
                print(f"❌ Search failed: {e}")
                return []
        else:
            # CLI fallback
            import subprocess
            try:
                result = subprocess.run(
                    ["memvid", "find", str(self.memory_file), 
                     "--query", query, "--limit", str(top_k), "--json"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    return json.loads(result.stdout).get("hits", [])
                return []
            except Exception as e:
                print(f"❌ CLI search error: {e}")
                return []
    
    def stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        if self._sdk_available:
            try:
                import memvid_sdk
                mem = memvid_sdk.open(str(self.memory_file))
                stats = mem.stats()
                return {
                    "frame_count": stats.frame_count,
                    "has_lex_index": stats.has_lex_index,
                    "has_vec_index": stats.has_vec_index
                }
            except Exception as e:
                return {"error": str(e)}
        else:
            import subprocess
            try:
                result = subprocess.run(
                    ["memvid", "stats", str(self.memory_file), "--json"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    return json.loads(result.stdout)
                return {"error": result.stderr}
            except Exception as e:
                return {"error": str(e)}


class InfrastructureRAG:
    """
    RAG system for Infrastructure knowledge retrieval.
    
    Combines Memvid for document storage/retrieval with Ollama for LLM generation.
    """
    
    SYSTEM_PROMPT = """You are an Infrastructure Specialist assistant with expertise in:
- Kubernetes (AKS, OpenShift, TKG)
- Terraform and Infrastructure as Code
- Ansible automation
- Cloud platforms (Azure, AWS, GCP)
- DevOps practices

Answer questions based ONLY on the provided context. If the context doesn't contain 
relevant information, say "I don't have specific information about that in my knowledge base."

Be concise, accurate, and provide code examples when relevant."""

    RAG_PROMPT_TEMPLATE = """Based on the following context, answer the question.

## Context (Retrieved from Knowledge Base):
{context}

## Question:
{question}

## Answer:"""

    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()
        
        print("\n" + "="*60)
        print("🧠 Initializing Infrastructure RAG System")
        print("="*60)
        
        # Initialize Ollama client
        self.llm = OllamaClient(
            base_url=self.config.ollama_base_url,
            model=self.config.ollama_model
        )
        
        # Initialize Memvid memory
        self.memory = MemvidMemory(self.config.memory_file)
        
        print(f"📁 Memory file: {self.config.memory_file}")
        print(f"🤖 Model: {self.config.ollama_model}")
        print("="*60 + "\n")
    
    def retrieve(self, query: str) -> str:
        """Retrieve relevant context for a query"""
        results = self.memory.search(
            query=query,
            top_k=self.config.top_k,
            snippet_chars=self.config.snippet_chars
        )
        
        if not results:
            return "No relevant documents found in knowledge base."
        
        # Format retrieved documents
        context_parts = []
        for i, hit in enumerate(results, 1):
            title = hit.get("title", "Untitled")
            text = hit.get("text", "")
            score = hit.get("score", 0)
            
            context_parts.append(f"### Document {i}: {title} (relevance: {score:.2f})")
            context_parts.append(text)
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def ask(self, question: str, include_sources: bool = True) -> str:
        """
        Ask a question using RAG.
        
        1. Retrieve relevant context from Memvid
        2. Generate answer using Ollama with context
        """
        print(f"\n🔍 Query: {question}")
        
        # Step 1: Retrieve context
        print("📚 Retrieving relevant documents...")
        context = self.retrieve(question)
        
        # Step 2: Build prompt
        prompt = self.RAG_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        
        # Step 3: Generate answer
        print("🤖 Generating answer...")
        answer = self.llm.generate(
            prompt=prompt,
            system=self.SYSTEM_PROMPT,
            temperature=0.3  # Lower temperature for factual answers
        )
        
        if include_sources:
            return f"{answer}\n\n---\n📚 *Based on {self.config.top_k} retrieved documents*"
        
        return answer
    
    def chat(self):
        """Interactive chat mode"""
        print("\n" + "="*60)
        print("💬 Infrastructure RAG Chat")
        print("Type 'quit' or 'exit' to end the session")
        print("Type 'stats' to see memory statistics")
        print("="*60 + "\n")
        
        while True:
            try:
                question = input("\n🧑 You: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break
                
                if question.lower() == "stats":
                    stats = self.memory.stats()
                    print(f"\n📊 Memory Stats: {json.dumps(stats, indent=2)}")
                    continue
                
                answer = self.ask(question)
                print(f"\n🤖 Assistant: {answer}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size // 2:
                chunk = text[start:start + break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return [c for c in chunks if c]  # Filter empty chunks


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Infrastructure RAG System")
    parser.add_argument("--query", "-q", type=str, help="Single query mode")
    parser.add_argument("--chat", "-c", action="store_true", help="Interactive chat mode")
    parser.add_argument("--memory", "-m", type=str, help="Path to memory file")
    parser.add_argument("--model", type=str, help="Ollama model to use")
    
    args = parser.parse_args()
    
    # Build config
    config = RAGConfig()
    if args.memory:
        config.memory_file = args.memory
    if args.model:
        config.ollama_model = args.model
    
    # Initialize RAG
    rag = InfrastructureRAG(config=config)
    
    if args.query:
        # Single query mode
        answer = rag.ask(args.query)
        print(f"\n{answer}")
    else:
        # Interactive chat mode
        rag.chat()
