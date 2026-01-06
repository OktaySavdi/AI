#!/usr/bin/env python3
"""
Fine-tune an open-source LLM using Unsloth and prepare it for Ollama.
This script uses Unsloth for efficient 4-bit QLoRA fine-tuning.
"""
from unsloth import FastLanguageModel
import json
import torch
from datasets import Dataset
from transformers import TrainingArguments
from trl import SFTTrainer

# Configuration
MAX_SEQ_LENGTH = 2048
MODEL_NAME = "unsloth/mistral-7b-v0.3-bnb-4bit"  # You can change this to other models
OUTPUT_DIR = "./finetuned-k8s-model"
TRAINING_DATA = "/home/os/K8S_AzureOpenAI.jsonl"

def load_and_prepare_data(file_path):
    """Load JSONL data and convert to training format."""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            item = json.loads(line)
            messages = item['messages']
            
            # Convert to Alpaca format
            user_msg = next(m['content'] for m in messages if m['role'] == 'user')
            assistant_msg = next(m['content'] for m in messages if m['role'] == 'assistant')
            
            # Create formatted prompt with EOS token to teach model when to stop
            formatted_text = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{user_msg}

### Response:
{assistant_msg}</s>"""
            
            data.append({"text": formatted_text})
    
    return Dataset.from_list(data)

def main():
    print("Loading model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,  # Auto-detect
        load_in_4bit=True,
    )
    
    print("Setting up LoRA...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,  # LoRA rank
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
        use_rslora=False,
        loftq_config=None,
    )
    
    print("Loading training data...")
    dataset = load_and_prepare_data(TRAINING_DATA)
    print(f"Loaded {len(dataset)} examples")
    
    # Split into train/eval
    train_test = dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = train_test['train']
    eval_dataset = train_test['test']
    
    print("Starting training...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LENGTH,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=10,
            max_steps=200,  # Reduced from 500 for faster training
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir=OUTPUT_DIR,
            save_steps=100,
            eval_steps=50,
            eval_strategy="steps",
        ),
    )
    
    trainer.train()
    
    print("Saving model...")
    model.save_pretrained(f"{OUTPUT_DIR}/final")
    tokenizer.save_pretrained(f"{OUTPUT_DIR}/final")
    
    print("Converting to GGUF format for Ollama...")
    model.save_pretrained_gguf(
        f"{OUTPUT_DIR}/gguf",
        tokenizer,
        quantization_method="q4_k_m",
    )
    
    print(f"\nTraining complete!")
    print(f"Model saved to: {OUTPUT_DIR}")
    print(f"GGUF model for Ollama: {OUTPUT_DIR}/gguf")
    print("\nNext steps:")
    print("1. Create a Modelfile")
    print("2. Import to Ollama: ollama create k8s-assistant -f Modelfile")

if __name__ == "__main__":
    main()
