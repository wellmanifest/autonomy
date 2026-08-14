# AUTONOMY-POLICY-001

## Risk

An inactive or malformed grant, missing exclusion, unsafe continuation rule,
unbounded queue, or mutable/unpinned runtime profile could authorize work beyond
the issuer's intended standing delegation.

## Detection

The checker compares grant time and scope, mandatory excluded effects, risk
ceiling, queue and stop policy, lifecycle receipts, and selected profile bytes
with the manifest's immutable bindings.

## Remediation

Stop mutation. Restore the mandatory policy, pin the protected profile digest,
or obtain a new externally issued grant. The agent fleet must not repair,
renew, widen, or reactivate its own authority.

## Verification

Re-run schema and semantic conformance, then evaluate the grant at the intended
operation time from the protected controller. Confirm that revocation and the
kill switch still stop mutation.
