---
name: zero-trust-architecture
description: >-
  Zero Trust architecture specialist for Azure, Kubernetes, and autonomous AI agents.
  Designs and implements never-trust-always-verify principles across identity, network,
  device, and workload layers. Covers Conditional Access, Entra ID, mTLS, service mesh,
  micro-segmentation, and agentic AI security (agent identity, least agency, blast radius,
  prompt injection, tool/MCP security, memory poisoning). Activate for Zero Trust design,
  review, gap assessment, or any Claude Code / MCP / agentic deployment security question.
domain: cybersecurity
subdomain: zero-trust-architecture
tags:
  - zero-trust
  - conditional-access
  - entra-id
  - mtls
  - service-mesh
  - micro-segmentation
  - aks
  - azure
  - agentic-ai
  - mcp
  - prompt-injection
  - least-agency
nist_csf: [PR.AC-01, PR.AC-03, PR.AC-05, ID.AM-03, DE.CM-01]
version: "2.0"
author: osavdi
license: Apache-2.0
---

# Zero Trust Architecture Skill

## When to Use

- Designing a Zero Trust network architecture for AKS or Azure
- Reviewing Conditional Access policies for Zero Trust compliance
- Implementing mTLS between microservices (Istio/Linkerd)
- Designing workload identity (UAMI, federated credentials)
- Conducting a Zero Trust maturity assessment
- Implementing micro-segmentation via Kubernetes NetworkPolicy
- Designing or reviewing an autonomous AI agent deployment (Claude Code, custom agents, MCP servers)
- Scoping tool/MCP access, agent credentials, or agent-to-agent trust boundaries
- Defending against prompt injection, tool poisoning, or memory/context poisoning

## Zero Trust Pillars (NIST SP 800-207)

| Pillar | Azure Control | Kubernetes Control |
|--------|--------------|-------------------|
| Identity | Entra ID + PIM + MFA | OIDC + RBAC + UAMI |
| Device | Intune + Defender for Endpoint | Node integrity (Secure Boot) |
| Network | Private Endpoints + Azure Firewall | NetworkPolicy + mTLS |
| Application | App Proxy + Conditional Access | Ingress mTLS + RBAC |
| Data | Purview + AIP + CMK | Encrypted Secrets (KMS) |
| Infrastructure | Defender for Cloud | Kyverno + Pod Security |

## Zero Trust Maturity Model Assessment

### Level 1 — Traditional
- VPN-based access, network perimeter trust
- Password-only auth
- No workload identity

### Level 2 — Advanced
- MFA enforced via Conditional Access
- Some role separation (RBAC exists)
- Basic network segmentation

### Level 3 — Optimal (Target)
- All access: identity-verified, device-compliant, context-aware
- Just-In-Time privileged access (PIM)
- Workload identity (UAMI/federated)
- mTLS between all services
- Default-deny NetworkPolicy everywhere
- Continuous verification (not just at login)

## Conditional Access — Zero Trust Baseline

```
Policy: Require MFA + Compliant Device for all apps
├── Users: All users (except break-glass accounts)
├── Cloud apps: All cloud apps
├── Conditions:
│   ├── Device platforms: Any
│   └── Locations: Any (including trusted)
└── Grant:
    ├── Require MFA
    └── Require device compliance (Intune)
    └── Operator: AND

Policy: Block legacy authentication
├── Users: All users
├── Cloud apps: All cloud apps
├── Conditions:
│   └── Client apps: Exchange ActiveSync, Other clients
└── Grant: Block
```

## mTLS in AKS (Istio Service Mesh)

```yaml
# Enforce mTLS for entire mesh
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
---
# AuthorizationPolicy — only allow specific service communication
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-api-to-db
  namespace: production
spec:
  selector:
    matchLabels:
      app: postgres
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/production/sa/api-service"]
      to:
        - operation:
            ports: ["5432"]
```

## Zero Trust Checklist for AKS

- [ ] AKS API server: private cluster only (no public endpoint)
- [ ] Workload identity: UAMI + federated credential for every pod needing Azure access
- [ ] RBAC: no `cluster-admin` for regular operations; use namespaced roles
- [ ] NetworkPolicy: default-deny all namespaces, explicit allow per flow
- [ ] mTLS: Istio/Linkerd in STRICT mode for production namespaces
- [ ] Node access: no direct SSH; use AKS command invoke or Bastion
- [ ] Secrets: all secrets in Key Vault via CSI driver (not K8s Secrets in etcd)
- [ ] Image provenance: Cosign signed + Kyverno verifyImages policy
- [ ] Pod Security: Restricted profile enforced cluster-wide
- [ ] Audit logging: kube-audit to Log Analytics, all auth events captured

## Verification

```bash
# Verify Conditional Access blocks legacy auth (test with IMAP)
# This should fail: telnet outlook.office365.com 143

# Verify mTLS between services
kubectl exec -it <pod> -- curl http://other-service:8080
# Should fail without mutual TLS certificate

# Verify no public AKS API server
az aks show -n <cluster> -g <rg> \
  --query 'apiServerAccessProfile.enablePrivateCluster'
```

---

# Zero Trust for Autonomous AI Agents

Source: Anthropic, "Zero Trust for AI Agents" (2026). Applies to any agentic deployment —
Claude Code, custom LLM agents, MCP servers/tools, and multi-agent systems.

## The Design Test: Impossible, Not Tedious

For every control, ask: **does this make the attack impossible, or just tedious?**
Friction-only controls (extra pivot hops, rate limits, non-standard ports, SMS-based MFA)
degrade badly against agentic attackers with unlimited patience and near-zero per-attempt
cost. Prefer controls that remove a capability (hardware-bound credentials, expiring tokens,
cryptographic identity, network paths that don't exist) over controls that merely throttle it.
Apply this test as a standing design-review question on every agent architecture.

## Core Agentic Concepts

- **Blast radius** — potential damage if an agent is compromised. Size security investment
  to the blast radius, not to perceived likelihood of compromise. Assume it will be tested.
- **Least agency** (OWASP) — extends least privilege to *what a tool can do, how often, and
  where*. A DB tool gets read-only queries; an email tool gets no send/delete; an API gets
  minimal CRUD. Deny-by-default always.
- **Confused deputy / unscoped privilege inheritance** — a high-privilege manager agent must
  never pass its full access context to a worker agent. Scope every delegation explicitly.

## Capability Tiers (Foundation → Enterprise → Advanced)

Foundation = minimum viable (small teams/initial deployments, floor raised by AI-accelerated
offense — friction-only controls no longer qualify). Enterprise = target for most
organizations at scale. Advanced = regulated/high-stakes environments. Each tier strengthens
the one below; don't replace, extend.

| Capability | Foundation | Enterprise | Advanced |
|---|---|---|---|
| Agent identity | Cryptographic per-instance ID | X.509 cert + lifecycle mgmt | HSM/TPM-backed + remote attestation |
| Service auth | Short-lived OAuth2 tokens (min expiry), no embedded creds | mTLS + cert pinning | Hardware-bound creds, attested issuance |
| Permissions | RBAC, deny-by-default | ABAC, context-aware | Continuous per-action authorization |
| Privilege scoping | Static least-privilege roles | Dynamic elevation, auto-revert | JIT/JEA, auto-expiring |
| Isolation | Identity-based (crypto identity per workload) + network segmentation as backstop | Sandboxed containers (gVisor) | Hardware isolation (SEV/TDX), microVMs |
| Logging | Full action logs w/ identity + context | Immutable, integrity-verified | Real-time SIEM streaming + correlation |
| Traceability | Request IDs across actions | Distributed tracing (OpenTelemetry) | Full provenance chain, replayable |
| Anomaly detection | Threshold alerts + automated first-pass triage | Statistical/tunable | ML behavioral analysis |
| Response | Alert + model-drafted triage context | Automated containment (session kill, revoke) | Orchestrated SOAR playbooks |
| Input validation | Schema + length limits | Known-pattern filtering | Multi-layer + constitutional classifiers + spotlighting |
| Output control | PII/secret pattern filtering | Semantic analysis | Human-in-loop for high-risk actions |
| Config integrity | Version-controlled | Signed configs, verified at deploy | Immutable images + attestation |
| Recovery | Documented rollback | Automated rollback + health checks | Self-healing, auto-remediation |

Static API keys, embedded credentials, and shared service-account secrets are **never**
acceptable, not even at Foundation — treat any you find as already-compromised.

## Threats to Check For (OWASP agentic top risks)

- **Prompt injection** — direct (input overrides) and indirect (payload hidden in web pages,
  emails, docs the agent processes). LLMs cannot reliably separate instructions from data;
  mitigate with spotlighting (delimit untrusted content) — cuts indirect injection success
  from >50% to <2%.
- **Tool/resource misuse** — tool poisoning (compromised MCP descriptors/metadata), rug-pull
  attacks (legitimate tool silently replaced), tool chaining (legitimate tools combined to
  exfiltrate data neither exposes alone), resource exhaustion (loop amplification/DoS billing).
- **Identity/privilege abuse** — unscoped privilege inheritance, confused deputy, memory-based
  privilege retention (cached creds reused across session boundaries).
- **Supply chain** — poisoned model weights/fine-tuning data (backdoors persist through RLHF),
  malicious MCP servers/packages, unmaintained FOSS dependencies. Use an AI-BOM (OWASP
  CycloneDX ML-BOM) and OpenSSF Scorecard in CI. Run/host MCP servers yourself on an
  immutable platform after verifying the code; sign it yourself.
- **Memory/context poisoning** — RAG poisoning, shared-context poisoning in multi-tenant
  systems, long-term memory drift (gradual, hard to detect as a single malicious change).

## Agent Implementation Workflow (8 phases)

1. **Identify requirements** — regulatory + operational + stakeholder alignment before building.
2. **Manage supply chain risk** — AI-BOM, OpenSSF Scorecard, dependency-tree redundancy audit,
   reachability analysis for patching, cryptographic signing at every stage, vendor assessment.
3. **Define agent boundaries** — unique cryptographic identity per instance; explicit
   approved/prohibited actions (enforced via permissions, not just told to the model);
   escalation triggers for high-value/sensitive actions; scope limits (Least Agency); compute
   blast radius and apply the impossible-vs-tedious test to the containment plan.
4. **Defend against prompt injection** — input isolation/spotlighting, constitutional
   classifiers, limit who/what can interact with the agent.
5. **Secure tool access** — tool allow-listing (deny unlisted), capability restrictions per
   tool, parameter validation (agent side AND tool side), sandboxed execution, human approval
   escalation for high-risk tool calls.
6. **Protect agent credentials** — short-lived IdP-issued tokens as baseline; hardware-bound
   for production; per-agent credential isolation (never shared); explicit trust boundaries
   between agents (verify identity before accepting delegated tasks); JIT access; ABAC.
7. **Safeguard agent memory** — session/user memory isolation, context integrity validation
   (hash + source attribution at every retrieval, not just storage), short TTL for
   unverified/external context, versioned memory for rollback.
8. **Measure what matters** — instrument **dwell time** (anomaly → human awareness) and
   **coverage** (% of alerts investigated) before anything else; target detection within an
   hour for critical systems; track behavioral drift against an established baseline.

## Defensive Operations at Agent Speed

- Automate the bookkeeping (evidence collection, enrichment, correlation, documentation);
  keep humans on the decisions (containment, disclosure, customer comms).
- Put a triage model at the front of the alert queue: start with one noisy/high-false-positive
  rule, read-only SIEM access, measure agreement with a human reviewer for two weeks before
  expanding.
- Map detection coverage against MITRE ATT&CK, prioritizing lateral movement and credential
  access (highest leverage for AI-accelerated attackers with compromised agent identities).
- Rehearse multi-incident tabletop exercises (five simultaneous, not one) and pre-authorize
  emergency change procedures (who can revoke a credential / isolate a service, how fast).
- Defensive agents (Agentic SOAR) get the *same* Zero Trust treatment: verified integrity,
  limited blast radius, clear human escalation paths, full logging — never blindly trusted.

## Claude Code Native Controls (map to the tiers above)

- Deny-by-default permissions requiring explicit approval for writes/execs (`settings.json`,
  the `ask` parameter, managed-only permission rules)
- `PreToolUse`/`PostToolUse` hooks for parameter validation and command-injection detection
- Sandboxed execution: OS-level filesystem/network isolation, isolated context windows for
  web content (prevents indirect prompt injection reaching the main context)
- OAuth 2.0 with automatic token refresh for MCP; API keys in OS credential store, never in
  config files (`apiKeyHelper` for external vault integration)
- Session-scoped tool permissions that expire when the session ends
- Version-controlled `settings.json` (permission configs + MCP allowlists reviewable/rollback-able)
- `session.id` + `user.account_uuid` + `organization.id` on all telemetry for attribution
- Configurable memory retention (`cleanupPeriodDays`) and checkpoint/rewind (`Esc+Esc`,
  `/rewind`) for rollback to known-good state

## Zero Trust Checklist for Agentic Deployments

- [ ] Every agent instance has a unique, cryptographically-rooted identity (not just a label)
- [ ] No static API keys / embedded credentials / shared service accounts anywhere
- [ ] Tool access is allow-listed and deny-by-default; unlisted tool calls are rejected
- [ ] Least Agency applied per tool (scope of action, frequency, target) — not just per role
- [ ] Untrusted input (web content, docs, emails) is isolated/spotlighted before reaching the agent
- [ ] MCP servers are self-hosted on immutable infra after code review, or from a vetted vendor
- [ ] Multi-agent delegation re-verifies identity/authorization at each hop (no confused deputy)
- [ ] Memory/context is isolated per session/user with integrity checks on retrieval
- [ ] High-risk actions (financial, data export, external comms) require human-in-the-loop approval
- [ ] Dwell time and alert coverage are instrumented and reviewed
- [ ] Rollback/recovery procedure is documented and tested, not just assumed
