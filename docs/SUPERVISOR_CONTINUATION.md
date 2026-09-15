# Evidence-based supervisor continuation

Profile: `wellmanifest.autonomy/supervisor-continuation/v1`, version 1.1.0.
This additive profile preserves the autonomy manifest v6 and grants no authority.
Its normative requirement catalog is `profiles/supervisor-continuation.v1.json`.

A supervisor resolves independent validation capability and the existing
subject-bound authority before deciding that a human must review a PR.
An available Validator App is not authorization. A valid standing mandate is
not independent approval. CI success is not proof of publication.

The protected execution path freezes repository, PR, head and base, checks
trusted CI, acquires a durable publication claim, invokes the independent
validator, reads the resulting review and merge, and verifies the exact effect.
Pending CI waits; failed CI enters bounded repair. An already merged subject
is reconciled from authoritative evidence without another review or merge.
Human input is required for a real authority boundary, not merely because the
operation writes to GitHub. Missing capability is an explicit system blocker.

Repeated polling must preserve a semantic fingerprint when only timestamps,
heartbeat counters, elapsed durations or model narration change. New evidence,
a due bounded follow-up or a periodic review may trigger assessment. A live
service, a plan, an exit code or an increasing cycle count is not effect progress.

History presents recorded goal, subject, operation, actor, rationale, timestamps
and evidence references. Missing fields remain unknown. Truncation is marked.
Old plans are distinguished from recent activity. A pinned immutable deployment
is identified by its release evidence; detached HEAD alone is not development.

## Human assistance protocol

Human help is a typed boundary, not an informal prompt. Use the
`wellmanifest.autonomy/human-assistance/v1` request when the risk ceiling,
excluded effects, ownership or protected evidence prevents autonomous
continuation. The request is bound to one repository, ticket, head SHA, base
SHA and selected continuation profile:

```json
{
  "kind": "human-assistance-request",
  "requestId": "human-assist/example-1",
  "requestDigest": "sha256:<64 lowercase hex>",
  "profile": "wellmanifest.autonomy/human-assistance/v1",
  "subject": {
    "repository": "example/example-api",
    "ticket": "ticket-123",
    "headSha": "<40 lowercase hex>",
    "baseSha": "<40 lowercase hex>",
    "profile": "wellmanifest.autonomy/supervisor-continuation/v1"
  },
  "riskTier": "high",
  "reason": "the requested effect is outside the standing grant",
  "question": "Approve the one bounded operation?",
  "requestedDecision": "approve",
  "issuedAt": "2026-09-15T08:00:00Z",
  "expiresAt": "2026-09-15T09:00:00Z",
  "status": "pending",
  "effectsFrozen": true
}
```

Validate it with `python3 src/continuation_check.py human-request request.json`.
While it is pending, the only conforming continuation is `wait` (or protected
observation/reconciliation); edit, push, approval, merge and secret access are
frozen. A response must carry the same request digest and subject, a response
digest, and an authenticated `human` or `external-authority` actor. Validate a
response with `python3 src/continuation_check.py human-response response.json`.
An LLM answer, bot comment or Markdown approval is never consent. An expired
request is blocked and must be renewed by the external authority as a new
request; it is not a successful continuation.

When the active grant already provides a verified independent validator, use
that path instead of escalating to a human. The checker rejects a
human-only loop in that case (`SC-001`/`SC-012`).

## Conformance and adoption

Run `python3 src/continuation_check.py decision evidence.json` for protected
normalized decision facts, or `adoption` for a single consumer. `fleet` accepts
`expected` repository IDs and `records`, rejecting missing, duplicate and
unexpected consumers. These are shape/semantic checks on supplied facts, not
cryptographic verification: a protected adapter must authenticate receipts and
revisions before producing the verified fields. Never trust candidate-authored
flags as approval or runtime proof.

Every applicable consumer records the exact published standard revision and
profile digest, a passing executable check and its receipt reference. Effect-
capable consumers additionally need a fresh verified runtime readback. A
repository without a control plane may be assessed not applicable with an
explicit reason and immutable inspection reference. Unknown is not exempt.
A fleet declaration, a copied document or a queued rollout is not full adoption.
