---
name: "regex-vs-llm-structured-text"
description: >
  Decision framework for choosing between regex and LLM for text parsing.
  Covers performance, accuracy, and cost trade-offs. Activate when parsing text.
metadata:
  version: 1.0.0
  category: engineering
---

# Regex vs LLM for Structured Text Skill

## Decision Framework

```
Is the format strictly defined and consistent?
  YES → Use regex
  NO  ↓
Does it vary slightly but follow a pattern?
  YES → Use regex with optional groups
  NO  ↓
Is it natural language or free-form?
  YES → Use LLM
  NO  ↓
Is it semi-structured (HTML, PDFs, mixed)?
  YES → Use parser library + LLM for ambiguous parts
```

## Use Regex When

- Format is well-defined and consistent (dates, IDs, phone numbers, emails)
- Volume is high and cost matters (>1M/day)
- Latency must be < 10ms
- Output needs to be 100% predictable

```python
import re

DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.\w+")
UUID_RE  = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
```

## Use LLM When

- Format is inconsistent or natural language
- Need semantic understanding ("extract the person's title and company")
- Handling international variations, edge cases would require 50+ regexes
- Acceptable latency ≥ 100ms

```python
from openai import OpenAI

def extract_contact_info(text: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # cheap for extraction
        response_format={"type": "json_object"},
        messages=[{
            "role": "user",
            "content": f"Extract name, email, phone from: {text}\nReturn JSON."
        }]
    )
    return json.loads(response.choices[0].message.content)
```

## Hybrid Pattern (Best of Both)

```python
def extract_invoice_data(text: str) -> dict:
    # Fast regex for well-defined fields
    invoice_no = re.search(r"INV-(\d{6})", text)
    date = re.search(r"Date:\s*(\d{4}-\d{2}-\d{2})", text)

    # LLM for ambiguous/variable fields
    if invoice_no and date:
        # Already have structured data — avoid LLM cost
        return {"invoice_no": invoice_no.group(1), "date": date.group(1)}

    # Fall back to LLM for unusual formats
    return llm_extract(text)
```

## Performance Comparison

| Approach | Latency | Cost/1M | Accuracy |
|---|---|---|---|
| Regex | < 1ms | ~$0 | 100% on matched, 0% on unmatched |
| LLM (haiku) | 100-500ms | $0.25-1.25 | 95-99% |
| LLM (sonnet) | 500ms-2s | $3-15 | 99%+ |
| Hybrid | 1-500ms | $0-0.25 | 99%+ |
