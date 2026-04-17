---
name: "cost-aware-llm-pipeline"
description: >
  LLM cost optimization: model routing, budget tracking, token estimation,
  and pipeline cost analysis. Activate when designing or optimizing LLM workflows.
metadata:
  version: 1.0.0
  category: engineering
---

# Cost-Aware LLM Pipeline Skill

## Model Routing Strategy

Route tasks to the cheapest model that can handle them:

| Task Type | Recommended Model | Why |
|---|---|---|
| Simple extraction/classification | haiku / gpt-4o-mini | < 10k tokens, no reasoning |
| Code generation, analysis | sonnet / gpt-4o | Default quality/cost |
| Complex reasoning, architecture | opus / o1 | Only when needed |
| Embeddings | text-embedding-3-small | 5x cheaper than large |

## Token Estimation

```python
import tiktoken

def estimate_tokens(text: str, model: str = "gpt-4o") -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def estimate_cost(prompt: str, completion: str, model: str = "gpt-4o") -> float:
    PRICING = {
        "gpt-4o":        {"input": 2.50, "output": 10.00},  # per 1M tokens
        "gpt-4o-mini":   {"input": 0.15, "output": 0.60},
        "claude-sonnet": {"input": 3.00, "output": 15.00},
        "claude-haiku":  {"input": 0.25, "output": 1.25},
    }
    p = PRICING[model]
    in_tokens = estimate_tokens(prompt, model) / 1_000_000
    out_tokens = estimate_tokens(completion, model) / 1_000_000
    return in_tokens * p["input"] + out_tokens * p["output"]
```

## Budget Tracking

```python
from dataclasses import dataclass, field
from threading import Lock

@dataclass
class BudgetTracker:
    limit_usd: float
    spent_usd: float = 0.0
    _lock: Lock = field(default_factory=Lock)

    def check_and_spend(self, cost: float) -> bool:
        with self._lock:
            if self.spent_usd + cost > self.limit_usd:
                raise BudgetExceededError(f"Would exceed ${self.limit_usd:.2f} budget")
            self.spent_usd += cost
            return True
```

## Prompt Optimization

```python
# Cache repeated prompts
from functools import lru_cache

@lru_cache(maxsize=1000)
def classify_intent(text: str) -> str:
    # Only call LLM for unique texts
    return llm.complete(CLASSIFICATION_PROMPT + text)

# Batch requests
def classify_batch(texts: list[str]) -> list[str]:
    unique = list(set(texts))
    results = {t: classify_intent(t) for t in unique}
    return [results[t] for t in texts]
```

## Pipeline Cost Analysis

For a pipeline processing 1M documents/day:

| Step | Model | Tokens/doc | Daily cost |
|---|---|---|---|
| Extract metadata | haiku | 500 | $125 |
| Classify category | haiku | 200 | $50 |
| Generate summary | sonnet | 1000 | $3,000 |
| **Total** | | | **$3,175** |

Optimization: cache summaries, batch classification → 40% cost reduction.

## Claude Code Token Management

```bash
/cost                         # check current session spend
/clear                        # reset context (free)
/compact                      # summarize context
export MAX_THINKING_TOKENS=10000  # reduce hidden thinking cost
```
