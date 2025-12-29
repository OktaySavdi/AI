# Deploy Ollama on Azure VM for Qwen 2.5

## Prerequisites

- Azure subscription with GPU quota approved (80 vCores for Standard_NC80adis_H100_v5)
- `az` CLI installed
- SSH key pair

## 1. Create Azure GPU Virtual Machine

```bash
# Create resource group
az group create --name AZ-RG-TEST-01 --location eastus2

# Create VM with H100 GPU
az vm create \
  --resource-group AZ-RG-TEST-01 \
  --name azeus2-vm-llm-test-01 \
  --size Standard_NC80adis_H100_v5 \
  --image Ubuntu2204 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard \
  --nic-delete-option Delete \
  --os-disk-delete-option Delete

# Open Ollama port
az vm open-port \
  --resource-group AZ-RG-TEST-01 \
  --name azeus2-vm-llm-test-01 \
  --port 11434 \
  --priority 1001

# Get public IP
VM_IP=$(az vm show -d \
  --resource-group AZ-RG-TEST-01 \
  --name azeus2-vm-llm-test-01 \
  --query publicIps -o tsv)

echo "VM IP: $VM_IP"
```

## 2. Install NVIDIA GPU Drivers

**Option A: Using Azure GPU Driver Extension (Recommended)**

From your **local machine**:

```bash
# Install NVIDIA GPU driver extension
az vm extension set \
  --resource-group AZ-RG-TEST-01 \
  --vm-name azeus2-vm-llm-test-01 \
  --name NvidiaGpuDriverLinux \
  --publisher Microsoft.HpcCompute \
  --version 1.9

# Monitor installation (takes 5-10 minutes)
az vm extension show \
  --resource-group AZ-RG-TEST-01 \
  --vm-name azeus2-vm-llm-test-01 \
  --name NvidiaGpuDriverLinux \
  --query "{Status: provisioningState, Message: instanceView.statuses[0].message}"
```

**Option B: Manual Installation**

SSH to VM and install CUDA drivers:

```bash
# SSH to VM
ssh azureuser@$VM_IP

# Check GPU is detected
lspci | grep -i nvidia

# Install prerequisites
sudo apt-get update
sudo apt-get install -y build-essential

# Download and install CUDA (includes NVIDIA drivers)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-drivers-565

# Reboot to load drivers
sudo reboot
```

**Verify GPU Drivers**

After reboot (wait 2-3 minutes), SSH back and verify:

```bash
ssh azureuser@$VM_IP

# Verify NVIDIA driver is loaded
nvidia-smi

# Expected output: H100L 94GB GPU info
```

## 3. Install Docker and NVIDIA Container Toolkit

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Logout and login to apply docker group
exit
```

## 4. Deploy Ollama with Docker

```bash
# SSH back after reboot
ssh azureuser@$VM_IP

# Verify GPU
nvidia-smi

# Run Ollama with GPU support
docker run -d \
  --name ollama \
  --gpus all \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  --restart unless-stopped \
  ollama/ollama

# Verify Ollama is running
docker logs ollama
curl http://localhost:11434/api/tags
```

## 5. Pull Qwen 2.5 Model

```bash
# Pull Qwen 2.5 32B (on the VM)
docker exec ollama ollama pull qwen2.5-coder:32b

# Or from your local machine
curl http://$VM_IP:11434/api/pull -d '{"name": "qwen2.5-coder:32b"}'

# Monitor progress
docker logs -f ollama
```

**Manage Models**

```bash
# List installed models
docker exec ollama ollama list

# Remove a model
docker exec ollama ollama rm qwen2.5-coder:32b
```

## 6. Test Inference

```bash
# From VM
docker exec ollama ollama run qwen2.5-coder:32b "Explain Kubernetes in one sentence"

# From local machine
curl http://$VM_IP:11434/api/generate -d '{
  "model": "qwen2.5-coder:32b",
  "prompt": "Explain Kubernetes in one sentence",
  "stream": false
}'
```

## 7. Integrate with Continue (VS Code)

Update your `~/.continue/config.yaml`:

```yaml
models:
  - name: Qwen 2.5 32B (Azure VM)
    provider: ollama
    model: qwen2.5-coder:32b
    apiBase: http://YOUR_VM_IP:11434
    roles:
      - chat
      - edit
      - apply
```

## 8. (Optional) Install Open WebUI

```bash
# Run Open WebUI on the VM
docker run -d \
  --name open-webui \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://localhost:11434 \
  -v open-webui:/app/backend/data \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main

# Open port for WebUI
az vm open-port \
  --resource-group AZ-RG-TEST-01 \
  --name azeus2-vm-llm-test-01 \
  --port 3000 \
  --priority 1002

# Access at http://$VM_IP:3000
```

## Resource Requirements

| Component | Specification |
|-----------|--------------|
| VM Size | Standard_NC80adis_H100_v5 |
| GPU | 2x NVIDIA H100 (80GB each) |
| vCPUs | 80 |
| Memory | 640GB RAM |
| OS Disk | 128GB Premium SSD |

## Cost Estimate

- **Standard_NC80adis_H100_v5**: ~$18/hour (~$13,104/month for 24/7)
- **Storage**: ~$20-30/month
- **Total**: ~$13,134/month

## Monitoring

```bash
# Check GPU usage
ssh azureuser@$VM_IP "nvidia-smi"

# Check Ollama logs
ssh azureuser@$VM_IP "docker logs ollama"

# Check model list
curl http://$VM_IP:11434/api/tags
```

## Cleanup

```bash
# Delete VM and all resources
az group delete --name AZ-RG-TEST-01 --yes --no-wait
```

## Troubleshooting

### GPU Drivers Not Working

**Check extension status:**
```bash
# From local machine
az vm extension show \
  --resource-group AZ-RG-TEST-01 \
  --vm-name azeus2-vm-llm-test-01 \
  --name NvidiaGpuDriverLinux

# Check extension logs on VM
sudo cat /var/log/azure/nvidia-vmext-status
```

**Reinstall extension:**
```bash
# From local machine
az vm extension delete \
  --resource-group AZ-RG-TEST-01 \
  --vm-name azeus2-vm-llm-test-01 \
  --name NvidiaGpuDriverLinux

az vm extension set \
  --resource-group AZ-RG-TEST-01 \
  --vm-name azeus2-vm-llm-test-01 \
  --name NvidiaGpuDriverLinux \
  --publisher Microsoft.HpcCompute \
  --version 1.9

# Wait 10 minutes, then SSH and reboot
ssh azureuser@$VM_IP
sudo reboot
```

**Manual verification:**
```bash
# Check GPU hardware
lspci | grep -i nvidia

# Check driver module
lsmod | grep nvidia

# Check driver version
nvidia-smi
```

### Secure Boot Blocking Drivers

If `nvidia-smi` fails with "couldn't communicate", Secure Boot is likely blocking the driver. Disable it:

```bash
# From local machine
az vm update \
  --resource-group AZ-RG-TEST-01 \
  --name azeus2-vm-llm-test-01 \
  --set securityProfile.uefiSettings.secureBootEnabled=false

# Restart VM
az vm restart --resource-group AZ-RG-TEST-01 --name azeus2-vm-llm-test-01
```

### Docker Permission Denied
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

### Ollama Connection Refused
```bash
# Check if running
docker ps | grep ollama

# Restart if needed
docker restart ollama

# Check firewall
sudo ufw status
```
