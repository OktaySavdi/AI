#!/usr/bin/env python3
"""
Simple test script to validate your fine-tuned model
"""

import requests
import json

OLLAMA_URL = "http://localhost:11434"

def test_model(model_name="k8s-assistant", prompt="List all pods in the default namespace"):
    """Test the model with a sample prompt"""
    
    url = f"{OLLAMA_URL}/api/generate"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    
    print(f"Testing model: {model_name}")
    print(f"Prompt: {prompt}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {result['response']}")
        print("-" * 50)
        print(f"Total duration: {result.get('total_duration', 0) / 1e9:.2f}s")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        print("Make sure Ollama is running on localhost:11434")

def test_multiple_prompts(model_name="k8s-assistant"):
    """Test with multiple Kubernetes-related prompts"""
    
    test_prompts = [
        "List all pods in the default namespace",
        "Create a namespace called 'production'",
        "Get logs from a pod named 'web-app'",
        "Scale deployment 'nginx' to 5 replicas",
        "List all services across all namespaces",
    ]
    
    print(f"\n{'='*60}")
    print(f"Running {len(test_prompts)} test prompts")
    print(f"{'='*60}\n")
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}/{len(test_prompts)}")
        test_model(model_name, prompt)
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    else:
        model_name = "k8s-assistant"
    
    # Run comprehensive tests
    test_multiple_prompts(model_name)
