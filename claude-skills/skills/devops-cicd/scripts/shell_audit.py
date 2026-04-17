#!/usr/bin/env python3
"""Scan shell scripts in a directory for common security and quality issues."""
import argparse
import re
import sys
from pathlib import Path

CHECKS = [
    # (severity, pattern, message)
    ("critical", re.compile(r"curl\s+.*\|\s*(?:bash|sh)\b"),          "Piping curl to bash — remote code execution risk"),
    ("critical", re.compile(r"rm\s+-rf\s+/(?:\s|$)"),                 "rm -rf / — destructive command"),
    ("critical", re.compile(r"eval\s+[\"\$]"),                         "eval with variable — injection risk"),
    ("high",     re.compile(r"password\s*=\s*['\"][^'\"${}]{4,}"),    "Hardcoded password in script"),
    ("high",     re.compile(r"TOKEN\s*=\s*['\"][A-Za-z0-9_\-]{20,}"), "Possible hardcoded token"),
    ("medium",   re.compile(r"^(?!.*set -[e]).*\bsh\b|\bbash\b", re.M), "Script may lack set -e"),
    ("medium",   re.compile(r"\bsudo\b"),                               "sudo usage — requires justification"),
    ("low",      re.compile(r"\becho\b.*\$\w+"),                       "echo with variable — potential secret exposure"),
]

BEST_PRACTICE_CHECKS = [
    ("has_set_euo",   re.compile(r"set -[a-z]*e[a-z]*u[a-z]*o[a-z]*\s+pipefail|set -euo pipefail"), "Missing 'set -euo pipefail'"),
    ("has_trap",      re.compile(r"\btrap\b"),                                                          "No trap for cleanup/error handling"),
    ("has_shebang",   re.compile(r"^#!"),                                                               "Missing shebang line"),
]


def check_script(path: Path) -> list[dict]:
    findings = []
    content = path.read_text(errors="replace")
    lines = content.splitlines()

    # Line-by-line checks
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for sev, pattern, msg in CHECKS:
            if pattern.search(line):
                findings.append({
                    "severity": sev,
                    "ref": f"{path.name}:{i}",
                    "issue": msg,
                    "line": stripped[:100],
                })

    # Whole-file best practices
    for key, pattern, msg in BEST_PRACTICE_CHECKS:
        if not pattern.search(content):
            findings.append({
                "severity": "medium",
                "ref": f"{path.name}:—",
                "issue": msg,
                "line": "",
            })

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Shell script file or directory")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    scripts = list(args.path.rglob("*.sh")) if args.path.is_dir() else [args.path]
    if not scripts:
        print("No .sh files found.")
        return 0

    all_findings: list[dict] = []
    for s in scripts:
        all_findings.extend(check_script(s))

    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_findings.sort(key=lambda x: sev_order.get(x["severity"], 9))

    if args.json:
        import json
        print(json.dumps(all_findings, indent=2))
        return 0

    if not all_findings:
        print("✅ No issues found.")
        return 0

    icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
    for f in all_findings:
        icon = icons.get(f["severity"], "")
        print(f"{icon} [{f['severity'].upper()}] {f['ref']}")
        print(f"   {f['issue']}")
        if f["line"]:
            print(f"   → {f['line']}")
        print()

    print(f"Total: {len(all_findings)} issue(s) across {len(scripts)} script(s)")
    return 1 if any(f["severity"] in ("critical", "high") for f in all_findings) else 0


if __name__ == "__main__":
    sys.exit(main())
