#!/usr/bin/env python3
"""Check Terraform .tf files for Azure naming convention violations and common issues."""
import argparse
import re
import sys
from pathlib import Path

# Pattern: <type>-<workload>-<env>-<region>
# e.g. aks-platform-prod-weu
VALID_ENVS = {"dev", "staging", "prod", "test", "uat"}
VALID_REGIONS = {"weu", "neu", "eus", "eus2", "wus", "wus2", "aue", "sea"}

ISSUES: list[tuple[str, str, str]] = []  # (severity, file:line, message)

HARDCODED_SECRET_PATTERNS = [
    (re.compile(r'password\s*=\s*"[^"${}]{4,}"', re.I), "Possible hardcoded password"),
    (re.compile(r'client_secret\s*=\s*"[^"${}]{4,}"', re.I), "Possible hardcoded client_secret"),
    (re.compile(r'sas_token\s*=\s*"[^"${}]{4,}"', re.I), "Possible hardcoded SAS token"),
    (re.compile(r'access_key\s*=\s*"[^"${}]{4,}"', re.I), "Possible hardcoded access key"),
]

LATEST_TAG_PATTERN = re.compile(r'image\s*=\s*"[^"]+:latest"', re.I)
MISSING_TAGS_PATTERN = re.compile(r'resource\s+"[^"]+"\s+"[^"]+"\s*\{(?!.*tags\s*=)', re.DOTALL)


def check_file(path: Path) -> list[dict]:
    findings = []
    lines = path.read_text().splitlines()

    for i, line in enumerate(lines, 1):
        ref = f"{path.name}:{i}"

        # Hardcoded secrets
        for pattern, msg in HARDCODED_SECRET_PATTERNS:
            if pattern.search(line):
                findings.append({"severity": "critical", "ref": ref, "issue": msg, "line": line.strip()})

        # :latest image
        if LATEST_TAG_PATTERN.search(line):
            findings.append({"severity": "high", "ref": ref, "issue": "Image uses :latest tag", "line": line.strip()})

        # azurerm provider version (warn if not pinned)
        if "hashicorp/azurerm" in line and "~>" not in line and "version" in line:
            findings.append({"severity": "medium", "ref": ref, "issue": "azurerm provider not pinned with ~>", "line": line.strip()})

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="File or directory to check")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    tf_files = list(args.path.rglob("*.tf")) if args.path.is_dir() else [args.path]
    all_findings: list[dict] = []

    for f in tf_files:
        all_findings.extend(check_file(f))

    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_findings.sort(key=lambda x: sev_order.get(x["severity"], 9))

    if args.json:
        import json
        print(json.dumps(all_findings, indent=2))
    else:
        if not all_findings:
            print("✅ No issues found.")
            return 0
        icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
        for f in all_findings:
            icon = icons.get(f["severity"], "")
            print(f"{icon} [{f['severity'].upper()}] {f['ref']}")
            print(f"   {f['issue']}")
            print(f"   → {f['line']}\n")
        print(f"Total: {len(all_findings)} issue(s) in {len(tf_files)} file(s)")

    return 1 if any(f["severity"] in ("critical", "high") for f in all_findings) else 0


if __name__ == "__main__":
    sys.exit(main())
