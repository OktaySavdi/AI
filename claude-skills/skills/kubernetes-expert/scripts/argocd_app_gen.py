#!/usr/bin/env python3
"""Generate ArgoCD ApplicationSet YAML from a simple JSON/YAML config."""
import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def build_applicationset(cfg: dict) -> dict:
    name = cfg["name"]
    repo = cfg["repoURL"]
    revision = cfg.get("targetRevision", "main")
    path_template = cfg.get("pathTemplate", "clusters/{{name}}")
    namespace = cfg.get("namespace", "argocd")
    project = cfg.get("project", "default")
    cluster_label = cfg.get("clusterLabel", {})

    appset = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "ApplicationSet",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "spec": {
            "generators": [
                {
                    "clusters": {
                        "selector": {
                            "matchLabels": cluster_label
                        }
                    }
                }
            ],
            "template": {
                "metadata": {
                    "name": f"{{{{name}}}}-{name}",
                },
                "spec": {
                    "project": project,
                    "source": {
                        "repoURL": repo,
                        "targetRevision": revision,
                        "path": path_template,
                    },
                    "destination": {
                        "server": "{{server}}",
                        "namespace": cfg.get("destinationNamespace", name),
                    },
                    "syncPolicy": {
                        "automated": {
                            "prune": True,
                            "selfHeal": True,
                        },
                        "syncOptions": [
                            "CreateNamespace=true",
                            "ServerSideApply=true",
                        ],
                    },
                },
            },
        },
    }
    return appset


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="JSON config file for ApplicationSet")
    parser.add_argument("--out", type=Path, help="Output file (default: stdout)")
    args = parser.parse_args()

    if not args.config.exists():
        print(f"ERROR: {args.config} not found", file=sys.stderr)
        return 1

    cfg = json.loads(args.config.read_text())
    doc = build_applicationset(cfg)
    output = "---\n" + yaml.dump(doc, default_flow_style=False, sort_keys=False)

    if args.out:
        args.out.write_text(output)
        print(f"Written to {args.out}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
