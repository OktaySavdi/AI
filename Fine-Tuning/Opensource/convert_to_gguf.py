#!/usr/bin/env python3
"""Manual GGUF conversion using llama.cpp"""
import subprocess
import os

model_dir = "/home/os/ollama-finetuning/finetuned-k8s-model/gguf"
llama_cpp_dir = "/home/os/llama.cpp"

print("Converting model to GGUF Q4_K_M format...")
print(f"Model directory: {model_dir}")
print(f"llama.cpp directory: {llama_cpp_dir}")

# Convert to FP16 GGUF first
cmd = f"python3 {llama_cpp_dir}/convert_hf_to_gguf.py {model_dir} --outfile {model_dir}/k8s-model-f16.gguf --outtype f16"
print(f"\nRunning: {cmd}")
subprocess.run(cmd, shell=True, check=True)

# Quantize to Q4_K_M
cmd = f"{llama_cpp_dir}/build/bin/llama-quantize {model_dir}/k8s-model-f16.gguf {model_dir}/k8s-model-q4km.gguf Q4_K_M"
print(f"\nRunning: {cmd}")
subprocess.run(cmd, shell=True, check=True)

print("\n✅ GGUF conversion complete!")
print(f"Output file: {model_dir}/k8s-model-q4km.gguf")
