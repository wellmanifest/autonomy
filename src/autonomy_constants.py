"""Normative constants, diagnostic model, and strict JSON loader for Wellmanifest Autonomy."""

from __future__ import annotations

import errno
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SYNTAX = "AUTONOMY-SYNTAX-001"
POLICY = "AUTONOMY-POLICY-001"
BOUNDARY = "AUTONOMY-BOUNDARY-001"

# Stable public diagnostics are deliberately coarse. Internal aliases keep the
# validator readable without expanding the public compatibility surface.
GRANT = POLICY
RISK = POLICY
CONTINUATION = POLICY
PROFILE = POLICY
SEPARATION = BOUNDARY
HEAD = BOUNDARY

CRITICAL_CODES = {POLICY, BOUNDARY}
URI_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:[^\s]+$")
DIGEST_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
SHA_RE = re.compile(r"^[a-f0-9]{40}$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:/-]*$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
ENV_RE = re.compile(r"^[A-Z][A-Z0-9_]+$")
RFC6901_INDEX_RE = re.compile(r"^(?:0|[1-9][0-9]*)$")
RFC3339_OFFSET_RE = re.compile(r"^(?:.*)[Tt](?:.+)(?:[Zz]|[+-][0-9]{2}:[0-9]{2})$")

MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_JSON_DEPTH = 64

ROLES = {
    "observer",
    "dispatcher",
    "planner",
    "implementer",
    "validator",
    "publisher",
    "auditor",
}
DIMENSIONS = {"principal", "credential", "workspace", "approval-identity"}
RISK_ORDER = {"low": 0, "moderate": 1, "high": 2, "critical": 3}

AUTHORITIES = {
    "observe",
    "trigger-cycle",
    "claim-cycle",
    "reconcile-cycle",
    "select-task",
    "propose-plan",
    "create-ticket",
    "create-branch",
    "edit-candidate",
    "test-candidate",
    "commit-candidate",
    "push-candidate",
    "open-pull-request",
    "issue-validator-attestation",
    "approve-via-validator-app",
    "merge-pull-request",
    "post-merge-read-back",
    "append-audit-receipt",
}

ROLE_AUTHORITY_CEILINGS = {
    "observer": {"observe"},
    "dispatcher": {"trigger-cycle", "claim-cycle", "reconcile-cycle"},
    "planner": {"select-task", "propose-plan"},
    "implementer": {
        "create-ticket",
        "create-branch",
        "edit-candidate",
        "test-candidate",
        "commit-candidate",
        "push-candidate",
    },
    "validator": {"issue-validator-attestation", "approve-via-validator-app"},
    "publisher": {
        "open-pull-request",
        "merge-pull-request",
        "post-merge-read-back",
    },
    "auditor": {"observe", "append-audit-receipt"},
}

REQUIRED_ACTIONS = set().union(*ROLE_AUTHORITY_CEILINGS.values())
MANDATORY_EXCLUDED_EFFECTS = {
    "secrets",
    "destructive-infrastructure",
    "billing",
    "legal",
    "identity-and-access",
    "security-boundary",
    "authority-policy",
    "grant-mutation",
    "force-push",
    "history-rewrite",
    "direct-default-branch-push",
    "untrusted-dependency-publish",
}
PIPELINE_STATES = [
    "dispatch",
    "claim",
    "observe",
    "evidence",
    "plan",
    "grant-check",
    "isolated-edit",
    "deterministic-validate",
    "independent-validate",
    "publish-pr",
    "exact-head-gate",
    "post-approval-convergence",
    "protected-merge",
    "post-merge-verify",
    "checkpoint",
    "continue",
]
REQUIRED_GATES = {
    "trigger-liveness",
    "queue-claim",
    "invocation-correlation",
    "registry-consistency",
    "grant-active",
    "candidate-scope",
    "intent-history",
    "contract-consumers",
    "deterministic-checks",
    "check-provenance",
    "independent-validator",
    "exact-head-current-base",
    "post-approval-convergence",
    "effect-reconciliation",
    "post-merge-read-back",
}
REQUIRED_BINDINGS = {
    "repository",
    "pullRequest",
    "headSha",
    "baseSha",
    "ticket",
    "grant",
    "profileDigest",
    "actor",
}
REQUIRED_CHECKS = {"governance", "tests", "security", "validator"}
REQUIRED_RECEIPTS = {
    "observation",
    "trigger-delivery",
    "queue-claim",
    "registry-resolution",
    "intent-checkpoint",
    "base-refresh",
    "contract-migration",
    "check-provenance",
    "policy-convergence",
    "supersession-disposition",
    "plan",
    "grant-check",
    "change",
    "deterministic-validation",
    "independent-validation",
    "publication",
    "read-back",
    "liveness-canary",
    "branch-cleanup",
    "scheduler-heartbeat",
    "missed-cycle",
    "effect-reconciliation",
}
REQUIRED_IDEMPOTENCY_BINDINGS = {
    "repository",
    "ticket",
    "correlationId",
    "headSha",
    "operation",
}
REQUIRED_EFFECT_BINDINGS = {
    "repository",
    "target",
    "headSha",
    "ticket",
    "correlationId",
    "operation",
    "externalEffectId",
}
REQUIRED_ALREADY_APPLIED_BINDINGS = {
    "repository",
    "pullRequest",
    "baseSha",
    "headSha",
    "operation",
    "approvalId",
    "mergeCommitSha",
    "mergedAt",
}
REQUIRED_INVOCATION_BINDINGS = {
    "strategy",
    "repository",
    "target",
    "headSha",
    "correlationId",
}
REQUIRED_REGISTRY_BINDINGS = {
    "repository",
    "baseBranch",
    "requiredChecks",
    "checkProvenance",
    "validatorIdentity",
    "mergePolicy",
}
REQUIRED_CANARY_RECEIPTS = {
    "scheduler-heartbeat",
    "trigger-delivery",
    "queue-claim",
    "registry-resolution",
    "check-provenance",
    "policy-convergence",
    "deterministic-validation",
    "independent-validation",
    "publication",
    "read-back",
    "branch-cleanup",
}
REQUIRED_CONSUMER_SURFACES = {
    "local",
    "container-image",
    "compose",
    "hosted-ci",
    "validator",
}
REQUIRED_CHECK_PROVENANCE_BINDINGS = {
    "producer",
    "event",
    "repository",
    "headSha",
    "checkName",
}
REQUIRED_POLICY_REBINDINGS = {
    "repository",
    "pullRequest",
    "headSha",
    "baseSha",
    "approvalId",
    "requiredCheckSet",
    "policyDigest",
    "registryDigest",
}
REQUIRED_SUPERSESSION_BINDINGS = {
    "predecessorRepository",
    "predecessorPullRequest",
    "predecessorHeadSha",
    "successorPullRequest",
    "successorHeadSha",
    "successorMergeSha",
    "contentDisposition",
    "receiptDigest",
}
SUPERSESSION_CLOSURE_MODES = {"explicit-later", "provider-coupled"}
PROVIDER_COUPLED_READ_BACKS = {
    "branchAbsent",
    "pullRequestClosed",
    "pullRequestUnmerged",
    "archiveHeadPreserved",
}
REQUIRED_STOP_CONDITIONS = {
    "grant-revoked",
    "grant-expired",
    "kill-switch-disabled",
    "no-runnable-task",
    "out-of-scope",
    "independent-validation-failed",
    "budget-exhausted",
    "retry-exhausted",
    "ambiguous-evidence",
    "protected-authority-unavailable",
    "liveness-proof-stale",
    "registry-drift",
    "trigger-quorum-unavailable",
}

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = ROOT / "profiles" / "subactor-semcod.profile.json"


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    message: str
    severity: str


class StrictJsonError(ValueError):
    """Raised when a JSON input violates regular-file, uniqueness, finiteness, or depth bounds."""


def _reject_constant(token: str) -> Any:
    raise StrictJsonError(f"non-standard JSON constant {token!r} is forbidden")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJsonError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def strict_json_loads(raw_text: str) -> Any:
    try:
        parsed = json.loads(
            raw_text,
            parse_constant=_reject_constant,
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (json.JSONDecodeError, RecursionError) as error:
        raise StrictJsonError(str(error)) from error
    stack: list[tuple[Any, int]] = [(parsed, 0)]
    while stack:
        current, depth = stack.pop()
        if depth > MAX_JSON_DEPTH:
            raise StrictJsonError(f"JSON nesting depth exceeds {MAX_JSON_DEPTH}")
        if isinstance(current, dict):
            for child in current.values():
                if isinstance(child, (dict, list)):
                    stack.append((child, depth + 1))
        elif isinstance(current, list):
            for child in current:
                if isinstance(child, (dict, list)):
                    stack.append((child, depth + 1))
    return parsed


def safe_read_regular_bytes(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(path, flags)
    except OSError as error:
        if error.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise StrictJsonError("symlinks are forbidden") from error
        raise StrictJsonError(str(error)) from error
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise StrictJsonError("expected a regular file")
        if info.st_size > MAX_JSON_BYTES:
            raise StrictJsonError(f"file exceeds {MAX_JSON_BYTES} bytes")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_JSON_BYTES:
                raise StrictJsonError(f"file exceeds {MAX_JSON_BYTES} bytes")
            chunks.append(chunk)
        return b"".join(chunks)
    except OSError as error:
        raise StrictJsonError(str(error)) from error
    finally:
        os.close(fd)


def safe_read_json(path: Path) -> tuple[bytes, Any]:
    raw = safe_read_regular_bytes(path)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise StrictJsonError(f"invalid UTF-8: {error}") from error
    return raw, strict_json_loads(text)
