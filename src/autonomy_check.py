#!/usr/bin/env python3
"""Dependency-free conformance checker for Wellmanifest Autonomy 0.5."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

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
    "protected-merge",
    "post-merge-verify",
    "checkpoint",
    "continue",
]
REQUIRED_GATES = {
    "trigger-liveness",
    "queue-claim",
    "registry-consistency",
    "grant-active",
    "candidate-scope",
    "intent-history",
    "contract-consumers",
    "deterministic-checks",
    "check-provenance",
    "independent-validator",
    "exact-head-current-base",
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
    "plan",
    "grant-check",
    "change",
    "deterministic-validation",
    "independent-validation",
    "publication",
    "read-back",
    "liveness-canary",
    "branch-cleanup",
}
REQUIRED_IDEMPOTENCY_BINDINGS = {
    "repository",
    "ticket",
    "correlationId",
    "headSha",
    "operation",
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
    "trigger-delivery",
    "queue-claim",
    "registry-resolution",
    "check-provenance",
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


class Validator:
    def __init__(self, *, at: datetime | None = None, profile_path: Path | None = None) -> None:
        self.at = at
        self.profile_path = profile_path
        self.findings: list[Finding] = []

    def add(self, code: str, path: str, message: str) -> None:
        finding = Finding(
            code=code,
            path=path,
            message=message,
            severity="critical" if code in CRITICAL_CODES else "error",
        )
        if finding not in self.findings:
            self.findings.append(finding)

    def closed(
        self,
        value: Any,
        path: str,
        required: Iterable[str],
        allowed: Iterable[str],
    ) -> bool:
        if not isinstance(value, dict):
            self.add(SYNTAX, path, "expected an object")
            return False
        required_set = set(required)
        allowed_set = set(allowed)
        for key in sorted(required_set - value.keys()):
            self.add(SYNTAX, path, f"missing required property {key!r}")
        for key in sorted(value.keys() - allowed_set):
            self.add(SYNTAX, f"{path}.{key}", "unknown property")
        return required_set <= value.keys() and value.keys() <= allowed_set

    def string(
        self,
        value: Any,
        path: str,
        *,
        pattern: re.Pattern[str] | None = None,
        nullable: bool = False,
    ) -> bool:
        if nullable and value is None:
            return True
        if not isinstance(value, str) or not value:
            self.add(SYNTAX, path, "expected a non-empty string")
            return False
        if pattern is not None and pattern.fullmatch(value) is None:
            self.add(SYNTAX, path, "string does not match the required format")
            return False
        return True

    def boolean(self, value: Any, path: str, expected: bool | None = None) -> bool:
        if not isinstance(value, bool):
            self.add(SYNTAX, path, "expected a boolean")
            return False
        if expected is not None and value is not expected:
            self.add(SYNTAX, path, f"expected {str(expected).lower()}")
            return False
        return True

    def integer(self, value: Any, path: str, minimum: int, maximum: int) -> bool:
        if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
            self.add(SYNTAX, path, f"expected an integer in {minimum}..{maximum}")
            return False
        return True

    def number(self, value: Any, path: str, minimum: float, maximum: float) -> bool:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            self.add(SYNTAX, path, "expected a number")
            return False
        if not minimum < float(value) <= maximum:
            self.add(SYNTAX, path, f"expected a number > {minimum} and <= {maximum}")
            return False
        return True

    def enum(self, value: Any, path: str, choices: set[str]) -> bool:
        if not isinstance(value, str) or value not in choices:
            self.add(SYNTAX, path, f"expected one of {sorted(choices)}")
            return False
        return True

    def uri(self, value: Any, path: str) -> bool:
        if not self.string(value, path, pattern=URI_RE):
            return False
        if not urlsplit(value).scheme:
            self.add(SYNTAX, path, "URI must have a scheme")
            return False
        return True

    def timestamp(self, value: Any, path: str) -> datetime | None:
        if not self.string(value, path):
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            self.add(SYNTAX, path, "expected an RFC 3339 date-time")
            return None
        if parsed.tzinfo is None:
            self.add(SYNTAX, path, "date-time must include an offset")
            return None
        return parsed

    def string_set(
        self,
        value: Any,
        path: str,
        *,
        minimum: int = 0,
        allowed: set[str] | None = None,
    ) -> list[str] | None:
        if not isinstance(value, list) or len(value) < minimum:
            self.add(SYNTAX, path, f"expected an array with at least {minimum} item(s)")
            return None
        if any(not isinstance(item, str) or not item for item in value):
            self.add(SYNTAX, path, "expected non-empty strings")
            return None
        if len(value) != len(set(value)):
            self.add(SYNTAX, path, "duplicate values are forbidden")
        if allowed is not None:
            for index, item in enumerate(value):
                if item not in allowed:
                    self.add(SYNTAX, f"{path}[{index}]", "unknown value")
        return value

    def manifest_shape(self, doc: Any, path: str) -> bool:
        fields = (
            "$schema",
            "schema",
            "id",
            "version",
            "status",
            "subject",
            "grant",
            "fleet",
            "riskPolicy",
            "budgets",
            "queue",
            "executionLiveness",
            "pipeline",
            "changeControl",
            "publication",
            "receipts",
            "continuation",
        )
        if not self.closed(doc, path, fields, fields):
            return False
        if doc["$schema"] != "https://wellmanifest.com/schemas/autonomy-manifest/v3":
            self.add(SYNTAX, f"{path}.$schema", "unknown schema URI")
        if doc["schema"] != "wellmanifest.autonomy/manifest/v3":
            self.add(SYNTAX, f"{path}.schema", "unknown manifest version")
        self.uri(doc["id"], f"{path}.id")
        self.string(doc["version"], f"{path}.version", pattern=SEMVER_RE)
        self.enum(
            doc["status"], f"{path}.status", {"draft", "active", "suspended", "revoked", "expired"}
        )
        self.subject_shape(doc["subject"], f"{path}.subject")
        self.grant_shape(doc["grant"], f"{path}.grant")
        self.fleet_shape(doc["fleet"], f"{path}.fleet")
        self.risk_shape(doc["riskPolicy"], f"{path}.riskPolicy")
        self.budgets_shape(doc["budgets"], f"{path}.budgets")
        self.queue_shape(doc["queue"], f"{path}.queue")
        self.execution_liveness_shape(
            doc["executionLiveness"], f"{path}.executionLiveness"
        )
        self.pipeline_shape(doc["pipeline"], f"{path}.pipeline")
        self.change_control_shape(doc["changeControl"], f"{path}.changeControl")
        self.publication_shape(doc["publication"], f"{path}.publication")
        self.receipts_shape(doc["receipts"], f"{path}.receipts")
        self.continuation_shape(doc["continuation"], f"{path}.continuation")
        return True

    def subject_shape(self, value: Any, path: str) -> None:
        fields = ("repository", "defaultBranch", "adoptedRevision", "policyDigest", "profile")
        if not self.closed(value, path, fields, fields):
            return
        self.string(value["repository"], f"{path}.repository", pattern=REPOSITORY_RE)
        self.string(value["defaultBranch"], f"{path}.defaultBranch")
        self.string(value["adoptedRevision"], f"{path}.adoptedRevision", pattern=SHA_RE)
        self.string(value["policyDigest"], f"{path}.policyDigest", pattern=DIGEST_RE)
        profile = value["profile"]
        fields = ("id", "version", "digest")
        if self.closed(profile, f"{path}.profile", fields, fields):
            self.string(profile["id"], f"{path}.profile.id", pattern=ID_RE)
            self.string(profile["version"], f"{path}.profile.version", pattern=SEMVER_RE)
            self.string(profile["digest"], f"{path}.profile.digest", pattern=DIGEST_RE)

    def grant_shape(self, value: Any, path: str) -> None:
        fields = (
            "id",
            "issuer",
            "issuedAt",
            "notBefore",
            "reviewAt",
            "expiresAt",
            "scope",
            "constraints",
        )
        if not self.closed(value, path, fields, fields):
            return
        self.uri(value["id"], f"{path}.id")
        issuer = value["issuer"]
        if self.closed(issuer, f"{path}.issuer", ("id", "kind"), ("id", "kind")):
            self.string(issuer["id"], f"{path}.issuer.id", pattern=ID_RE)
            self.enum(
                issuer["kind"],
                f"{path}.issuer.kind",
                {"human", "organization", "external-authority"},
            )
        for field in ("issuedAt", "notBefore", "reviewAt", "expiresAt"):
            self.timestamp(value[field], f"{path}.{field}")
        scope = value["scope"]
        fields = ("repositories", "branches", "pathAllow", "pathDeny", "actions", "riskCeiling")
        if self.closed(scope, f"{path}.scope", fields, fields):
            repos = self.string_set(scope["repositories"], f"{path}.scope.repositories", minimum=1)
            if repos is not None:
                for index, repo in enumerate(repos):
                    self.string(repo, f"{path}.scope.repositories[{index}]", pattern=REPOSITORY_RE)
            self.string_set(scope["branches"], f"{path}.scope.branches", minimum=1)
            for field in ("pathAllow", "pathDeny"):
                globs = self.string_set(scope[field], f"{path}.scope.{field}", minimum=1)
                if globs:
                    for index, item in enumerate(globs):
                        if item.startswith("/") or "../" in item or item == "..":
                            self.add(SYNTAX, f"{path}.scope.{field}[{index}]", "unsafe path glob")
            self.string_set(
                scope["actions"], f"{path}.scope.actions", minimum=1, allowed=AUTHORITIES
            )
            self.enum(scope["riskCeiling"], f"{path}.scope.riskCeiling", {"low", "moderate"})
        constraints = value["constraints"]
        fields = (
            "noPerPullRequestHumanApproval",
            "allowAutomatedMerge",
            "selfExtension",
            "selfRenewal",
            "killSwitch",
            "killSwitchExpected",
        )
        if self.closed(constraints, f"{path}.constraints", fields, fields):
            self.boolean(
                constraints["noPerPullRequestHumanApproval"],
                f"{path}.constraints.noPerPullRequestHumanApproval",
                True,
            )
            self.boolean(
                constraints["allowAutomatedMerge"], f"{path}.constraints.allowAutomatedMerge", True
            )
            self.boolean(constraints["selfExtension"], f"{path}.constraints.selfExtension", False)
            self.boolean(constraints["selfRenewal"], f"{path}.constraints.selfRenewal", False)
            self.string(constraints["killSwitch"], f"{path}.constraints.killSwitch", pattern=ENV_RE)
            self.string(constraints["killSwitchExpected"], f"{path}.constraints.killSwitchExpected")

    def fleet_shape(self, value: Any, path: str) -> None:
        if not self.closed(value, path, ("roles", "separation"), ("roles", "separation")):
            return
        roles = value["roles"]
        if not isinstance(roles, list) or len(roles) < 7:
            self.add(SYNTAX, f"{path}.roles", "expected at least seven roles")
        else:
            for index, role in enumerate(roles):
                self.role_shape(role, f"{path}.roles[{index}]")
        separation = value["separation"]
        if not isinstance(separation, list) or len(separation) < 3:
            self.add(SYNTAX, f"{path}.separation", "expected at least three separation rules")
        else:
            for index, rule in enumerate(separation):
                item_path = f"{path}.separation[{index}]"
                if not self.closed(
                    rule,
                    item_path,
                    ("left", "right", "dimensions"),
                    ("left", "right", "dimensions"),
                ):
                    continue
                self.string(rule["left"], f"{item_path}.left", pattern=ID_RE)
                self.string(rule["right"], f"{item_path}.right", pattern=ID_RE)
                dimensions = self.string_set(
                    rule["dimensions"], f"{item_path}.dimensions", minimum=4, allowed=DIMENSIONS
                )
                if dimensions is not None and set(dimensions) != DIMENSIONS:
                    self.add(
                        SEPARATION,
                        f"{item_path}.dimensions",
                        "all four independence dimensions are required",
                    )

    def role_shape(self, value: Any, path: str) -> None:
        required = (
            "id",
            "role",
            "principal",
            "provider",
            "authorities",
            "forbiddenAuthorities",
            "workspaceIsolation",
        )
        allowed = (*required, "model")
        if not self.closed(value, path, required, allowed):
            return
        self.string(value["id"], f"{path}.id", pattern=ID_RE)
        self.enum(value["role"], f"{path}.role", ROLES)
        self.string(value["principal"], f"{path}.principal", pattern=ID_RE)
        self.string(value["provider"], f"{path}.provider")
        if "model" in value:
            self.string(value["model"], f"{path}.model", nullable=True)
        self.string_set(value["authorities"], f"{path}.authorities", allowed=AUTHORITIES)
        self.string_set(
            value["forbiddenAuthorities"],
            f"{path}.forbiddenAuthorities",
            minimum=1,
            allowed=AUTHORITIES,
        )
        self.enum(
            value["workspaceIsolation"],
            f"{path}.workspaceIsolation",
            {"read-only", "dedicated-worktree", "fresh-checkout", "protected-service"},
        )

    def risk_shape(self, value: Any, path: str) -> None:
        fields = ("autonomousTiers", "escalatedTiers", "excludedEffects")
        if not self.closed(value, path, fields, fields):
            return
        self.string_set(
            value["autonomousTiers"],
            f"{path}.autonomousTiers",
            minimum=1,
            allowed={"low", "moderate"},
        )
        self.string_set(
            value["escalatedTiers"],
            f"{path}.escalatedTiers",
            minimum=2,
            allowed={"high", "critical"},
        )
        self.string_set(value["excludedEffects"], f"{path}.excludedEffects", minimum=1)

    def budgets_shape(self, value: Any, path: str) -> None:
        limits = {
            "maxFilesPerChange": (1, 50),
            "maxComponentsPerChange": (1, 10),
            "maxPublicInterfacesPerChange": (0, 10),
            "maxRuntimeDependenciesPerChange": (0, 10),
            "maxMinutesPerCycle": (1, 240),
            "maxRetriesPerTask": (0, 5),
            "maxConsecutiveCycles": (1, 100),
            "maxConcurrentTasks": (1, 5),
            "cooldownSeconds": (1, 86400),
            "leaseSeconds": (60, 86400),
        }
        fields = (*limits.keys(), "maxCostUsdPerCycle")
        if not self.closed(value, path, fields, fields):
            return
        for field, (minimum, maximum) in limits.items():
            self.integer(value[field], f"{path}.{field}", minimum, maximum)
        self.number(value["maxCostUsdPerCycle"], f"{path}.maxCostUsdPerCycle", 0, 100)

    def queue_shape(self, value: Any, path: str) -> None:
        fields = (
            "source",
            "selection",
            "freshnessSeconds",
            "deduplication",
            "humanBoundaryLabels",
            "oneMutationPerCycle",
            "durable",
            "delivery",
            "checkpointStore",
            "idempotencyBindings",
            "deadLetterAfterAttempts",
            "resumeFromCheckpoint",
        )
        if not self.closed(value, path, fields, fields):
            return
        self.enum(value["source"], f"{path}.source", {"planfile", "todo2code", "composite"})
        if value["selection"] != "runnable-priority-dag":
            self.add(SYNTAX, f"{path}.selection", "expected runnable-priority-dag")
        self.integer(value["freshnessSeconds"], f"{path}.freshnessSeconds", 60, 2592000)
        if value["deduplication"] != "fingerprint":
            self.add(SYNTAX, f"{path}.deduplication", "expected fingerprint")
        self.string_set(value["humanBoundaryLabels"], f"{path}.humanBoundaryLabels", minimum=2)
        self.boolean(value["oneMutationPerCycle"], f"{path}.oneMutationPerCycle", True)
        self.boolean(value["durable"], f"{path}.durable")
        if value["delivery"] != "at-least-once":
            self.add(POLICY, f"{path}.delivery", "delivery must be at-least-once")
        self.uri(value["checkpointStore"], f"{path}.checkpointStore")
        self.string_set(
            value["idempotencyBindings"],
            f"{path}.idempotencyBindings",
            minimum=1,
            allowed=REQUIRED_IDEMPOTENCY_BINDINGS,
        )
        self.integer(value["deadLetterAfterAttempts"], f"{path}.deadLetterAfterAttempts", 1, 10)
        self.boolean(value["resumeFromCheckpoint"], f"{path}.resumeFromCheckpoint")

    def execution_liveness_shape(self, value: Any, path: str) -> None:
        fields = (
            "primaryTrigger",
            "watchdog",
            "independentPrincipals",
            "manualDispatchProvesLiveness",
            "missedTriggerStatus",
            "perRepositoryIsolation",
            "unrelatedFailureBlocksMerge",
            "aggregateStatusAuthoritative",
            "registry",
            "canary",
        )
        if not self.closed(value, path, fields, fields):
            return

        primary = value["primaryTrigger"]
        trigger_fields = ("id", "kind", "principal", "protected")
        if self.closed(primary, f"{path}.primaryTrigger", trigger_fields, trigger_fields):
            self.string(primary["id"], f"{path}.primaryTrigger.id", pattern=ID_RE)
            self.enum(
                primary["kind"],
                f"{path}.primaryTrigger.kind",
                {"event", "scheduler", "durable-queue"},
            )
            self.string(primary["principal"], f"{path}.primaryTrigger.principal", pattern=ID_RE)
            self.boolean(primary["protected"], f"{path}.primaryTrigger.protected")

        watchdog = value["watchdog"]
        watchdog_fields = (
            "id",
            "kind",
            "principal",
            "protected",
            "maxSilenceSeconds",
            "triggerOnSilence",
        )
        if self.closed(watchdog, f"{path}.watchdog", watchdog_fields, watchdog_fields):
            self.string(watchdog["id"], f"{path}.watchdog.id", pattern=ID_RE)
            if watchdog["kind"] != "independent-scheduler":
                self.add(POLICY, f"{path}.watchdog.kind", "watchdog must be independent")
            self.string(watchdog["principal"], f"{path}.watchdog.principal", pattern=ID_RE)
            self.boolean(watchdog["protected"], f"{path}.watchdog.protected")
            self.integer(
                watchdog["maxSilenceSeconds"], f"{path}.watchdog.maxSilenceSeconds", 60, 86400
            )
            self.boolean(watchdog["triggerOnSilence"], f"{path}.watchdog.triggerOnSilence")

        for field in (
            "independentPrincipals",
            "manualDispatchProvesLiveness",
            "perRepositoryIsolation",
            "unrelatedFailureBlocksMerge",
            "aggregateStatusAuthoritative",
        ):
            self.boolean(value[field], f"{path}.{field}")
        if value["missedTriggerStatus"] != "degraded":
            self.add(POLICY, f"{path}.missedTriggerStatus", "missed triggers must degrade status")

        registry = value["registry"]
        registry_fields = (
            "source",
            "digest",
            "protected",
            "singleSource",
            "requiredBindings",
            "driftCheck",
        )
        if self.closed(registry, f"{path}.registry", registry_fields, registry_fields):
            self.uri(registry["source"], f"{path}.registry.source")
            self.string(registry["digest"], f"{path}.registry.digest", pattern=DIGEST_RE)
            self.boolean(registry["protected"], f"{path}.registry.protected")
            self.boolean(registry["singleSource"], f"{path}.registry.singleSource")
            self.string_set(
                registry["requiredBindings"],
                f"{path}.registry.requiredBindings",
                minimum=1,
                allowed=REQUIRED_REGISTRY_BINDINGS,
            )
            self.boolean(registry["driftCheck"], f"{path}.registry.driftCheck")

        canary = value["canary"]
        canary_fields = ("mode", "maximumAgeSeconds", "manualDispatchCounts", "requiredReceipts")
        if self.closed(canary, f"{path}.canary", canary_fields, canary_fields):
            if canary["mode"] != "protected-low-risk-pr":
                self.add(
                    POLICY,
                    f"{path}.canary.mode",
                    "canary must traverse protected publication",
                )
            self.integer(
                canary["maximumAgeSeconds"], f"{path}.canary.maximumAgeSeconds", 60, 604800
            )
            self.boolean(canary["manualDispatchCounts"], f"{path}.canary.manualDispatchCounts")
            self.string_set(
                canary["requiredReceipts"],
                f"{path}.canary.requiredReceipts",
                minimum=1,
                allowed=REQUIRED_CANARY_RECEIPTS,
            )

    def pipeline_shape(self, value: Any, path: str) -> None:
        fields = ("states", "requiredGates", "onFailure", "onOutOfScope")
        if not self.closed(value, path, fields, fields):
            return
        states = self.string_set(value["states"], f"{path}.states", minimum=15)
        if states is not None and states != PIPELINE_STATES:
            self.add(
                CONTINUATION, f"{path}.states", "pipeline states must match the normative order"
            )
        gates = value["requiredGates"]
        if not isinstance(gates, list) or len(gates) < 12:
            self.add(SYNTAX, f"{path}.requiredGates", "expected at least twelve gates")
        else:
            for index, gate in enumerate(gates):
                item_path = f"{path}.requiredGates[{index}]"
                fields = ("id", "stage", "kind", "producer", "protected", "failClosed")
                if not self.closed(gate, item_path, fields, fields):
                    continue
                self.string(gate["id"], f"{item_path}.id", pattern=ID_RE)
                self.enum(
                    gate["stage"],
                    f"{item_path}.stage",
                    {
                        "pre-cycle",
                        "pre-edit",
                        "pre-push",
                        "pre-approval",
                        "pre-merge",
                        "post-merge",
                    },
                )
                self.enum(
                    gate["kind"],
                    f"{item_path}.kind",
                    {"liveness", "deterministic", "independent-attestation", "read-back"},
                )
                self.string(gate["producer"], f"{item_path}.producer", pattern=ID_RE)
                self.boolean(gate["protected"], f"{item_path}.protected")
                self.boolean(gate["failClosed"], f"{item_path}.failClosed", True)
        if value["onFailure"] != "fail-closed":
            self.add(CONTINUATION, f"{path}.onFailure", "failure must fail closed")
        if value["onOutOfScope"] != "escalate":
            self.add(CONTINUATION, f"{path}.onOutOfScope", "out-of-scope work must escalate")

    def change_control_shape(self, value: Any, path: str) -> None:
        fields = (
            "intentHistory",
            "baseRefresh",
            "contractMigration",
            "checkProvenance",
            "providerReads",
        )
        if not self.closed(value, path, fields, fields):
            return

        intent = value["intentHistory"]
        intent_fields = ("checkpointBeforeImplementation", "immutableScope")
        if self.closed(intent, f"{path}.intentHistory", intent_fields, intent_fields):
            self.boolean(
                intent["checkpointBeforeImplementation"],
                f"{path}.intentHistory.checkpointBeforeImplementation",
                True,
            )
            self.boolean(intent["immutableScope"], f"{path}.intentHistory.immutableScope", True)

        refresh = value["baseRefresh"]
        refresh_fields = ("acceptedBaseRequired", "revalidateAll", "historyRewrite", "mode")
        if self.closed(refresh, f"{path}.baseRefresh", refresh_fields, refresh_fields):
            self.boolean(
                refresh["acceptedBaseRequired"],
                f"{path}.baseRefresh.acceptedBaseRequired",
                True,
            )
            self.boolean(refresh["revalidateAll"], f"{path}.baseRefresh.revalidateAll", True)
            self.boolean(refresh["historyRewrite"], f"{path}.baseRefresh.historyRewrite", False)
            if refresh["mode"] != "successor-pull-request":
                self.add(
                    BOUNDARY,
                    f"{path}.baseRefresh.mode",
                    "base refresh must publish a successor without rewriting history",
                )

        migration = value["contractMigration"]
        migration_fields = (
            "exactVersionAllowlist",
            "resolveBeforeConsumerExecution",
            "unknownVersion",
            "consumerInventoryRequired",
            "allConsumersMustPass",
            "requiredSurfaces",
        )
        if self.closed(
            migration,
            f"{path}.contractMigration",
            migration_fields,
            migration_fields,
        ):
            for field in (
                "exactVersionAllowlist",
                "resolveBeforeConsumerExecution",
                "consumerInventoryRequired",
                "allConsumersMustPass",
            ):
                self.boolean(migration[field], f"{path}.contractMigration.{field}", True)
            if migration["unknownVersion"] != "fail-closed":
                self.add(
                    POLICY,
                    f"{path}.contractMigration.unknownVersion",
                    "unknown contract versions must fail closed",
                )
            self.string_set(
                migration["requiredSurfaces"],
                f"{path}.contractMigration.requiredSurfaces",
                minimum=5,
                allowed=REQUIRED_CONSUMER_SURFACES,
            )

        provenance = value["checkProvenance"]
        provenance_fields = (
            "protectedRegistry",
            "requiredBindings",
            "authoritativeProducerRequired",
            "duplicateContextPolicy",
            "nonAuthoritativeStatusBlocksMerge",
        )
        if self.closed(
            provenance,
            f"{path}.checkProvenance",
            provenance_fields,
            provenance_fields,
        ):
            self.boolean(
                provenance["protectedRegistry"],
                f"{path}.checkProvenance.protectedRegistry",
                True,
            )
            self.string_set(
                provenance["requiredBindings"],
                f"{path}.checkProvenance.requiredBindings",
                minimum=5,
                allowed=REQUIRED_CHECK_PROVENANCE_BINDINGS,
            )
            self.boolean(
                provenance["authoritativeProducerRequired"],
                f"{path}.checkProvenance.authoritativeProducerRequired",
                True,
            )
            if provenance["duplicateContextPolicy"] != "reject-ambiguous":
                self.add(
                    BOUNDARY,
                    f"{path}.checkProvenance.duplicateContextPolicy",
                    "ambiguous duplicate check contexts must fail closed",
                )
            self.boolean(
                provenance["nonAuthoritativeStatusBlocksMerge"],
                f"{path}.checkProvenance.nonAuthoritativeStatusBlocksMerge",
                False,
            )

        reads = value["providerReads"]
        read_fields = ("boundedRetries", "rateLimitStatus", "fallbackMustPreserveAuthority")
        if self.closed(reads, f"{path}.providerReads", read_fields, read_fields):
            self.boolean(reads["boundedRetries"], f"{path}.providerReads.boundedRetries", True)
            if reads["rateLimitStatus"] != "degraded":
                self.add(
                    POLICY,
                    f"{path}.providerReads.rateLimitStatus",
                    "rate limiting must produce a degraded outcome",
                )
            self.boolean(
                reads["fallbackMustPreserveAuthority"],
                f"{path}.providerReads.fallbackMustPreserveAuthority",
                True,
            )

    def publication_shape(self, value: Any, path: str) -> None:
        fields = (
            "mode",
            "approval",
            "requiredChecks",
            "bindings",
            "sameRepositoryOnly",
            "recheckBaseBeforeMerge",
            "autonomousMerge",
            "mergeMode",
            "nativeAutoMerge",
            "directDefaultBranchPush",
            "deleteBranchAfterMerge",
            "postMergeReadBack",
        )
        if not self.closed(value, path, fields, fields):
            return
        if value["mode"] != "pull-request":
            self.add(HEAD, f"{path}.mode", "publication must use pull requests")
        self.enum(
            value["approval"],
            f"{path}.approval",
            {"trusted-validator-app", "signed-validator-attestation"},
        )
        self.string_set(value["requiredChecks"], f"{path}.requiredChecks", minimum=1)
        self.string_set(value["bindings"], f"{path}.bindings", minimum=1, allowed=REQUIRED_BINDINGS)
        if value["mergeMode"] != "protected-explicit":
            self.add(HEAD, f"{path}.mergeMode", "merge must use protected explicit execution")
        for field in (
            "sameRepositoryOnly",
            "recheckBaseBeforeMerge",
            "autonomousMerge",
            "nativeAutoMerge",
            "directDefaultBranchPush",
            "deleteBranchAfterMerge",
            "postMergeReadBack",
        ):
            self.boolean(value[field], f"{path}.{field}")

    def receipts_shape(self, value: Any, path: str) -> None:
        fields = ("store", "required", "redaction", "retentionDays")
        if not self.closed(value, path, fields, fields):
            return
        self.uri(value["store"], f"{path}.store")
        self.string_set(
            value["required"], f"{path}.required", minimum=17, allowed=REQUIRED_RECEIPTS
        )
        if value["redaction"] != "secret-free":
            self.add(RISK, f"{path}.redaction", "receipts must be secret-free")
        self.integer(value["retentionDays"], f"{path}.retentionDays", 30, 3650)

    def continuation_shape(self, value: Any, path: str) -> None:
        fields = (
            "enabled",
            "nextTaskWithoutHumanApproval",
            "closeOnlyAfterReadBack",
            "stopConditions",
        )
        if not self.closed(value, path, fields, fields):
            return
        self.boolean(value["enabled"], f"{path}.enabled", True)
        self.boolean(
            value["nextTaskWithoutHumanApproval"], f"{path}.nextTaskWithoutHumanApproval", True
        )
        self.boolean(value["closeOnlyAfterReadBack"], f"{path}.closeOnlyAfterReadBack", True)
        self.string_set(value["stopConditions"], f"{path}.stopConditions", minimum=1)

    def profile_shape(self, doc: Any, path: str) -> bool:
        fields = (
            "$schema",
            "schema",
            "id",
            "version",
            "status",
            "ownership",
            "bindings",
            "protectedBoundaries",
        )
        if not self.closed(doc, path, fields, fields):
            return False
        if doc["$schema"] != "https://wellmanifest.com/schemas/autonomy-manifest/v3":
            self.add(SYNTAX, f"{path}.$schema", "unknown schema URI")
        if doc["schema"] != "wellmanifest.autonomy/profile/v3":
            self.add(SYNTAX, f"{path}.schema", "unknown profile version")
        self.string(doc["id"], f"{path}.id", pattern=ID_RE)
        self.string(doc["version"], f"{path}.version", pattern=SEMVER_RE)
        self.enum(doc["status"], f"{path}.status", {"experimental", "stable", "deprecated"})
        ownership = doc["ownership"]
        if self.closed(
            ownership,
            f"{path}.ownership",
            ("standardOwner", "runtimeOwners"),
            ("standardOwner", "runtimeOwners"),
        ):
            if ownership["standardOwner"] != "wellmanifest/autonomy":
                self.add(
                    PROFILE,
                    f"{path}.ownership.standardOwner",
                    "standard ownership must remain in wellmanifest/autonomy",
                )
            owners = self.string_set(
                ownership["runtimeOwners"], f"{path}.ownership.runtimeOwners", minimum=1
            )
            if owners:
                for index, owner in enumerate(owners):
                    if not owner.startswith(("subactor/", "semcod/")):
                        self.add(
                            PROFILE,
                            f"{path}.ownership.runtimeOwners[{index}]",
                            "runtime owner must be subactor/* or semcod/*",
                        )
        bindings = doc["bindings"]
        if not isinstance(bindings, list) or len(bindings) < 7:
            self.add(SYNTAX, f"{path}.bindings", "expected at least seven bindings")
        else:
            for index, binding in enumerate(bindings):
                self.profile_binding_shape(binding, f"{path}.bindings[{index}]")
        boundaries = doc["protectedBoundaries"]
        fields = (
            "profileDigestExternal",
            "durableQueueProtected",
            "watchdogPrincipalIndependent",
            "registryDigestExternal",
            "targetOutcomeIsolated",
            "validatorPrincipalIndependent",
            "publisherCredentialProtected",
            "llmVerdictAdvisory",
        )
        if self.closed(boundaries, f"{path}.protectedBoundaries", fields, fields):
            for field in fields:
                self.boolean(boundaries[field], f"{path}.protectedBoundaries.{field}", True)
        return True

    def profile_binding_shape(self, value: Any, path: str) -> None:
        fields = ("stage", "product", "role", "mode", "capabilities", "contracts", "restrictions")
        if not self.closed(value, path, fields, fields):
            return
        self.enum(
            value["stage"],
            f"{path}.stage",
            {
                "dispatch",
                "observe",
                "evidence",
                "plan",
                "implement",
                "validate",
                "publish",
                "audit",
            },
        )
        if not self.string(value["product"], f"{path}.product"):
            return
        if not value["product"].startswith(("subactor/", "semcod/", "wellmanifest/")):
            self.add(PROFILE, f"{path}.product", "unknown product owner")
        self.enum(value["role"], f"{path}.role", ROLES)
        self.enum(
            value["mode"],
            f"{path}.mode",
            {
                "read-only",
                "protected-dispatch",
                "propose-only",
                "candidate-write",
                "validate-only",
                "protected-publish",
                "append-only-audit",
            },
        )
        self.string_set(value["capabilities"], f"{path}.capabilities", minimum=1)
        contracts = self.string_set(value["contracts"], f"{path}.contracts")
        if contracts:
            for index, contract in enumerate(contracts):
                self.uri(contract, f"{path}.contracts[{index}]")
        self.string_set(value["restrictions"], f"{path}.restrictions", minimum=1)

    def manifest_semantics(self, doc: dict[str, Any], path: str) -> None:
        if doc.get("status") != "active":
            self.add(
                GRANT, f"{path}.status", "only an active manifest authorizes autonomous effects"
            )

        subject = doc.get("subject", {})
        grant = doc.get("grant", {})
        scope = grant.get("scope", {})
        constraints = grant.get("constraints", {})
        if subject.get("repository") not in scope.get("repositories", []):
            self.add(
                GRANT, f"{path}.grant.scope.repositories", "subject repository is outside the grant"
            )
        if subject.get("defaultBranch") not in scope.get("branches", []):
            self.add(GRANT, f"{path}.grant.scope.branches", "default branch is outside the grant")
        actions = set(scope.get("actions", [])) if isinstance(scope.get("actions"), list) else set()
        missing_actions = REQUIRED_ACTIONS - actions
        if missing_actions:
            self.add(
                GRANT,
                f"{path}.grant.scope.actions",
                f"missing autonomous lifecycle actions: {sorted(missing_actions)}",
            )
        if (
            constraints.get("selfExtension") is not False
            or constraints.get("selfRenewal") is not False
        ):
            self.add(
                GRANT,
                f"{path}.grant.constraints",
                "grant self-extension and self-renewal are forbidden",
            )

        times = [
            self.timestamp(grant.get(field), f"{path}.grant.{field}")
            for field in ("issuedAt", "notBefore", "reviewAt", "expiresAt")
        ]
        if all(times):
            issued, not_before, review, expires = times
            assert (
                issued is not None
                and not_before is not None
                and review is not None
                and expires is not None
            )
            if not issued <= not_before < review < expires:
                self.add(
                    GRANT, f"{path}.grant", "expected issuedAt <= notBefore < reviewAt < expiresAt"
                )
            if self.at is not None and not (not_before <= self.at < expires):
                self.add(
                    GRANT, f"{path}.grant", "grant is not active at the requested evaluation time"
                )

        roles = doc.get("fleet", {}).get("roles", [])
        role_map = {role.get("role"): role for role in roles if isinstance(role, dict)}
        if set(role_map) != ROLES or len(roles) != len(ROLES):
            self.add(
                SEPARATION, f"{path}.fleet.roles", "exactly one of each normative role is required"
            )
        ids = [role.get("id") for role in roles if isinstance(role, dict)]
        if len(ids) != len(set(ids)):
            self.add(SEPARATION, f"{path}.fleet.roles", "role IDs must be unique")
        for role_name, role in role_map.items():
            authorities = set(role.get("authorities", []))
            forbidden = set(role.get("forbiddenAuthorities", []))
            overlap = authorities & forbidden
            if overlap:
                self.add(
                    SEPARATION,
                    f"{path}.fleet.roles",
                    f"{role_name} both holds and forbids {sorted(overlap)}",
                )
            excess = authorities - ROLE_AUTHORITY_CEILINGS[role_name]
            if excess:
                self.add(
                    SEPARATION,
                    f"{path}.fleet.roles",
                    f"{role_name} exceeds its authority ceiling: {sorted(excess)}",
                )

        critical_roles = [role_map.get(name) for name in ("implementer", "validator", "publisher")]
        if all(critical_roles):
            principals = [role.get("principal") for role in critical_roles if role]
            if len(set(principals)) != 3:
                self.add(
                    SEPARATION,
                    f"{path}.fleet.roles",
                    "implementer, validator, and publisher principals must differ",
                )
            expected_isolation = {
                "implementer": "dedicated-worktree",
                "validator": "fresh-checkout",
                "publisher": "protected-service",
            }
            for name, expected in expected_isolation.items():
                if role_map[name].get("workspaceIsolation") != expected:
                    self.add(
                        SEPARATION, f"{path}.fleet.roles", f"{name} requires {expected} isolation"
                    )

            ids_by_role = {name: role_map[name].get("id") for name in expected_isolation}
            required_pairs = {
                frozenset((ids_by_role["implementer"], ids_by_role["validator"])),
                frozenset((ids_by_role["implementer"], ids_by_role["publisher"])),
                frozenset((ids_by_role["validator"], ids_by_role["publisher"])),
            }
            observed_pairs = set()
            for rule in doc.get("fleet", {}).get("separation", []):
                if isinstance(rule, dict) and set(rule.get("dimensions", [])) == DIMENSIONS:
                    observed_pairs.add(frozenset((rule.get("left"), rule.get("right"))))
            if not required_pairs <= observed_pairs:
                self.add(
                    SEPARATION,
                    f"{path}.fleet.separation",
                    "all critical role pairs need four-dimensional separation",
                )

        risk = doc.get("riskPolicy", {})
        excluded = (
            set(risk.get("excludedEffects", []))
            if isinstance(risk.get("excludedEffects"), list)
            else set()
        )
        missing_exclusions = MANDATORY_EXCLUDED_EFFECTS - excluded
        if missing_exclusions:
            self.add(
                RISK,
                f"{path}.riskPolicy.excludedEffects",
                f"missing mandatory exclusions: {sorted(missing_exclusions)}",
            )
        ceiling = scope.get("riskCeiling")
        autonomous = risk.get("autonomousTiers", [])
        if ceiling in RISK_ORDER and any(
            RISK_ORDER.get(tier, 99) > RISK_ORDER[ceiling] for tier in autonomous
        ):
            self.add(
                RISK,
                f"{path}.riskPolicy.autonomousTiers",
                "autonomous tier exceeds the grant ceiling",
            )
        if set(risk.get("escalatedTiers", [])) != {"high", "critical"}:
            self.add(
                RISK, f"{path}.riskPolicy.escalatedTiers", "high and critical work must escalate"
            )

        queue = doc.get("queue", {})
        labels = (
            set(queue.get("humanBoundaryLabels", []))
            if isinstance(queue.get("humanBoundaryLabels"), list)
            else set()
        )
        if not {"human", "autonomy-frontier"} <= labels:
            self.add(
                CONTINUATION,
                f"{path}.queue.humanBoundaryLabels",
                "human and autonomy-frontier labels are required",
            )
        if queue.get("oneMutationPerCycle") is not True:
            self.add(
                CONTINUATION,
                f"{path}.queue.oneMutationPerCycle",
                "a cycle may perform only one mutation",
            )
        if queue.get("durable") is not True or queue.get("delivery") != "at-least-once":
            self.add(
                CONTINUATION,
                f"{path}.queue",
                "autonomous continuation requires durable at-least-once delivery",
            )
        if set(queue.get("idempotencyBindings", [])) != REQUIRED_IDEMPOTENCY_BINDINGS:
            self.add(
                CONTINUATION,
                f"{path}.queue.idempotencyBindings",
                "all idempotency bindings are required for replay-safe delivery",
            )
        if queue.get("resumeFromCheckpoint") is not True:
            self.add(
                CONTINUATION,
                f"{path}.queue.resumeFromCheckpoint",
                "continuation must resume from a durable checkpoint",
            )

        liveness = doc.get("executionLiveness", {})
        primary = liveness.get("primaryTrigger", {})
        watchdog = liveness.get("watchdog", {})
        dispatcher = role_map.get("dispatcher", {})
        if primary.get("principal") != dispatcher.get("principal"):
            self.add(
                SEPARATION,
                f"{path}.executionLiveness.primaryTrigger.principal",
                "primary trigger must be controlled by the declared dispatcher principal",
            )
        if dispatcher.get("workspaceIsolation") != "protected-service":
            self.add(
                SEPARATION,
                f"{path}.fleet.roles",
                "dispatcher requires protected-service isolation",
            )
        if primary.get("principal") == watchdog.get("principal"):
            self.add(
                SEPARATION,
                f"{path}.executionLiveness.watchdog.principal",
                "watchdog and primary trigger principals must differ",
            )
        for object_name, item, fields in (
            ("primaryTrigger", primary, ("protected",)),
            ("watchdog", watchdog, ("protected", "triggerOnSilence")),
        ):
            for field in fields:
                if item.get(field) is not True:
                    self.add(
                        BOUNDARY,
                        f"{path}.executionLiveness.{object_name}.{field}",
                        "execution trigger boundary must be protected and self-recovering",
                    )
        for field, expected in (
            ("independentPrincipals", True),
            ("manualDispatchProvesLiveness", False),
            ("perRepositoryIsolation", True),
            ("unrelatedFailureBlocksMerge", False),
            ("aggregateStatusAuthoritative", False),
        ):
            if liveness.get(field) is not expected:
                self.add(
                    BOUNDARY,
                    f"{path}.executionLiveness.{field}",
                    "unsafe execution-liveness boundary",
                )
        if liveness.get("missedTriggerStatus") != "degraded":
            self.add(
                CONTINUATION,
                f"{path}.executionLiveness.missedTriggerStatus",
                "a missed trigger must be visible as degraded status",
            )
        registry = liveness.get("registry", {})
        if set(registry.get("requiredBindings", [])) != REQUIRED_REGISTRY_BINDINGS:
            self.add(
                BOUNDARY,
                f"{path}.executionLiveness.registry.requiredBindings",
                "protected registry must bind every repository execution decision",
            )
        for field in ("protected", "singleSource", "driftCheck"):
            if registry.get(field) is not True:
                self.add(
                    BOUNDARY,
                    f"{path}.executionLiveness.registry.{field}",
                    "registry authority must be protected, singular, and drift checked",
                )
        canary = liveness.get("canary", {})
        if canary.get("manualDispatchCounts") is not False:
            self.add(
                CONTINUATION,
                f"{path}.executionLiveness.canary.manualDispatchCounts",
                "manual dispatch is diagnostic evidence, not a liveness proof",
            )
        if set(canary.get("requiredReceipts", [])) != REQUIRED_CANARY_RECEIPTS:
            self.add(
                CONTINUATION,
                f"{path}.executionLiveness.canary.requiredReceipts",
                "canary must prove the complete protected execution path",
            )

        pipeline = doc.get("pipeline", {})
        gate_ids = {
            gate.get("id") for gate in pipeline.get("requiredGates", []) if isinstance(gate, dict)
        }
        if not REQUIRED_GATES <= gate_ids:
            self.add(
                HEAD,
                f"{path}.pipeline.requiredGates",
                f"missing protected gates: {sorted(REQUIRED_GATES - gate_ids)}",
            )
        for gate in pipeline.get("requiredGates", []):
            if isinstance(gate, dict) and (
                gate.get("protected") is not True or gate.get("failClosed") is not True
            ):
                self.add(
                    HEAD,
                    f"{path}.pipeline.requiredGates",
                    "every gate must be protected and fail closed",
                )

        publication = doc.get("publication", {})
        if set(publication.get("bindings", [])) != REQUIRED_BINDINGS:
            self.add(
                HEAD,
                f"{path}.publication.bindings",
                "approval must bind repository, PR, head, base, ticket, grant, profile, and actor",
            )
        if not REQUIRED_CHECKS <= set(publication.get("requiredChecks", [])):
            self.add(
                HEAD,
                f"{path}.publication.requiredChecks",
                "governance, tests, security, and validator checks are required",
            )
        for field, expected in (
            ("sameRepositoryOnly", True),
            ("recheckBaseBeforeMerge", True),
            ("autonomousMerge", True),
            ("nativeAutoMerge", False),
            ("directDefaultBranchPush", False),
            ("deleteBranchAfterMerge", True),
            ("postMergeReadBack", True),
        ):
            if publication.get(field) is not expected:
                self.add(HEAD, f"{path}.publication.{field}", "unsafe publication boundary")
        if publication.get("mergeMode") != "protected-explicit":
            self.add(
                HEAD,
                f"{path}.publication.mergeMode",
                "native queued auto-merge cannot replace protected exact-head publication",
            )

        if set(doc.get("receipts", {}).get("required", [])) != REQUIRED_RECEIPTS:
            self.add(
                CONTINUATION, f"{path}.receipts.required", "all lifecycle receipts are required"
            )
        continuation = doc.get("continuation", {})
        if not REQUIRED_STOP_CONDITIONS <= set(continuation.get("stopConditions", [])):
            self.add(
                CONTINUATION,
                f"{path}.continuation.stopConditions",
                "mandatory fail-closed stop conditions are missing",
            )
        for field in ("enabled", "nextTaskWithoutHumanApproval", "closeOnlyAfterReadBack"):
            if continuation.get(field) is not True:
                self.add(
                    CONTINUATION,
                    f"{path}.continuation.{field}",
                    "bounded autonomous continuation requires true",
                )

        self.verify_selected_profile(doc, path)

    def verify_selected_profile(self, doc: dict[str, Any], path: str) -> None:
        profile_path = self.profile_path
        if profile_path is None:
            profile_path = DEFAULT_PROFILE
        if not profile_path.is_file():
            self.add(PROFILE, f"{path}.subject.profile", "selected profile file is unavailable")
            return
        try:
            raw = profile_path.read_bytes()
            profile = json.loads(raw)
        except (OSError, json.JSONDecodeError) as error:
            self.add(PROFILE, f"{path}.subject.profile", f"cannot read selected profile: {error}")
            return
        profile_validator = Validator(profile_path=None)
        before = len(profile_validator.findings)
        if (
            profile_validator.profile_shape(profile, "$.profile")
            and len(profile_validator.findings) == before
        ):
            profile_validator.profile_semantics(profile, "$.profile")
        for finding in profile_validator.findings:
            self.add(PROFILE, finding.path, finding.message)
        selected = doc.get("subject", {}).get("profile", {})
        actual_digest = f"sha256:{hashlib.sha256(raw).hexdigest()}"
        if selected.get("id") != profile.get("id") or selected.get("version") != profile.get(
            "version"
        ):
            self.add(
                PROFILE,
                f"{path}.subject.profile",
                "selected profile ID/version does not match the profile file",
            )
        if selected.get("digest") != actual_digest:
            self.add(
                PROFILE,
                f"{path}.subject.profile.digest",
                "selected profile digest does not match exact bytes",
            )

    def profile_semantics(self, doc: dict[str, Any], path: str) -> None:
        expected = {
            "dispatch": ("dispatcher", "protected-dispatch"),
            "observe": ("observer", "read-only"),
            "evidence": ("observer", "read-only"),
            "plan": ("planner", "propose-only"),
            "implement": ("implementer", "candidate-write"),
            "validate": ("validator", "validate-only"),
            "publish": ("publisher", "protected-publish"),
            "audit": ("auditor", "append-only-audit"),
        }
        stages = set()
        owners = set(doc.get("ownership", {}).get("runtimeOwners", []))
        for index, binding in enumerate(doc.get("bindings", [])):
            if not isinstance(binding, dict):
                continue
            stage = binding.get("stage")
            stages.add(stage)
            if stage in expected and (binding.get("role"), binding.get("mode")) != expected[stage]:
                self.add(
                    PROFILE,
                    f"{path}.bindings[{index}]",
                    "stage role/mode crosses the profile authority boundary",
                )
            product = binding.get("product")
            if (
                isinstance(product, str)
                and not product.startswith("wellmanifest/")
                and product not in owners
            ):
                self.add(
                    PROFILE,
                    f"{path}.bindings[{index}].product",
                    "product is not declared as a runtime owner",
                )
        if stages != set(expected):
            self.add(
                PROFILE,
                f"{path}.bindings",
                "profile must cover all lifecycle stages; missing "
                f"{sorted(set(expected) - stages)}",
            )


def parse_at(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("evaluation time must include an offset")
    return parsed


def apply_invalid_case(
    document: dict[str, Any], path: Path
) -> tuple[dict[str, Any] | None, list[Finding]]:
    validator = Validator()
    fields = ("schema", "base", "mutations", "expectedCodes")
    if not validator.closed(document, "$", fields, fields):
        return None, validator.findings
    if document.get("schema") != "wellmanifest.autonomy/invalid-case/v1":
        validator.add(SYNTAX, "$.schema", "unknown invalid-case version")
        return None, validator.findings
    base_value = document.get("base")
    if not isinstance(base_value, str) or not base_value:
        validator.add(SYNTAX, "$.base", "expected a relative base path")
        return None, validator.findings
    examples_root = path.parent.parent.resolve()
    base_path = (path.parent / base_value).resolve()
    try:
        base_path.relative_to(examples_root)
    except ValueError:
        validator.add(RISK, "$.base", "base path escapes the examples root")
        return None, validator.findings
    if base_path.parent.name != "valid":
        validator.add(SYNTAX, "$.base", "base must resolve inside examples/valid")
        return None, validator.findings
    try:
        candidate = json.loads(base_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        validator.add(SYNTAX, "$.base", f"cannot load base manifest: {error}")
        return None, validator.findings
    mutations = document.get("mutations")
    if not isinstance(mutations, list) or not mutations:
        validator.add(SYNTAX, "$.mutations", "expected at least one mutation")
        return None, validator.findings
    for index, mutation in enumerate(mutations):
        item_path = f"$.mutations[{index}]"
        if not validator.closed(
            mutation, item_path, ("op", "path", "value"), ("op", "path", "value")
        ):
            continue
        if mutation.get("op") != "replace":
            validator.add(RISK, f"{item_path}.op", "invalid cases allow replace only")
            continue
        pointer = mutation.get("path")
        if not isinstance(pointer, str) or not pointer.startswith("/") or pointer == "/":
            validator.add(SYNTAX, f"{item_path}.path", "expected a non-root JSON pointer")
            continue
        parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]
        target: Any = candidate
        try:
            for part in parts[:-1]:
                target = target[int(part)] if isinstance(target, list) else target[part]
            leaf = parts[-1]
            if isinstance(target, list):
                target[int(leaf)] = copy.deepcopy(mutation.get("value"))
            else:
                if leaf not in target:
                    raise KeyError(leaf)
                target[leaf] = copy.deepcopy(mutation.get("value"))
        except (KeyError, IndexError, ValueError, TypeError):
            validator.add(SYNTAX, f"{item_path}.path", "pointer does not select an existing value")
    expected = validator.string_set(document.get("expectedCodes"), "$.expectedCodes", minimum=1)
    if expected is not None:
        unknown = set(expected) - {SYNTAX, POLICY, BOUNDARY}
        if unknown:
            validator.add(SYNTAX, "$.expectedCodes", f"unknown diagnostic codes: {sorted(unknown)}")
    return candidate, validator.findings


def validate_document(
    document: Any,
    *,
    at: datetime | None = None,
    profile_path: Path | None = DEFAULT_PROFILE,
    path: str = "$",
) -> list[Finding]:
    validator = Validator(at=at, profile_path=profile_path)
    if not isinstance(document, dict):
        validator.add(SYNTAX, path, "expected a JSON object")
        return validator.findings
    schema = document.get("schema")
    if schema == "wellmanifest.autonomy/manifest/v3":
        before = len(validator.findings)
        if validator.manifest_shape(document, path) and len(validator.findings) == before:
            validator.manifest_semantics(document, path)
    elif schema == "wellmanifest.autonomy/profile/v3":
        before = len(validator.findings)
        if validator.profile_shape(document, path) and len(validator.findings) == before:
            validator.profile_semantics(document, path)
    else:
        validator.add(SYNTAX, f"{path}.schema", "unknown document schema")
    return sorted(
        validator.findings, key=lambda finding: (finding.code, finding.path, finding.message)
    )


def load_and_validate(
    path: Path,
    *,
    at: datetime | None = None,
    profile_path: Path | None = DEFAULT_PROFILE,
) -> list[Finding]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [Finding(SYNTAX, "$", f"cannot load JSON: {error}", "error")]
    overlay_findings: list[Finding] = []
    if (
        isinstance(document, dict)
        and document.get("schema") == "wellmanifest.autonomy/invalid-case/v1"
    ):
        document, overlay_findings = apply_invalid_case(document, path)
        if document is None:
            return overlay_findings
    return overlay_findings + validate_document(document, at=at, profile_path=profile_path)


def iter_json_paths(paths: list[Path]) -> list[Path]:
    discovered: list[Path] = []
    for path in paths:
        if path.is_dir():
            discovered.extend(sorted(path.rglob("*.json")))
        else:
            discovered.append(path)
    return discovered


def render(path: Path, findings: list[Finding], output_format: str) -> str:
    if output_format == "json":
        payload = {
            "schema": "wellmanifest.autonomy/findings/v1",
            "producer": "wellmanifest.autonomy-check",
            "path": path.as_posix(),
            "valid": not findings,
            "findings": [asdict(finding) for finding in findings],
        }
        return json.dumps(payload, sort_keys=True)
    if not findings:
        return f"PASS {path.as_posix()}"
    return "\n".join(
        f"{finding.severity.upper()} {finding.code} "
        f"{path.as_posix()}:{finding.path} {finding.message}"
        for finding in findings
    )


def self_test() -> int:
    valid_path = ROOT / "examples" / "valid" / "project.autonomy.json"
    valid_findings = load_and_validate(valid_path)
    if valid_findings:
        print(render(valid_path.relative_to(ROOT), valid_findings, "text"), file=sys.stderr)
        return 1
    for path in sorted((ROOT / "examples" / "invalid").glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        expected = set(case["expectedCodes"])
        findings = load_and_validate(path)
        observed = {finding.code for finding in findings}
        if not expected <= observed:
            print(
                f"FAIL {path.relative_to(ROOT)} expected {sorted(expected)}, "
                f"observed {sorted(observed)}",
                file=sys.stderr,
            )
            return 1
    profile = json.loads(DEFAULT_PROFILE.read_text(encoding="utf-8"))
    profile_findings = validate_document(profile, profile_path=None)
    if profile_findings:
        print(render(DEFAULT_PROFILE.relative_to(ROOT), profile_findings, "text"), file=sys.stderr)
        return 1
    print("PASS autonomy self-test")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="autonomy-check")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser(
        "validate", help="validate manifests, profiles, or directories"
    )
    validate_parser.add_argument("paths", nargs="+", type=Path)
    validate_parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    validate_parser.add_argument("--at", help="evaluate grant activity at an RFC 3339 time")
    validate_parser.add_argument("--format", choices=("text", "json"), default="text")
    subparsers.add_parser("self-test", help="run bundled positive and negative conformance cases")
    args = parser.parse_args(argv)

    if args.command == "self-test":
        return self_test()

    try:
        at = parse_at(args.at)
    except ValueError as error:
        parser.error(str(error))
    failed = False
    for path in iter_json_paths(args.paths):
        findings = load_and_validate(path, at=at, profile_path=args.profile)
        print(render(path, findings, args.format))
        failed = failed or bool(findings)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
