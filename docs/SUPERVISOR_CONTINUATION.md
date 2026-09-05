# Evidence-based supervisor continuation

Profile: `wellmanifest.autonomy/supervisor-continuation/v1`, version 1.0.0.
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
