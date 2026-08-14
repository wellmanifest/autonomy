# Ticket 009: Standardize practice-backed autonomous change control

- **ID**: ticket-009
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-14

## Goal and scope

Promote Autonomy 0.5 from the protected Deployment migration evidence. A
conforming autonomous change must commit its intent before implementation,
refresh a moved base without rewriting published history, inventory every
contract consumer and bind required checks to protected producer provenance.

## Acceptance criteria

- [x] AC-01: The ticket binds continuation authorization to exact protected
  `main@9960c12`, ten implementation files, three components and no runtime
  dependency.
- [x] AC-02: Manifest v3 requires an intent checkpoint before implementation,
  exact accepted-base refresh, full revalidation and successor PRs instead of
  autonomous history rewrite.
- [x] AC-03: Contract migration requires an exact version allowlist, complete
  consumer-surface inventory, pre-execution resolution and fail-closed unknown
  versions across local, image, Compose, hosted CI and validator surfaces.
- [x] AC-04: Required-check authority binds producer, event, repository, head
  and check name; ambiguous duplicate contexts fail closed while explicitly
  non-authoritative statuses cannot override a passing authoritative check.
- [x] AC-05: Checker and tests reject missing intent history, unsafe base
  refresh, partial consumer migration and ambiguous check provenance.
- [x] AC-06: Spec, schema, profile, example, architecture and logic flow align
  at stable version 0.5.0 and pass all deterministic conformance gates.

## Risks

- This is a deliberate manifest v3 contract boundary; v2 adopters must migrate
  explicitly and cannot silently claim 0.5 conformance.
- Provider-specific API fallback remains implementation guidance; the
  normative rule is authoritative evidence and bounded fail-closed recovery.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
