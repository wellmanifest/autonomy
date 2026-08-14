---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-007
---
# Participant: codex (AI agent)

## Understanding

Autonomy 0.3 correctly required isolated runtime sources but its first Subactor
deployment only checked that a clean development checkout was an ancestor of
protected main. Editing a systemd unit on a candidate branch changed the live
linked unit before merge and stopped the next timer cycle. The fail-closed
boundary prevented effects, while recovery required copying the supervisor
outside the repository and loading the old protected runtime from a detached
exact-SHA worktree. The standard must make that distinction explicit.

## Execution plan

1. Freeze the zero-effect linked-unit failure and isolated recovery evidence.
2. Define exact-runtime pins and supervisor-source separation.
3. Define quiesced rollout/rollback ordering and automatic post-rollout proof.
4. Bind the Subactor profile and promote 0.4.0 through protected publication.

## Actual changes

- Initialized the bounded ticket and recorded SESSION_EXECUTION_AUTHORIZATION
  from the request to execute this work.
- Promoted the standard, selected profile and pinned examples to 0.4.0.
- Required exact revision or artifact-digest matching before effect-capable code
  loads; protected-history ancestry alone no longer counts as the pin.
- Prohibited supervisor units, executable paths and pin configuration from
  resolving through candidate or concurrently mutable development workspaces.
- Defined prepare, validate, quiesce, switch, reload, resume and rollback order,
  including fail-stopped behavior and a fresh automatic post-rollout proof.
- Bound the Subactor profile to its detached runtime worktree, exact pin,
  deployment script, copied service unit and quiesced rollback restrictions.
- Recorded the `18:47:10Z` fail-closed linked-unit incident, protected
  `814e257` recovery, autonomous PR #17 publication and the automatic
  `88953aa` post-rollout cycle at `18:57:40Z`.
- Passed all declared deterministic, DSL, lint and governance gates; protected
  publication completed on the same exact head.
- Observed Validator run `31831392755`, exact-head App review `4940380603`,
  explicit App merge `164a94e25550894e3c7ed468be316ab985219eff`,
  protected-main read-back and source branch cleanup.

## Blockers

- None. The bounded 0.4 standard and protected publication are complete.
- New authority remains required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
