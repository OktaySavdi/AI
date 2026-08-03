# Zero Trust for Agentic Systems — Always-Apply Rules

Source: Anthropic, "Zero Trust for AI Agents" (2026). These rules apply whenever work touches
an autonomous agent, LLM-backed automation, MCP server/tool, CI/CD agent, or Kubernetes
operator that acts without a human approving each step. Extends `common/security.md`.
Full reference and tiered capability tables: skill `zero-trust-architecture`.

## The Standing Design Test

Before approving any control, ask: **does this make the attack impossible, or just tedious?**
Reject friction-only mitigations (rate limits alone, obscurity, SMS MFA) as the *sole* control
for anything agent-facing. Prefer: hardware/crypto-bound identity, expiring tokens, and network
paths that don't exist over paths that are merely inconvenient.

## Non-Negotiables for Any Agent/Automation Work

1. **No static credentials.** No API keys, passwords, or service-account secrets hardcoded,
   committed, or reused across agent instances — flag as CRITICAL immediately, same severity
   as a hardcoded secret in `common/security.md`. Short-lived, identity-provider-issued tokens
   are the floor, even for "Foundation" tier / small scripts.
2. **Unique identity per agent instance.** Every agent, cron job, operator, or bot gets its own
   cryptographically distinguishable identity — never a shared credential across multiple
   agents or copies of the same agent.
3. **Least Agency, not just least privilege.** When scoping a tool/API/DB account for an agent,
   constrain not just *what* it can access but *how much* and *how often*: read-only unless
   write is proven necessary, narrow CRUD, rate/spend limits with circuit breakers.
4. **Deny-by-default tool access.** Agents/automations get an explicit allow-list of
   tools/actions. Unlisted calls are rejected, not merely logged.
5. **Untrusted input is isolated.** Any content an agent ingests from outside the direct
   operator (web pages, emails, tickets, PR descriptions, scraped docs) is treated as
   potentially adversarial (prompt injection risk) — delimit/spotlight it, never let it
   silently alter agent instructions or trigger tool calls without a boundary check.
6. **Blast radius is computed, not assumed.** Before granting an agent access to a system,
   state explicitly: what's the worst case if this agent/credential is fully compromised?
   If the answer is "significant," scope down before proceeding, don't rely on monitoring
   to catch it after the fact.
7. **MCP/tool supply chain gets the same rigor as code dependencies.** Prefer self-hosted,
   code-reviewed, signed MCP servers over unvetted third-party ones. Check for tool
   poisoning risk (can tool descriptions/metadata be silently changed post-install?).
8. **High-risk actions require human-in-the-loop.** Financial transactions, data exports,
   external communications (email/Slack/PR merges to protected branches), and irreversible
   infra changes triggered by an agent require explicit human approval — this mirrors the
   "Executing actions with care" guidance already in scope, extended to agent-initiated
   (not just Claude-initiated) actions.
9. **Log for attribution.** Every agent action must be traceable to a specific agent identity,
   triggering event, and authorization — request/session IDs propagated through the full
   action chain.

## When Reviewing Agentic/Automation Code or Infra

Apply this checklist in addition to `common/security.md`:
- [ ] Agent/bot credentials: short-lived, unique per instance, never embedded in code/config
- [ ] Tool/API access: allow-listed, least-agency scoped, deny-by-default
- [ ] External/untrusted input: isolated or validated before it can influence agent behavior
- [ ] Multi-agent delegation: each hop re-verifies identity/authorization (no confused deputy —
      a high-privilege agent must not blindly execute instructions relayed by a low-privilege one)
- [ ] Memory/context stores: isolated per session/tenant, with integrity checks on retrieval
- [ ] Rollback/kill-switch exists and is documented for any agent with write access

## Escalate Immediately (CRITICAL) If Found

- Shared or static credentials used by more than one agent instance
- An agent with unscoped/admin-level access to a system it only needs narrow access to
- Prompt/instruction content from an untrusted source (web, email, ticket) able to change
  agent behavior without any isolation or validation layer
- No human-approval gate on an agent capable of financial, data-export, or production-write actions

These mirror the "Incident Response Trigger" list in `common/security.md` — treat agentic
Zero Trust violations with the same urgency as a wildcard RBAC role or a committed secret.
