#!/usr/bin/env python3
"""Quick test to verify training setup works - runs 10 steps only"""
from unsloth import FastLanguageModel
import json
import torch
from datasets import Dataset
from transformers import TrainingArguments
from trl import SFTTrainer

# Configuration for quick test
MAX_SEQ_LENGTH = 512
MODEL_NAME = "unsloth/mistral-7b-v0.3-bnb-4bit"
OUTPUT_DIR = "./test-model"
TRAINING_DATA = "/home/os/K8S_AzureOpenAI.jsonl"

def load_and_prepare_data(file_path, max_samples=50):
    """Load JSONL data and convert to training format."""
    data = []
    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= max_samples:
                break
            item = json.loads(line)
            messages = item['messages']
            user_msg = next(m['content'] for m in messages if m['role'] == 'user')
            assistant_msg = next(m['content'] for m in messages if m['role'] == 'assistant')
            formatted_text = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{user_msg}

### Response:
{assistant_msg}"""
            data.append({"text": formatted_text})
    return Dataset.from_list(data)

print("🚀 Starting Quick Test (10 steps only)...")
print("Loading model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)

print("Setting up LoRA...")
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
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

print("Loading training data (50 samples for test)...")
dataset = load_and_prepare_data(TRAINING_DATA, max_samples=50)
train_test = dataset.train_test_split(test_size=0.2, seed=42)

print(f"Training on {len(train_test['train'])} examples...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_test['train'],
    eval_dataset=train_test['test'],
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=2,
        max_steps=10,  # Only 10 steps for test
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=2,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir=OUTPUT_DIR,
    ),
)

print("Training for 10 steps...")
trainer.train()
print("\n✅ Quick test successful! Training setup verified.")
print("\nNow run the full training with: python3 finetune_unsloth.py")
