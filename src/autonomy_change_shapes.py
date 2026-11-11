"""Change-control shape validation for Wellmanifest Autonomy."""

from __future__ import annotations

from typing import Any

from autonomy_constants import (
    BOUNDARY,
    CONTINUATION,
    HEAD,
    POLICY,
    PROVIDER_COUPLED_READ_BACKS,
    REQUIRED_BINDINGS,
    REQUIRED_CHECK_PROVENANCE_BINDINGS,
    REQUIRED_CHECKS,
    REQUIRED_CONSUMER_SURFACES,
    REQUIRED_GATES,
    REQUIRED_POLICY_REBINDINGS,
    REQUIRED_RECEIPTS,
    REQUIRED_STOP_CONDITIONS,
    REQUIRED_SUPERSESSION_BINDINGS,
    SUPERSESSION_CLOSURE_MODES,
)


def _str_items(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


class ValidatorChangeShapesMixin:
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
        if not self.closed(value, path, fields, fields):  # type: ignore[attr-defined]
            return
        for field, (minimum, maximum) in limits.items():
            self.integer(value[field], f"{path}.{field}", minimum, maximum)  # type: ignore[attr-defined]
        self.number(value["maxCostUsdPerCycle"], f"{path}.maxCostUsdPerCycle", 0, 100)  # type: ignore[attr-defined]

    def _pipeline_publication_semantics(self, doc: dict[str, Any], path: str) -> None:
        pipeline = doc.get("pipeline", {}) if isinstance(doc.get("pipeline"), dict) else {}
        raw_gates = pipeline.get("requiredGates", [])
        gates = raw_gates if isinstance(raw_gates, list) else []
        gate_ids = {
            gate["id"]
            for gate in gates
            if isinstance(gate, dict) and isinstance(gate.get("id"), str)
        }
        if not REQUIRED_GATES <= gate_ids:
            self.add(  # type: ignore[attr-defined]
                HEAD,
                f"{path}.pipeline.requiredGates",
                f"missing protected gates: {sorted(REQUIRED_GATES - gate_ids)}",
            )
        for gate in gates:
            if isinstance(gate, dict) and (
                gate.get("protected") is not True or gate.get("failClosed") is not True
            ):
                self.add(  # type: ignore[attr-defined]
                    HEAD,
                    f"{path}.pipeline.requiredGates",
                    "every gate must be protected and fail closed",
                )

        publication = (
            doc.get("publication", {}) if isinstance(doc.get("publication"), dict) else {}
        )
        if _str_items(publication.get("bindings")) != REQUIRED_BINDINGS:
            self.add(  # type: ignore[attr-defined]
                HEAD,
                f"{path}.publication.bindings",
                "approval must bind repository, PR, head, base, ticket, grant, profile, and actor",
            )
        if not REQUIRED_CHECKS <= _str_items(publication.get("requiredChecks")):
            self.add(  # type: ignore[attr-defined]
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
                self.add(HEAD, f"{path}.publication.{field}", "unsafe publication boundary")  # type: ignore[attr-defined]
        if publication.get("mergeMode") != "protected-explicit":
            self.add(  # type: ignore[attr-defined]
                HEAD,
                f"{path}.publication.mergeMode",
                "native queued auto-merge cannot replace protected exact-head publication",
            )

        receipts = doc.get("receipts", {}) if isinstance(doc.get("receipts"), dict) else {}
        if _str_items(receipts.get("required")) != REQUIRED_RECEIPTS:
            self.add(  # type: ignore[attr-defined]
                CONTINUATION, f"{path}.receipts.required", "all lifecycle receipts are required"
            )
        continuation = (
            doc.get("continuation", {}) if isinstance(doc.get("continuation"), dict) else {}
        )
        if not REQUIRED_STOP_CONDITIONS <= _str_items(continuation.get("stopConditions")):
            self.add(  # type: ignore[attr-defined]
                CONTINUATION,
                f"{path}.continuation.stopConditions",
                "mandatory fail-closed stop conditions are missing",
            )
        for field in ("enabled", "nextTaskWithoutHumanApproval", "closeOnlyAfterReadBack"):
            if continuation.get(field) is not True:
                self.add(  # type: ignore[attr-defined]
                    CONTINUATION,
                    f"{path}.continuation.{field}",
                    "bounded autonomous continuation requires true",
                )

    def change_control_shape(self, value: Any, path: str) -> None:
        fields = (
            "intentHistory",
            "baseRefresh",
            "contractMigration",
            "checkProvenance",
            "publicationConvergence",
            "supersededWork",
            "providerReads",
        )
        if not self.closed(value, path, fields, fields):  # type: ignore[attr-defined]
            return

        intent = value["intentHistory"]
        intent_fields = ("checkpointBeforeImplementation", "immutableScope")
        if self.closed(intent, f"{path}.intentHistory", intent_fields, intent_fields):  # type: ignore[attr-defined]
            self.boolean(  # type: ignore[attr-defined]
                intent["checkpointBeforeImplementation"],
                f"{path}.intentHistory.checkpointBeforeImplementation",
                True,
            )
            self.boolean(intent["immutableScope"], f"{path}.intentHistory.immutableScope", True)  # type: ignore[attr-defined]

        refresh = value["baseRefresh"]
        refresh_fields = ("acceptedBaseRequired", "revalidateAll", "historyRewrite", "mode")
        if self.closed(refresh, f"{path}.baseRefresh", refresh_fields, refresh_fields):  # type: ignore[attr-defined]
            self.boolean(  # type: ignore[attr-defined]
                refresh["acceptedBaseRequired"],
                f"{path}.baseRefresh.acceptedBaseRequired",
                True,
            )
            self.boolean(refresh["revalidateAll"], f"{path}.baseRefresh.revalidateAll", True)  # type: ignore[attr-defined]
            self.boolean(refresh["historyRewrite"], f"{path}.baseRefresh.historyRewrite", False)  # type: ignore[attr-defined]
            if refresh["mode"] != "successor-pull-request":
                self.add(  # type: ignore[attr-defined]
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
        if self.closed(  # type: ignore[attr-defined]
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
                self.boolean(migration[field], f"{path}.contractMigration.{field}", True)  # type: ignore[attr-defined]
            if migration["unknownVersion"] != "fail-closed":
                self.add(  # type: ignore[attr-defined]
                    POLICY,
                    f"{path}.contractMigration.unknownVersion",
                    "unknown contract versions must fail closed",
                )
            self.string_set(  # type: ignore[attr-defined]
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
        if self.closed(  # type: ignore[attr-defined]
            provenance,
            f"{path}.checkProvenance",
            provenance_fields,
            provenance_fields,
        ):
            self.boolean(  # type: ignore[attr-defined]
                provenance["protectedRegistry"],
                f"{path}.checkProvenance.protectedRegistry",
                True,
            )
            self.string_set(  # type: ignore[attr-defined]
                provenance["requiredBindings"],
                f"{path}.checkProvenance.requiredBindings",
                minimum=5,
                allowed=REQUIRED_CHECK_PROVENANCE_BINDINGS,
            )
            self.boolean(  # type: ignore[attr-defined]
                provenance["authoritativeProducerRequired"],
                f"{path}.checkProvenance.authoritativeProducerRequired",
                True,
            )
            if provenance["duplicateContextPolicy"] != "reject-ambiguous":
                self.add(  # type: ignore[attr-defined]
                    BOUNDARY,
                    f"{path}.checkProvenance.duplicateContextPolicy",
                    "ambiguous duplicate check contexts must fail closed",
                )
            self.boolean(  # type: ignore[attr-defined]
                provenance["nonAuthoritativeStatusBlocksMerge"],
                f"{path}.checkProvenance.nonAuthoritativeStatusBlocksMerge",
                False,
            )

        convergence = value["publicationConvergence"]
        convergence_fields = (
            "effectivePolicySourceProtected",
            "registryMustMatchEffectivePolicy",
            "preApprovalCheckPolicy",
            "approvalTriggeredChecksDeferred",
            "approvalStartsNewEpoch",
            "postApprovalChecksRequired",
            "postApprovalAttemptRequired",
            "terminalSuccessRequired",
            "minimumStableReads",
            "boundedSameHeadRetry",
            "requiredRebindings",
        )
        if self.closed(  # type: ignore[attr-defined]
            convergence,
            f"{path}.publicationConvergence",
            convergence_fields,
            convergence_fields,
        ):
            for field in (
                "effectivePolicySourceProtected",
                "registryMustMatchEffectivePolicy",
                "approvalTriggeredChecksDeferred",
                "approvalStartsNewEpoch",
                "postApprovalChecksRequired",
                "postApprovalAttemptRequired",
                "terminalSuccessRequired",
                "boundedSameHeadRetry",
            ):
                self.boolean(  # type: ignore[attr-defined]
                    convergence[field],
                    f"{path}.publicationConvergence.{field}",
                    True,
                )
            if convergence["preApprovalCheckPolicy"] != "terminal-success-non-circular":
                self.add(  # type: ignore[attr-defined]
                    BOUNDARY,
                    f"{path}.publicationConvergence.preApprovalCheckPolicy",
                    "pre-approval readiness must defer only approval-triggered checks",
                )
            self.integer(  # type: ignore[attr-defined]
                convergence["minimumStableReads"],
                f"{path}.publicationConvergence.minimumStableReads",
                2,
                2,
            )
            rebindings = self.string_set(  # type: ignore[attr-defined]
                convergence["requiredRebindings"],
                f"{path}.publicationConvergence.requiredRebindings",
                minimum=8,
                allowed=REQUIRED_POLICY_REBINDINGS,
            )
            if rebindings is not None and set(rebindings) != REQUIRED_POLICY_REBINDINGS:
                self.add(  # type: ignore[attr-defined]
                    HEAD,
                    f"{path}.publicationConvergence.requiredRebindings",
                    "post-approval merge must rebind the complete protected subject",
                )

        superseded = value["supersededWork"]
        superseded_fields = (
            "sameRepositorySuccessor",
            "successorMergeRequired",
            "losslessProofRequired",
            "requiredBindings",
            "uniqueDataPolicy",
            "equivalentBranchDisposition",
            "closureEffect",
            "unresolvedBranchDisposition",
            "standingPolicyAuthorizesProvenDeletion",
            "postDispositionReadBack",
        )
        if self.closed(  # type: ignore[attr-defined]
            superseded,
            f"{path}.supersededWork",
            superseded_fields,
            superseded_fields,
        ):
            for field in (
                "sameRepositorySuccessor",
                "successorMergeRequired",
                "losslessProofRequired",
                "standingPolicyAuthorizesProvenDeletion",
                "postDispositionReadBack",
            ):
                self.boolean(  # type: ignore[attr-defined]
                    superseded[field],
                    f"{path}.supersededWork.{field}",
                    True,
                )
            bindings = self.string_set(  # type: ignore[attr-defined]
                superseded["requiredBindings"],
                f"{path}.supersededWork.requiredBindings",
                minimum=8,
                allowed=REQUIRED_SUPERSESSION_BINDINGS,
            )
            if bindings is not None and set(bindings) != REQUIRED_SUPERSESSION_BINDINGS:
                self.add(  # type: ignore[attr-defined]
                    BOUNDARY,
                    f"{path}.supersededWork.requiredBindings",
                    "lossless supersession must bind predecessor, successor, content, and receipt",
                )
            expected_dispositions = (
                ("uniqueDataPolicy", "preserve"),
                ("equivalentBranchDisposition", "delete-after-lossless-proof"),
                ("unresolvedBranchDisposition", "keep-pull-request-open"),
            )
            for field, expected in expected_dispositions:
                if superseded[field] != expected:
                    self.add(  # type: ignore[attr-defined]
                        BOUNDARY,
                        f"{path}.supersededWork.{field}",
                        f"expected {expected}",
                    )
            closure = superseded["closureEffect"]
            closure_fields = (
                "allowedModes",
                "providerCoupledEffectIsSingleMutation",
                "explicitCloseOnlyWhenStillOpen",
                "requiredReadBack",
            )
            if self.closed(  # type: ignore[attr-defined]
                closure,
                f"{path}.supersededWork.closureEffect",
                closure_fields,
                closure_fields,
            ):
                modes = self.string_set(  # type: ignore[attr-defined]
                    closure["allowedModes"],
                    f"{path}.supersededWork.closureEffect.allowedModes",
                    minimum=2,
                    allowed=SUPERSESSION_CLOSURE_MODES,
                )
                if modes is not None and set(modes) != SUPERSESSION_CLOSURE_MODES:
                    self.add(  # type: ignore[attr-defined]
                        BOUNDARY,
                        f"{path}.supersededWork.closureEffect.allowedModes",
                        "both explicit-later and provider-coupled close must be modeled",
                    )
                for field in (
                    "providerCoupledEffectIsSingleMutation",
                    "explicitCloseOnlyWhenStillOpen",
                ):
                    self.boolean(  # type: ignore[attr-defined]
                        closure[field],
                        f"{path}.supersededWork.closureEffect.{field}",
                        True,
                    )
                read_back = self.string_set(  # type: ignore[attr-defined]
                    closure["requiredReadBack"],
                    f"{path}.supersededWork.closureEffect.requiredReadBack",
                    minimum=4,
                    allowed=PROVIDER_COUPLED_READ_BACKS,
                )
                if read_back is not None and set(read_back) != PROVIDER_COUPLED_READ_BACKS:
                    self.add(  # type: ignore[attr-defined]
                        BOUNDARY,
                        f"{path}.supersededWork.closureEffect.requiredReadBack",
                        "provider-coupled closure must preserve branch, PR, "
                        "merge, and archive evidence",
                    )

        reads = value["providerReads"]
        read_fields = ("boundedRetries", "rateLimitStatus", "fallbackMustPreserveAuthority")
        if self.closed(reads, f"{path}.providerReads", read_fields, read_fields):  # type: ignore[attr-defined]
            self.boolean(reads["boundedRetries"], f"{path}.providerReads.boundedRetries", True)  # type: ignore[attr-defined]
            if reads["rateLimitStatus"] != "degraded":
                self.add(  # type: ignore[attr-defined]
                    POLICY,
                    f"{path}.providerReads.rateLimitStatus",
                    "rate limiting must produce a degraded outcome",
                )
            self.boolean(  # type: ignore[attr-defined]
                reads["fallbackMustPreserveAuthority"],
                f"{path}.providerReads.fallbackMustPreserveAuthority",
                True,
            )
