# Quick Start Guide - K8s Assistant

## 1. Test the Pre-trained Model (30 seconds)

The model is already trained and deployed! Just test it:

```bash
# Test with a simple query
docker exec -it ollama ollama run k8s-assistant "List all pods in the default namespace"

# Expected output: kubectl get pods -n default
```

## 2. Available Commands

```bash
# Interactive mode
docker exec -it ollama ollama run k8s-assistant

# Single query
docker exec -it ollama ollama run k8s-assistant "Your K8s question here"

# Check model info
docker exec ollama ollama list | grep k8s

# API call
curl http://localhost:11434/api/generate -d '{
  "model": "k8s-assistant",
  "prompt": "Scale deployment to 5 replicas",
  "stream": false
}'
```

## 3. Example Queries

Try these queries to see the model in action:

### Basic Commands
```bash
docker exec -it ollama ollama run k8s-assistant "List all pods"
docker exec -it ollama ollama run k8s-assistant "Get pod details for nginx-pod"
docker exec -it ollama ollama run k8s-assistant "Delete service web-service"
```

### Deployments & Scaling
```bash
docker exec -it ollama ollama run k8s-assistant "Scale deployment web-app to 10 replicas"
docker exec -it ollama ollama run k8s-assistant "Update deployment image to nginx:1.21"
docker exec -it ollama ollama run k8s-assistant "Rollback deployment web-app"
```

### Advanced Queries
```bash
docker exec -it ollama ollama run k8s-assistant "List pods with high memory usage"
docker exec -it ollama ollama run k8s-assistant "Get pod logs from the last hour"
docker exec -it ollama ollama run k8s-assistant "Create a service for deployment web-app"
```

### YAML Configurations
```bash
docker exec -it ollama ollama run k8s-assistant "Create a pod with ConfigMap volume"
docker exec -it ollama ollama run k8s-assistant "Create a deployment with resource limits"
```

## 4. Retrain (if needed)

If you want to retrain with modified data:

```bash
cd /home/os/ollama-finetuning

# Edit training data
vim /home/os/K8S_AzureOpenAI.jsonl

# Retrain
python3 finetune_unsloth.py

# Convert to GGUF
python3 convert_to_gguf.py

# Reimport to Ollama
docker cp finetuned-k8s-model/gguf/k8s-model-q4km.gguf ollama:/tmp/
docker exec ollama ollama create k8s-assistant -f /tmp/Modelfile
```

## 5. Files Location

```
/home/os/ollama-finetuning/
├── README.md                  # Full documentation
├── TRAINING_SUMMARY.md        # Detailed training results
├── QUICK_START.md            # This file
├── finetune_unsloth.py       # Training script
├── convert_to_gguf.py        # GGUF conversion
├── test_model.py             # Testing script
├── requirements.txt          # Python dependencies
├── Modelfile                 # Quick setup config (no training)
├── Modelfile-finetuned       # Fine-tuned config (CLI/API) ✓ Recommended
├── Modelfile-continue        # IDE/Continue extension optimized
└── finetuned-k8s-model/      # Model output
    ├── checkpoint-100/
    ├── checkpoint-200/
    ├── final/
    └── gguf/
        ├── k8s-model-f16.gguf    # Full precision (14.5GB)
        └── k8s-model-q4km.gguf   # Quantized (4.4GB) ✓ In use
```

### Which Modelfile to Use?

| Use Case | Modelfile | Context | Notes |
|----------|-----------|---------|-------|
| **Terminal/Scripts** | `Modelfile-finetuned` | 8K tokens | Best for CLI |
| **VS Code/Continue** | `Modelfile-continue` | 16K tokens | Prevents context errors |
| **Quick Testing** | `Modelfile` | 2K tokens | No training needed |

## 6. Troubleshooting

**Model not responding?**
```bash
docker restart ollama
docker exec ollama ollama list
```

**Want to remove and reimport?**
```bash
docker exec ollama ollama rm k8s-assistant
docker cp finetuned-k8s-model/gguf/k8s-model-q4km.gguf ollama:/tmp/
docker exec ollama ollama create k8s-assistant -f /tmp/Modelfile
```

**Check model performance?**
```bash
# Watch GPU usage
nvidia-smi

# Check Ollama logs
docker logs ollama -f
```

## 7. Best Practices

1. **Be Specific**: "List pods in namespace production" works better than "show pods"
2. **Use Names**: Include specific resource names when available
3. **Test Commands**: Always verify generated commands before running in production
4. **Namespace Aware**: Always specify namespace for better accuracy
5. **Review YAML**: Check generated YAML before applying to cluster

## 8. Integration Examples

### Python Script
```python
import requests

def ask_k8s_assistant(question):
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'k8s-assistant',
        'prompt': question,
        'stream': False
    })
    return response.json()['response']

# Example
command = ask_k8s_assistant("List all pods in production namespace")
print(command)  # kubectl get pods -n production
```

### Shell Script
```bash
#!/bin/bash
ask_k8s() {
    docker exec ollama ollama run k8s-assistant "$1"
}

# Example
ask_k8s "Scale deployment web-app to 5 replicas"
```

### VS Code / Continue Extension

**If you get "Message exceeds context limit" error:**

1. Use the Continue-optimized Modelfile:
```bash
cd /home/os/ollama-finetuning
docker cp Modelfile-continue ollama:/tmp/Modelfile-continue
docker exec ollama ollama create k8s-assistant -f /tmp/Modelfile-continue
```

2. Configure Continue (`~/.continue/config.json`):
```json
{
  "models": [
    {
      "title": "K8s Assistant",
      "provider": "ollama",
      "model": "k8s-assistant",
      "apiBase": "http://localhost:11434"
    }
  ]
}
```

3. Restart VS Code and test with: "List all pods in default namespace"

## 9. Model Info

- **Name**: k8s-assistant:latest
- **Size**: 4.4 GB (Q4_K_M)
- **Base**: Mistral-7B-v0.3
- **Training**: 1,980 K8s examples
- **Status**: Production ready ✓

## 10. Need Help?

- Full docs: `cat /home/os/ollama-finetuning/README.md`
- Training details: `cat /home/os/ollama-finetuning/TRAINING_SUMMARY.md`
- Test script: `python3 /home/os/ollama-finetuning/test_model.py k8s-assistant`

---

**Ready to go!** Your model is trained, deployed, and serving requests. 🚀
