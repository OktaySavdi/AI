#!/usr/bin/env bash
# Session start context loader
# Displays key reminders and active context at the start of each Claude session

set -uo pipefail

echo "" >&2
echo "╔══════════════════════════════════════════════════════════╗" >&2
echo "║         IT Infrastructure Claude Code Session            ║" >&2
echo "╠══════════════════════════════════════════════════════════╣" >&2
echo "║ Model: sonnet (default) │ /model opus for deep reasoning ║" >&2
echo "║ Token: MAX_THINKING=10k │ Autocompact at 50%             ║" >&2
echo "╠══════════════════════════════════════════════════════════╣" >&2
echo "║ CONTEXTS  /dev → build │ /review → audit │ /research     ║" >&2
echo "║ AGENTS    planner · architect · k8s-reviewer             ║" >&2
echo "║           policy-engineer · terraform-engineer           ║" >&2
echo "║           security-reviewer · incident-responder         ║" >&2
echo "╠══════════════════════════════════════════════════════════╣" >&2
echo "║ QUICK CMDS                                               ║" >&2
echo "║  /plan · /tdd · /code-review · /build-fix               ║" >&2
echo "║  /k8s-review · /security-audit · /tf-review             ║" >&2
echo "║  /kyverno-policy · /pipeline-generate · /helm-create     ║" >&2
echo "╠══════════════════════════════════════════════════════════╣" >&2
echo "║ RULES     No :latest │ Always securityContext            ║" >&2
echo "║           No secrets in ConfigMap │ CEL: no quoted keys  ║" >&2
echo "╚══════════════════════════════════════════════════════════╝" >&2
echo "" >&2

exit 0
