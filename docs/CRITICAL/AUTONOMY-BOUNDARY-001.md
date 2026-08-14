# AUTONOMY-BOUNDARY-001

## Risk

Self-validation, shared principals or credentials, stale-head approval, direct
default-branch push, or an unprotected publication gate can let a candidate
approve or merge itself.

## Detection

The checker verifies authority ceilings, four-dimensional separation of the
implementer, validator, and publisher, protected exact-head/current-base gates,
required checks and bindings, same-repository PRs, auto-merge policy, read-back,
and branch cleanup.

## Remediation

Revoke the candidate's publication path, separate principals, credentials and
workspaces, and issue new independent validation for the exact current head
under the protected profile. Never reuse a stale review or generic bot approval.

## Verification

Fetch the current base and PR head through the protected controller, reproduce
all deterministic checks from a fresh validator checkout, verify the trusted
App or attestation identity, and read back the merged default-branch SHA.
