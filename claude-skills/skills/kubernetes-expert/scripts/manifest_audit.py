#!/usr/bin/env python3
"""Audit a Kubernetes manifest YAML for security and production-readiness issues."""
import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

SEVERITY = {"critical": 0, "high": 1, "medium": 2, "low": 3}

CHECKS = [
    # (severity, path_fn, message)
    ("critical", lambda c: not c.get("securityContext", {}).get("runAsNonRoot"), "runAsNonRoot not set to true"),
    ("critical", lambda c: c.get("securityContext", {}).get("allowPrivilegeEscalation", True), "allowPrivilegeEscalation not set to false"),
    ("critical", lambda c: "resources" not in c, "No resource requests/limits defined"),
    ("high",     lambda c: not c.get("securityContext", {}).get("readOnlyRootFilesystem"), "readOnlyRootFilesystem not true"),
    ("high",     lambda c: not c.get("livenessProbe"), "No livenessProbe defined"),
    ("high",     lambda c: not c.get("readinessProbe"), "No readinessProbe defined"),
    ("high",     lambda c: c.get("image", "").endswith(":latest"), "Image uses :latest tag"),
    ("medium",   lambda c: "ALL" not in c.get("securityContext", {}).get("capabilities", {}).get("drop", []), "capabilities.drop ALL not set"),
    ("medium",   lambda c: c.get("securityContext", {}).get("privileged"), "Container running as privileged"),
]

HOST_CHECKS = [
    ("critical", lambda s: s.get("hostNetwork"), "hostNetwork: true is set"),
    ("critical", lambda s: s.get("hostPID"), "hostPID: true is set"),
    ("critical", lambda s: s.get("hostIPC"), "hostIPC: true is set"),
]


def audit_manifest(doc: dict) -> list[dict]:
    findings = []
    kind = doc.get("kind", "Unknown")
    name = doc.get("metadata", {}).get("name", "unknown")
    ref = f"{kind}/{name}"

    # Dig to pod spec
    spec = doc.get("spec", {})
    if kind in ("Deployment", "DaemonSet", "StatefulSet", "Job", "CronJob"):
        template = spec.get("template", spec)
        pod_spec = template.get("spec", {})
    elif kind == "Pod":
        pod_spec = spec
    else:
        return findings

    # Host-level checks
    for sev, check_fn, msg in HOST_CHECKS:
        if check_fn(pod_spec):
            findings.append({"severity": sev, "resource": ref, "issue": msg})

    # Container checks
    for container in pod_spec.get("containers", []) + pod_spec.get("initContainers", []):
        cname = container.get("name", "unnamed")
        for sev, check_fn, msg in CHECKS:
            if check_fn(container):
                findings.append({"severity": sev, "resource": f"{ref}/{cname}", "issue": msg})

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to YAML manifest file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--min-severity", choices=SEVERITY.keys(), default="low")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"ERROR: File not found: {args.manifest}", file=sys.stderr)
        return 1

    all_findings: list[dict] = []
    docs = list(yaml.safe_load_all(args.manifest.read_text()))

    for doc in docs:
        if doc:
            all_findings.extend(audit_manifest(doc))

    # Filter by severity
    min_sev = SEVERITY[args.min_severity]
    filtered = [f for f in all_findings if SEVERITY[f["severity"]] <= min_sev]
    filtered.sort(key=lambda f: SEVERITY[f["severity"]])

    if args.json:
        print(json.dumps(filtered, indent=2))
    else:
        if not filtered:
            print("✅ No issues found.")
            return 0
        print(f"{'SEVERITY':<10} {'RESOURCE':<50} {'ISSUE'}")
        print("-" * 100)
        icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
        for f in filtered:
            icon = icons.get(f["severity"], "")
            print(f"{icon} {f['severity']:<9} {f['resource']:<50} {f['issue']}")
        print(f"\nTotal: {len(filtered)} issue(s)")

    return 1 if any(SEVERITY[f["severity"]] <= SEVERITY["high"] for f in filtered) else 0


if __name__ == "__main__":
    sys.exit(main())
