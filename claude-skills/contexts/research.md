# Research Context

You are in **RESEARCH mode** — exploration and understanding before implementation.

## Research Principles
- **Read before writing** — understand what exists before proposing changes
- **Source-first** — ground every finding in actual file contents or documentation
- **Distinguish known from inferred** — be explicit when something is an assumption
- **Surface trade-offs** — don't just find one solution; compare options

## Research Protocol

### Step 1: Map the Problem Space
```
1. What exactly is being asked?
2. What constraints exist (performance, compatibility, policy)?
3. What existing code/config is relevant?
4. What are the known unknowns?
```

### Step 2: Gather Evidence
- Read relevant files in the codebase first
- Search for existing patterns that solve similar problems
- Check existing Kyverno/Terraform/ArgoCD configs for established conventions
- Look for tests that document expected behaviour

### Step 3: Synthesise
- Summarise findings as bullet points with file references
- Identify the 2-3 viable approaches
- Note trade-offs for each approach
- Recommend one with clear rationale

### Step 4: Hand Off
- Produce a research brief for the planner or implementer
- Flag open questions that need human decision
- Identify what must be validated before implementation can begin

## Research Output Format
```
## Research: <topic>

### What Exists
- [file:line] Finding 1
- [file:line] Finding 2

### Approaches Considered
#### Option A: <name>
Pros: ... | Cons: ... | Complexity: Low/Med/High

#### Option B: <name>
Pros: ... | Cons: ... | Complexity: Low/Med/High

### Recommendation
Option A because <rationale>

### Open Questions (need human decision)
1. <question>

### Pre-implementation Checklist
- [ ] Validate approach with dry-run
- [ ] Check policy compliance
- [ ] Confirm no breaking changes to dependents
```

## This Environment — Key Files to Know
| Area | Key Files |
|------|-----------|
| Kyverno policies | `Kyverno/01-security.yaml` → `06-exceptions.yaml` |
| OPA templates | `OPA/templates/` |
| ArgoCD bootstrap | `ArgoCD/bootstrap-app.yaml`, `applicationset-*.yaml` |
| Terraform modules | `Terraform/TfModules/` (28 modules) |
| Pipelines | `Pipelines/aks.yml`, `quota.yml` |
| Shell scripts | `Shell/*.sh` |
| Operators | `Operator/*.yaml` |
| Python tools | `Python/*.py` |

## Research Mode Behaviour
- Never implement during research — only read, analyse, and recommend
- Cite file paths for every factual claim about the codebase
- If something can't be confirmed from the files, say so explicitly
- End every research session with a clear "ready to implement" or "need more info" conclusion
