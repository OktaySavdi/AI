#!/usr/bin/env python3
"""
Interactive Query Script for RAG System

Usage:
    python query_rag.py                    # Interactive mode
    python query_rag.py -q "Your question" # Single query
    python query_rag.py -m ./my-memory.mv2 # Use specific memory

Author: Oktay Savdi
Date: January 2026
"""

import argparse
from rag_example import InfrastructureRAG, RAGConfig


def main():
    parser = argparse.ArgumentParser(
        description="Query the Infrastructure RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive chat mode
  python query_rag.py

  # Single query
  python query_rag.py -q "How do I create a Kubernetes deployment?"

  # Use specific memory file
  python query_rag.py -m ./memories/k8s-docs.mv2

  # Use different model
  python query_rag.py --model deepseek-coder-v2:16b -q "Explain Terraform modules"
        """
    )
    
    parser.add_argument(
        "--query", "-q", type=str,
        help="Single query to ask (skips interactive mode)"
    )
    parser.add_argument(
        "--memory", "-m", type=str,
        help="Path to Memvid memory file (.mv2)"
    )
    parser.add_argument(
        "--model", type=str,
        help="Ollama model to use (default: qwen2.5-coder:32b)"
    )
    parser.add_argument(
        "--ollama-url", type=str,
        help="Ollama server URL (default: http://20.10.192.136:11434)"
    )
    parser.add_argument(
        "--top-k", type=int, default=5,
        help="Number of documents to retrieve (default: 5)"
    )
    parser.add_argument(
        "--no-sources", action="store_true",
        help="Don't show source information in answers"
    )
    
    args = parser.parse_args()
    
    # Build configuration
    config = RAGConfig()
    
    if args.memory:
        config.memory_file = args.memory
    if args.model:
        config.ollama_model = args.model
    if args.ollama_url:
        config.ollama_base_url = args.ollama_url
    if args.top_k:
        config.top_k = args.top_k
    
    # Initialize RAG
    try:
        rag = InfrastructureRAG(config=config)
    except Exception as e:
        print(f"❌ Failed to initialize RAG: {e}")
        return 1
    
    # Execute query or start chat
    if args.query:
        # Single query mode
        try:
            answer = rag.ask(args.query, include_sources=not args.no_sources)
            print(f"\n{'='*60}")
            print("🤖 Answer:")
            print("="*60)
            print(answer)
            print("="*60 + "\n")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return 1
    else:
        # Interactive chat mode
        rag.chat()
    
    return 0


if __name__ == "__main__":
    exit(main())
