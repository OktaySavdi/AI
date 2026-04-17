---
name: "article-writing"
description: >
  Long-form writing in a supplied voice without generic AI tone. Covers structure,
  style matching, and editing. Activate for technical writing and articles.
metadata:
  version: 1.0.0
  category: content
---

# Article Writing Skill

## Core Principle

Match the user's voice exactly. Never use AI-generic phrases.

## Banned Phrases (AI Tell Signs)

Do NOT use:
- "In today's fast-paced world..."
- "It's worth noting that..."
- "Delve into", "leverage", "dive deep"
- "As an AI language model..."
- "In conclusion, ..."
- "Firstly, ... Secondly, ..."

## Article Structure

```
HOOK (1-2 paragraphs)
  → Concrete situation or unexpected claim
  → Not a platitude or broad statement

BODY
  → Each section has one clear point
  → Evidence or example before opinion
  → Short paragraphs (3-5 sentences max)
  → Code blocks / examples / data for technical articles

ENDING
  → Close with the same idea from the hook
  → Avoid "In conclusion" summaries
  → Leave the reader with one thought
```

## Voice Matching Process

1. Ask for 3+ writing samples from the user
2. Identify: sentence length, vocabulary level, use of contractions, humor style
3. Mirror: first draft in their style
4. User edits → extract delta → update style profile

## Technical Article Checklist

- [ ] Opening claims something specific, not general
- [ ] Code examples are runnable and tested
- [ ] Diagrams/tables for complex relationships
- [ ] No unexplained jargon unless the article teaches it
- [ ] Each section could stand alone if needed
- [ ] Sub-headings are statements, not questions (unless intentional)

## Editing Pass

After drafting, scan for:
1. Any sentence > 25 words → split
2. Passive voice > 20% → rewrite
3. Same word used 3+ times in a paragraph → vary
4. Generic opener ("This article will...") → delete and start at the real content
