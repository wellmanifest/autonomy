"""Primitive field validators and core manifest shapes for Wellmanifest Autonomy."""

from __future__ import annotations

import math
import re
from collections.abc import Iterable
from datetime import datetime
from typing import Any
from urllib.parse import urlsplit

from autonomy_constants import (
    AUTHORITIES,
    CRITICAL_CODES,
    DIGEST_RE,
    DIMENSIONS,
    ENV_RE,
    ID_RE,
    POLICY,
    REPOSITORY_RE,
    REQUIRED_ALREADY_APPLIED_BINDINGS,
    REQUIRED_EFFECT_BINDINGS,
    REQUIRED_IDEMPOTENCY_BINDINGS,
    RFC3339_OFFSET_RE,
    ROLES,
    SEMVER_RE,
    SEPARATION,
    SHA_RE,
    SYNTAX,
    URI_RE,
    Finding,
)


class ValidatorPrimitivesMixin:
    findings: list[Finding]

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
        numeric = float(value)
        if not math.isfinite(numeric) or not minimum < numeric <= maximum:
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
        if RFC3339_OFFSET_RE.fullmatch(value) is None:
            self.add(SYNTAX, path, "expected an RFC 3339 date-time")
            return None
        normalized = f"{value[:-1]}+00:00" if value.endswith(("Z", "z")) else value
        try:
            parsed = datetime.fromisoformat(normalized)
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
        if doc["$schema"] != "https://wellmanifest.com/schemas/autonomy-manifest/v6":
            self.add(SYNTAX, f"{path}.$schema", "unknown schema URI")
        if doc["schema"] != "wellmanifest.autonomy/manifest/v6":
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
        self.execution_liveness_shape(doc["executionLiveness"], f"{path}.executionLiveness")  # type: ignore[attr-defined]
        self.pipeline_shape(doc["pipeline"], f"{path}.pipeline")  # type: ignore[attr-defined]
        self.change_control_shape(doc["changeControl"], f"{path}.changeControl")  # type: ignore[attr-defined]
        self.publication_shape(doc["publication"], f"{path}.publication")  # type: ignore[attr-defined]
        self.receipts_shape(doc["receipts"], f"{path}.receipts")  # type: ignore[attr-defined]
        self.continuation_shape(doc["continuation"], f"{path}.continuation")  # type: ignore[attr-defined]
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
                        segments = item.replace("\\", "/").split("/")
                        if item.startswith(("/", "\\")) or "\\" in item or ".." in segments:
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
            "effectReconciliation",
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

        reconciliation = value["effectReconciliation"]
        reconciliation_fields = (
            "mode",
            "successOutcomes",
            "duplicateOutcome",
            "externalReadBack",
            "requiredBindings",
            "alreadyAppliedRequiredBindings",
            "repeatReviewOrMerge",
            "closedUnmergedOutcome",
            "staleSubjectOutcome",
            "ambiguousReceiptOutcome",
        )
        if self.closed(
            reconciliation,
            f"{path}.effectReconciliation",
            reconciliation_fields,
            reconciliation_fields,
        ):
            if reconciliation["mode"] != "at-most-one-authoritative-effect":
                self.add(
                    POLICY,
                    f"{path}.effectReconciliation.mode",
                    "effects must converge to one authoritative result",
                )
            self.string_set(
                reconciliation["successOutcomes"],
                f"{path}.effectReconciliation.successOutcomes",
                minimum=2,
                allowed={"applied", "already-applied"},
            )
            if reconciliation["duplicateOutcome"] != "already-applied":
                self.add(
                    POLICY,
                    f"{path}.effectReconciliation.duplicateOutcome",
                    "an exact duplicate must reconcile as already-applied",
                )
            self.boolean(
                reconciliation["externalReadBack"],
                f"{path}.effectReconciliation.externalReadBack",
            )
            self.string_set(
                reconciliation["requiredBindings"],
                f"{path}.effectReconciliation.requiredBindings",
                minimum=1,
                allowed=REQUIRED_EFFECT_BINDINGS,
            )
            self.string_set(
                reconciliation["alreadyAppliedRequiredBindings"],
                f"{path}.effectReconciliation.alreadyAppliedRequiredBindings",
                minimum=1,
                allowed=REQUIRED_ALREADY_APPLIED_BINDINGS,
            )
            self.boolean(
                reconciliation["repeatReviewOrMerge"],
                f"{path}.effectReconciliation.repeatReviewOrMerge",
            )
            for field in (
                "closedUnmergedOutcome",
                "staleSubjectOutcome",
                "ambiguousReceiptOutcome",
            ):
                if reconciliation[field] != "failed":
                    self.add(
                        POLICY,
                        f"{path}.effectReconciliation.{field}",
                        "unverified effect reconciliation must fail closed",
                    )
