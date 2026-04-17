---
name: "content-engine"
description: >
  Multi-platform social content and repurposing workflows. Converts long-form
  content into posts, threads, and snippets. Activate for content repurposing.
metadata:
  version: 1.0.0
  category: content
---

# Content Engine Skill

## Content Hierarchy

```
Long-form article (2000+ words)
  → LinkedIn post (300 words)
  → X/Twitter thread (8-12 tweets)
  → Short newsletter section (150 words)
  → 3x single insight posts
```

## LinkedIn Post Template

```
[Hook — specific and bold claim, no preamble]

[3-5 lines of context or story]

[Key insight or lesson, formatted as list if > 3 items]

[Call to action — question or simple statement]

[3-5 hashtags, relevant not decorative]
```

## X/Twitter Thread Template

```
Tweet 1: Bold hook (must stand alone and be compelling without the thread)
Tweet 2-3: Context and setup
Tweet 4-8: Main points (one point per tweet)
Tweet 9-11: Evidence, examples, data
Tweet 12: Synthesis + call to action
Tweet 13: "Full article in profile bio" (if applicable)
```

## Repurposing Workflow

```
1. Input: article or transcript
2. Extract: 5 most shareable insights
3. For each insight:
   - LinkedIn micro-post (1 insight = 1 post)
   - Tweet (condensed to 280 chars)
   - Newsletter bullet point
4. Generate full thread from all insights
5. Schedule across platforms
```

## Voice Consistency Check

Before publishing, verify each repurposed piece:
- [ ] Same vocabulary level as source
- [ ] Consistent opinion (no contradictions)
- [ ] No AI-generic phrases
- [ ] Claim in opening is specific, not vague
- [ ] Platform-appropriate length and format
