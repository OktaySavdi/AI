---
name: "market-research"
description: >
  Source-attributed market, competitor, and investor research. Structured
  frameworks for market sizing and competitive analysis. Activate for research.
metadata:
  version: 1.0.0
  category: business
---

# Market Research Skill

## Research Protocol

Every claim must have a source. Format:

```
[Claim] (Source: [URL or publication, Year])
```

If no source available: state "unverified estimate" and flag for manual research.

## Market Sizing — TAM/SAM/SOM

```
TAM (Total Addressable Market)
  → All potential buyers of this category globally
  → Source: industry reports (Gartner, IDC, Statista)

SAM (Serviceable Addressable Market)
  → Buyers your business model can realistically reach
  → = TAM × (geographic fit × segment fit)

SOM (Serviceable Obtainable Market)
  → What you can win in 3-5 years given competition
  → = SAM × realistic market share estimate
```

## Competitive Analysis Template

```markdown
## Competitor: [Name]

**Category**: Direct / Indirect / Substitute

**Positioning**: [Their stated value prop]

**Price**: [Pricing model and range]

**Strengths**:
- [Evidence-based]
- [Evidence-based]

**Weaknesses**:
- [Evidence-based]
- [Evidence-based]

**Customer Sentiment**: [G2/Trustpilot/Reddit themes]

**Funding**: $X (Series X, Year) (Source: Crunchbase)
```

## Research Sources

| Type | Sources |
|---|---|
| Market size | Gartner, IDC, Statista, McKinsey Global Institute |
| Company data | Crunchbase, LinkedIn, PitchBook |
| Customer sentiment | G2, Trustpilot, Reddit, App Store reviews |
| Funding rounds | Crunchbase, TechCrunch, SEC EDGAR |
| Industry trends | CB Insights, a16z blog, First Round Review |

## Output Format

Deliver as:
1. Executive summary (1 page)
2. Market sizing model (spreadsheet-ready numbers)
3. Competitor matrix (table)
4. Source list (all URLs with access date)
