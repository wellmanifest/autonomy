# AUTONOMY-BOUNDARY-001

## Risk

Self-validation, shared trigger/watchdog principals, duplicated registry
configuration, cross-repository aggregate gating, stale-head approval, native
queued auto-merge, direct default-branch push, or an unprotected publication
gate can let a candidate bypass a required authority boundary.

## Detection

The checker verifies authority ceilings, trigger/watchdog independence,
four-dimensional separation of the implementer, validator, and publisher,
protected registry bindings, per-repository outcome isolation, protected
exact-head/current-base gates, required checks, same-repository PRs, explicit
App merge, native auto-merge disablement, read-back, and branch cleanup.

## Remediation

Revoke the candidate's publication path, separate principals, credentials and
workspaces, restore the protected registry projection, and issue new independent
validation for the exact current head under the protected profile. Never reuse
a stale review, aggregate success, or generic bot approval.

## Verification

Fetch the current base and PR head through the protected controller, reproduce
all deterministic checks from a fresh validator checkout, verify the trusted
App or attestation identity, confirm native auto-merge remains disabled, and
read back the merged default-branch SHA. Verify unrelated repository failures
cannot alter the target repository's gate result.
