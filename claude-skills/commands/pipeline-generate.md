Using the devops-cicd skill, generate an Azure DevOps YAML pipeline for: $ARGUMENTS

Include:
1. Trigger on main branch
2. Variable group reference (secrets from Key Vault)
3. Build stage: Docker build+push to ACR with BuildId tag
4. Deploy stage with `environment:` approval gate (production)
5. Rollback step on failure
6. Reusable template reference pattern (extends:)
7. Teams/email notification on failure

Security rules:
- No secrets in YAML — variable group only
- Pin all task versions (e.g., Docker@2, KubernetesManifest@1)
- Use service connections, not PATs

Output complete pipeline YAML.
