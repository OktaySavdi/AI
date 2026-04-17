---
name: "configure-ecc"
description: >
  Interactive ECC installation wizard. Guides setup of ~/.claude/ directory,
  settings.json, hooks, and language-specific rules. Activate for ECC setup.
metadata:
  version: 1.0.0
  category: meta
---

# Configure ECC Skill

## Installation Wizard

When `/configure-ecc` is invoked, walk through these steps:

### Step 1: Detect Environment

```bash
# OS detection
uname -s  # Darwin = macOS, Linux = Linux

# Claude Code version
claude --version

# Existing ~/.claude/ contents
ls ~/.claude/ 2>/dev/null || echo "No ~/.claude/ directory"
```

### Step 2: Settings Configuration

```bash
cat > ~/.claude/settings.json << 'EOF'
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
EOF
```

### Step 3: Language Rules Selection

Ask user which languages they use:
- [ ] Python → enable `rules/python/`
- [ ] Go → enable `rules/golang/`
- [ ] TypeScript → enable `rules/typescript/`
- [ ] Swift → enable `rules/swift/`
- [ ] PHP → enable `rules/php/`

### Step 4: Hook Configuration

Ask user which hooks to enable:
- [ ] `secret-detector` — blocks credential patterns (recommended)
- [ ] `latest-tag-check` — blocks `:latest` image tags (recommended)
- [ ] `k8s-dryrun-reminder` — kubectl dry-run prompts
- [ ] `terraform-fmt-reminder` — terraform fmt prompts
- [ ] `session-start` — context banner

### Step 5: Verification

```bash
echo "=== Verification ===" && \
ls ~/.claude/agents/ | wc -l && \
ls ~/.claude/commands/ | wc -l && \
ls ~/.claude/skills/ | wc -l && \
echo "Setup complete."
```

## Post-Setup

Run `/harness-audit` to verify the full configuration is correct.
