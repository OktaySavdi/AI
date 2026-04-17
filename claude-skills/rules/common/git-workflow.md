# Git Workflow Rules

## Commit Format
Use Conventional Commits specification:
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types
| Type | When to Use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `chore` | Build, config, tooling changes |
| `docs` | Documentation only |
| `refactor` | Code restructure without behaviour change |
| `test` | Adding or fixing tests |
| `perf` | Performance improvement |
| `ci` | CI/CD pipeline changes |
| `revert` | Revert a previous commit |

### Scopes (this workspace)
`kyverno` · `opa` · `argocd` · `terraform` · `pipeline` · `helm` · `shell` ·
`operator` · `ansible` · `python` · `docs` · `k8s`

### Examples
```
feat(kyverno): add CEL policy for image registry restriction
fix(terraform): correct AKS node pool VM size variable type
chore(pipeline): pin AzureCLI task to version 2.0.0
docs(argocd): update bootstrap README with App-of-Apps pattern
```

### Rules
- Subject line: max 72 characters, imperative mood ("add" not "adds" / "added")
- No period at end of subject
- Body explains *why*, not *what* (the diff shows what)
- Breaking changes noted in footer: `BREAKING CHANGE: <description>`

## Branch Strategy
```
main          ← production-ready, protected
dev           ← integration branch (PRs merge here first)
feature/<name>  ← new work
fix/<name>      ← bug fixes
chore/<name>    ← maintenance
```

## Pull Request Rules
- PR title follows Conventional Commit format
- PR description includes: what, why, testing notes, rollback plan
- At least one reviewer approval required before merge
- All CI checks must pass (lint, test, dry-run)
- Squash merge preferred for feature branches; merge commit for releases

## Pre-commit Checks (run before every commit)
```bash
# Kubernetes manifests
kubectl apply --dry-run=client -f <file>

# Terraform
terraform fmt && terraform validate

# Shell scripts
shellcheck <script>

# Python
black --check . && pylint <module>
```

## Tagging and Releases
- Semantic versioning: `vMAJOR.MINOR.PATCH`
- Tag on `main` only
- CHANGELOG updated before tagging

## What NOT to Commit
- `.env` files with real credentials
- `terraform.tfstate` or `terraform.tfstate.backup`
- `*.pem`, `*.key`, `*.p12` certificate files
- Editor configs (`.idea/`, `.vscode/`) unless team-standardised
- Binary artifacts — use artifact registry instead
