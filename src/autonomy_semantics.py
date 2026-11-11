"""Cross-field semantic invariants for Wellmanifest Autonomy manifests."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from autonomy_constants import (
    BOUNDARY,
    CONTINUATION,
    DIMENSIONS,
    GRANT,
    MANDATORY_EXCLUDED_EFFECTS,
    REQUIRED_ACTIONS,
    REQUIRED_ALREADY_APPLIED_BINDINGS,
    REQUIRED_CANARY_RECEIPTS,
    REQUIRED_EFFECT_BINDINGS,
    REQUIRED_IDEMPOTENCY_BINDINGS,
    REQUIRED_INVOCATION_BINDINGS,
    REQUIRED_REGISTRY_BINDINGS,
    RISK,
    RISK_ORDER,
    ROLE_AUTHORITY_CEILINGS,
    ROLES,
    SEPARATION,
)


def _str_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


class ValidatorSemanticsMixin:
    at: datetime | None

    def manifest_semantics(self, doc: dict[str, Any], path: str) -> None:
        if doc.get("status") != "active":
            self.add(  # type: ignore[attr-defined]
                GRANT, f"{path}.status", "only an active manifest authorizes autonomous effects"
            )

        subject = doc.get("subject", {}) if isinstance(doc.get("subject"), dict) else {}
        grant = doc.get("grant", {}) if isinstance(doc.get("grant"), dict) else {}
        scope = grant.get("scope", {}) if isinstance(grant.get("scope"), dict) else {}
        constraints = (
            grant.get("constraints", {}) if isinstance(grant.get("constraints"), dict) else {}
        )
        if subject.get("repository") not in _str_set(scope.get("repositories")):
            self.add(  # type: ignore[attr-defined]
                GRANT, f"{path}.grant.scope.repositories", "subject repository is outside the grant"
            )
        if subject.get("defaultBranch") not in _str_set(scope.get("branches")):
            self.add(  # type: ignore[attr-defined]
                GRANT, f"{path}.grant.scope.branches", "default branch is outside the grant"
            )
        actions = _str_set(scope.get("actions"))
        missing_actions = REQUIRED_ACTIONS - actions
        if missing_actions:
            self.add(  # type: ignore[attr-defined]
                GRANT,
                f"{path}.grant.scope.actions",
                f"missing autonomous lifecycle actions: {sorted(missing_actions)}",
            )
        if (
            constraints.get("selfExtension") is not False
            or constraints.get("selfRenewal") is not False
        ):
            self.add(  # type: ignore[attr-defined]
                GRANT,
                f"{path}.grant.constraints",
                "grant self-extension and self-renewal are forbidden",
            )

        times = [
            self.timestamp(grant.get(field), f"{path}.grant.{field}")  # type: ignore[attr-defined]
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
                self.add(  # type: ignore[attr-defined]
                    GRANT, f"{path}.grant", "expected issuedAt <= notBefore < reviewAt < expiresAt"
                )
            if self.at is not None and not (not_before <= self.at < expires):
                self.add(  # type: ignore[attr-defined]
                    GRANT, f"{path}.grant", "grant is not active at the requested evaluation time"
                )

        fleet = doc.get("fleet", {}) if isinstance(doc.get("fleet"), dict) else {}
        raw_roles = fleet.get("roles", [])
        roles = raw_roles if isinstance(raw_roles, list) else []
        role_map = {
            role.get("role"): role
            for role in roles
            if isinstance(role, dict) and isinstance(role.get("role"), str)
        }
        if set(role_map) != ROLES or len(roles) != len(ROLES):
            self.add(  # type: ignore[attr-defined]
                SEPARATION, f"{path}.fleet.roles", "exactly one of each normative role is required"
            )
        ids = [
            role.get("id")
            for role in roles
            if isinstance(role, dict) and isinstance(role.get("id"), str)
        ]
        if len(ids) != len(set(ids)):
            self.add(SEPARATION, f"{path}.fleet.roles", "role IDs must be unique")  # type: ignore[attr-defined]
        for role_name, role in role_map.items():
            if role_name not in ROLE_AUTHORITY_CEILINGS:
                continue
            authorities = _str_set(role.get("authorities"))
            forbidden = _str_set(role.get("forbiddenAuthorities"))
            overlap = authorities & forbidden
            if overlap:
                self.add(  # type: ignore[attr-defined]
                    SEPARATION,
                    f"{path}.fleet.roles",
                    f"{role_name} both holds and forbids {sorted(overlap)}",
                )
            excess = authorities - ROLE_AUTHORITY_CEILINGS[role_name]
            if excess:
                self.add(  # type: ignore[attr-defined]
                    SEPARATION,
                    f"{path}.fleet.roles",
                    f"{role_name} exceeds its authority ceiling: {sorted(excess)}",
                )

        critical_roles = [role_map.get(name) for name in ("implementer", "validator", "publisher")]
        if all(critical_roles):
            principals = [
                role.get("principal")
                for role in critical_roles
                if role and isinstance(role.get("principal"), str)
            ]
            if len(set(principals)) != 3:
                self.add(  # type: ignore[attr-defined]
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
                    self.add(  # type: ignore[attr-defined]
                        SEPARATION, f"{path}.fleet.roles", f"{name} requires {expected} isolation"
                    )

            ids_by_role = {name: role_map[name].get("id") for name in expected_isolation}
            if all(isinstance(val, str) for val in ids_by_role.values()):
                required_pairs = {
                    frozenset((ids_by_role["implementer"], ids_by_role["validator"])),
                    frozenset((ids_by_role["implementer"], ids_by_role["publisher"])),
                    frozenset((ids_by_role["validator"], ids_by_role["publisher"])),
                }
                observed_pairs = set()
                sep_rules = fleet.get("separation", [])
                for rule in sep_rules if isinstance(sep_rules, list) else []:
                    if (
                        isinstance(rule, dict)
                        and _str_set(rule.get("dimensions")) == DIMENSIONS
                        and isinstance(rule.get("left"), str)
                        and isinstance(rule.get("right"), str)
                    ):
                        observed_pairs.add(frozenset((rule["left"], rule["right"])))
                if not required_pairs <= observed_pairs:
                    self.add(  # type: ignore[attr-defined]
                        SEPARATION,
                        f"{path}.fleet.separation",
                        "all critical role pairs need four-dimensional separation",
                    )

        risk = doc.get("riskPolicy", {}) if isinstance(doc.get("riskPolicy"), dict) else {}
        missing_exclusions = MANDATORY_EXCLUDED_EFFECTS - _str_set(risk.get("excludedEffects"))
        if missing_exclusions:
            self.add(  # type: ignore[attr-defined]
                RISK,
                f"{path}.riskPolicy.excludedEffects",
                f"missing mandatory exclusions: {sorted(missing_exclusions)}",
            )
        ceiling = scope.get("riskCeiling")
        autonomous = _str_set(risk.get("autonomousTiers"))
        if isinstance(ceiling, str) and ceiling in RISK_ORDER and any(
            RISK_ORDER.get(tier, 99) > RISK_ORDER[ceiling] for tier in autonomous
        ):
            self.add(  # type: ignore[attr-defined]
                RISK,
                f"{path}.riskPolicy.autonomousTiers",
                "autonomous tier exceeds the grant ceiling",
            )
        if _str_set(risk.get("escalatedTiers")) != {"high", "critical"}:
            self.add(  # type: ignore[attr-defined]
                RISK, f"{path}.riskPolicy.escalatedTiers", "high and critical work must escalate"
            )

        queue = doc.get("queue", {}) if isinstance(doc.get("queue"), dict) else {}
        if not {"human", "autonomy-frontier"} <= _str_set(queue.get("humanBoundaryLabels")):
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.queue.humanBoundaryLabels",
                "human and autonomy-frontier labels are required",
            )
        if queue.get("oneMutationPerCycle") is not True:
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.queue.oneMutationPerCycle",
                "a cycle may perform only one mutation",
            )
        if queue.get("durable") is not True or queue.get("delivery") != "at-least-once":
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.queue",
                "autonomous continuation requires durable at-least-once delivery",
            )
        if _str_set(queue.get("idempotencyBindings")) != REQUIRED_IDEMPOTENCY_BINDINGS:
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.queue.idempotencyBindings",
                "all idempotency bindings are required for replay-safe delivery",
            )
        if queue.get("resumeFromCheckpoint") is not True:
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.queue.resumeFromCheckpoint",
                "continuation must resume from a durable checkpoint",
            )
        reconciliation = (
            queue.get("effectReconciliation", {})
            if isinstance(queue.get("effectReconciliation"), dict)
            else {}
        )
        if (
            reconciliation.get("mode") != "at-most-one-authoritative-effect"
            or reconciliation.get("externalReadBack") is not True
            or reconciliation.get("duplicateOutcome") != "already-applied"
            or _str_set(reconciliation.get("successOutcomes")) != {"applied", "already-applied"}
        ):
            self.add(  # type: ignore[attr-defined]
                BOUNDARY,
                f"{path}.queue.effectReconciliation",
                "effect success requires one externally reconciled authoritative result",
            )
        if _str_set(reconciliation.get("requiredBindings")) != REQUIRED_EFFECT_BINDINGS:
            self.add(  # type: ignore[attr-defined]
                BOUNDARY,
                f"{path}.queue.effectReconciliation.requiredBindings",
                "every effect receipt must carry the complete idempotency subject",
            )
        if (
            _str_set(reconciliation.get("alreadyAppliedRequiredBindings"))
            != REQUIRED_ALREADY_APPLIED_BINDINGS
        ):
            self.add(  # type: ignore[attr-defined]
                BOUNDARY,
                f"{path}.queue.effectReconciliation.alreadyAppliedRequiredBindings",
                "already-applied publication requires exact external approval and merge bindings",
            )
        if reconciliation.get("repeatReviewOrMerge") is not False:
            self.add(  # type: ignore[attr-defined]
                BOUNDARY,
                f"{path}.queue.effectReconciliation.repeatReviewOrMerge",
                "an already-applied subject must not receive another review or merge",
            )
        for field in (
            "closedUnmergedOutcome",
            "staleSubjectOutcome",
            "ambiguousReceiptOutcome",
        ):
            if reconciliation.get(field) != "failed":
                self.add(  # type: ignore[attr-defined]
                    BOUNDARY,
                    f"{path}.queue.effectReconciliation.{field}",
                    "missing, stale, ambiguous, or unmerged evidence must fail closed",
                )

        liveness = (
            doc.get("executionLiveness", {})
            if isinstance(doc.get("executionLiveness"), dict)
            else {}
        )
        primary = (
            liveness.get("primaryTrigger", {})
            if isinstance(liveness.get("primaryTrigger"), dict)
            else {}
        )
        watchdog = (
            liveness.get("watchdog", {}) if isinstance(liveness.get("watchdog"), dict) else {}
        )
        dispatcher = role_map.get("dispatcher", {})
        if primary.get("principal") != dispatcher.get("principal"):
            self.add(  # type: ignore[attr-defined]
                SEPARATION,
                f"{path}.executionLiveness.primaryTrigger.principal",
                "primary trigger must be controlled by the declared dispatcher principal",
            )
        if dispatcher.get("workspaceIsolation") != "protected-service":
            self.add(  # type: ignore[attr-defined]
                SEPARATION,
                f"{path}.fleet.roles",
                "dispatcher requires protected-service isolation",
            )
        if primary.get("principal") == watchdog.get("principal"):
            self.add(  # type: ignore[attr-defined]
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
                    self.add(  # type: ignore[attr-defined]
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
                self.add(  # type: ignore[attr-defined]
                    BOUNDARY,
                    f"{path}.executionLiveness.{field}",
                    "unsafe execution-liveness boundary",
                )
        if liveness.get("missedTriggerStatus") != "degraded":
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.executionLiveness.missedTriggerStatus",
                "a missed trigger must be visible as degraded status",
            )
        registry = (
            liveness.get("registry", {}) if isinstance(liveness.get("registry"), dict) else {}
        )
        if _str_set(registry.get("requiredBindings")) != REQUIRED_REGISTRY_BINDINGS:
            self.add(  # type: ignore[attr-defined]
                BOUNDARY,
                f"{path}.executionLiveness.registry.requiredBindings",
                "protected registry must bind every repository execution decision",
            )
        for field in ("protected", "singleSource", "driftCheck"):
            if registry.get(field) is not True:
                self.add(  # type: ignore[attr-defined]
                    BOUNDARY,
                    f"{path}.executionLiveness.registry.{field}",
                    "registry authority must be protected, singular, and drift checked",
                )
        canary = liveness.get("canary", {}) if isinstance(liveness.get("canary"), dict) else {}
        if canary.get("manualDispatchCounts") is not False:
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.executionLiveness.canary.manualDispatchCounts",
                "manual dispatch is diagnostic evidence, not a liveness proof",
            )
        if _str_set(canary.get("requiredReceipts")) != REQUIRED_CANARY_RECEIPTS:
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.executionLiveness.canary.requiredReceipts",
                "canary must prove the complete protected execution path",
            )
        heartbeat = (
            liveness.get("heartbeat", {}) if isinstance(liveness.get("heartbeat"), dict) else {}
        )
        for field, expected in (
            ("receiptRequired", True),
            ("protectedMonitor", True),
            ("missedCycleReceiptRequired", True),
            ("manualRecoveryRestoresLiveness", False),
        ):
            if heartbeat.get(field) is not expected:
                self.add(  # type: ignore[attr-defined]
                    BOUNDARY,
                    f"{path}.executionLiveness.heartbeat.{field}",
                    "scheduler heartbeat must remain externally observable "
                    "and independent of recovery",
                )
        if heartbeat.get("lateDeliveryPolicy") != "deduplicate-with-recovery":
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.executionLiveness.heartbeat.lateDeliveryPolicy",
                "late scheduled delivery and recovery must converge without duplicate effects",
            )
        interval = heartbeat.get("expectedIntervalSeconds")
        grace = heartbeat.get("deliveryGraceSeconds")
        silence = watchdog.get("maxSilenceSeconds")
        if all(
            isinstance(item, int) and not isinstance(item, bool)
            for item in (interval, grace, silence)
        ) and silence > interval + grace:  # type: ignore[operator]
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.executionLiveness.watchdog.maxSilenceSeconds",
                "watchdog detection must not exceed the heartbeat interval plus delivery grace",
            )

        invocation = (
            liveness.get("invocationIdentity", {})
            if isinstance(liveness.get("invocationIdentity"), dict)
            else {}
        )
        for field in (
            "correlationRequired",
            "providerRunIdentityRequired",
            "preDispatchBoundaryRequired",
            "postBoundaryOnly",
            "matrixChildCorrelationRequired",
        ):
            if invocation.get(field) is not True:
                self.add(  # type: ignore[attr-defined]
                    BOUNDARY,
                    f"{path}.executionLiveness.invocationIdentity.{field}",
                    "provider run selection requires protected exact invocation identity",
                )
        if _str_set(invocation.get("requiredBindings")) != REQUIRED_INVOCATION_BINDINGS:
            self.add(  # type: ignore[attr-defined]
                BOUNDARY,
                f"{path}.executionLiveness.invocationIdentity.requiredBindings",
                "run selection must bind strategy, repository, target, exact head, and correlation",
            )
        if invocation.get("ambiguousRunOutcome") != "failed":
            self.add(  # type: ignore[attr-defined]
                BOUNDARY,
                f"{path}.executionLiveness.invocationIdentity.ambiguousRunOutcome",
                "an ambiguous or pre-boundary run candidate must fail closed",
            )

        self._pipeline_publication_semantics(doc, path)  # type: ignore[attr-defined]
        self.verify_selected_profile(doc, path)  # type: ignore[attr-defined]
