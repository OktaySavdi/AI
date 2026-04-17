---
name: "nutrient-document-processing"
description: >
  Document processing with Nutrient (formerly PSPDFKit) SDK. Covers PDF
  generation, annotation, form filling, and document conversion. Activate for
  document processing tasks.
metadata:
  version: 1.0.0
  category: engineering
---

# Nutrient Document Processing Skill

## Nutrient SDK Overview

Nutrient (formerly PSPDFKit) provides server-side and client-side document processing:
- PDF generation from HTML/templates
- Annotation and redaction
- Form filling and flattening
- Digital signatures
- Format conversion (Word → PDF, PDF → images, etc.)

## Node.js: PDF from HTML

```javascript
const Nutrient = require('@nutrient-sdk/document-engine');

const client = new Nutrient.DocumentEngine({
  baseUrl: process.env.NUTRIENT_URL,
  authKey: process.env.NUTRIENT_API_KEY,
});

// HTML to PDF
const pdfBuffer = await client.build({
  parts: [{
    html: {
      content: '<h1>Invoice #12345</h1><p>Amount: $500</p>',
    },
  }],
});

await fs.writeFile('invoice.pdf', pdfBuffer);
```

## Python: Document Conversion

```python
import requests
import os

BASE_URL = os.environ["NUTRIENT_URL"]
API_KEY = os.environ["NUTRIENT_API_KEY"]

def convert_docx_to_pdf(docx_path: str) -> bytes:
    with open(docx_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/convert",
            headers={"Authorization": f"Token {API_KEY}"},
            files={"file": ("document.docx", f)},
            data={"output_format": "pdf"},
        )
    response.raise_for_status()
    return response.content
```

## Form Filling

```python
def fill_pdf_form(template_path: str, field_data: dict[str, str]) -> bytes:
    with open(template_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/form-fill",
            headers={"Authorization": f"Token {API_KEY}"},
            files={"file": f},
            json={"fields": field_data},
        )
    response.raise_for_status()
    return response.content

# Usage
pdf = fill_pdf_form("template.pdf", {
    "first_name": "Alice",
    "last_name": "Smith",
    "date": "2024-01-15",
})
```

## Redaction

```javascript
// Redact PII from a document
const result = await client.redact({
  documentId: documentId,
  regions: [
    {
      pageIndex: 0,
      type: 'text',
      regex: '\\d{3}-\\d{2}-\\d{4}',  // SSN pattern
    },
  ],
});
```

## Best Practices

- Store Nutrient API keys in environment variables or secret vaults
- Cache converted documents — conversion is expensive
- Validate file MIME types before sending to Nutrient
- Set reasonable timeouts (PDF generation can take 30-60s for complex docs)
