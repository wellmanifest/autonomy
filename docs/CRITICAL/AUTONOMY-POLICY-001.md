# AUTONOMY-POLICY-001

## Risk

An inactive or malformed grant, missing exclusion, unsafe continuation rule,
non-durable queue, stale or manually manufactured liveness proof, or
mutable/unpinned runtime profile could authorize work beyond the issuer's
intended standing delegation while appearing autonomous.

## Detection

The checker compares grant time and scope, mandatory excluded effects, risk
ceiling, durable delivery and idempotency policy, automatic canary receipts,
stop policy, lifecycle receipts, and selected profile bytes with the manifest's
immutable bindings.

## Remediation

Stop mutation. Restore the mandatory policy, pin the protected profile digest,
restore an independently watched automatic trigger, or obtain a new externally
issued grant. The agent fleet must not repair, renew, widen, or reactivate its
own authority. A manual dispatch may diagnose recovery but cannot restore a
liveness claim.

## Verification

Re-run schema and semantic conformance, then evaluate the grant at the intended
operation time from the protected controller. Confirm that revocation and the
kill switch still stop mutation, then require a fresh non-manual protected
canary receipt set before claiming operational conformance.
