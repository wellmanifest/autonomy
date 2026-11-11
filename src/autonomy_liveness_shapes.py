"""Liveness, pipeline, publication, receipt, continuation, and profile shapes for Autonomy."""

from __future__ import annotations

from typing import Any

from autonomy_constants import (
    CONTINUATION,
    DIGEST_RE,
    HEAD,
    ID_RE,
    PIPELINE_STATES,
    POLICY,
    PROFILE,
    REQUIRED_BINDINGS,
    REQUIRED_CANARY_RECEIPTS,
    REQUIRED_INVOCATION_BINDINGS,
    REQUIRED_RECEIPTS,
    REQUIRED_REGISTRY_BINDINGS,
    RISK,
    ROLES,
    SEMVER_RE,
    SYNTAX,
)


class ValidatorLivenessShapesMixin:
    def execution_liveness_shape(self, value: Any, path: str) -> None:
        fields = (
            "primaryTrigger",
            "watchdog",
            "heartbeat",
            "invocationIdentity",
            "independentPrincipals",
            "manualDispatchProvesLiveness",
            "missedTriggerStatus",
            "perRepositoryIsolation",
            "unrelatedFailureBlocksMerge",
            "aggregateStatusAuthoritative",
            "registry",
            "canary",
        )
        if not self.closed(value, path, fields, fields):  # type: ignore[attr-defined]
            return

        primary = value["primaryTrigger"]
        trigger_fields = ("id", "kind", "principal", "protected")
        if self.closed(primary, f"{path}.primaryTrigger", trigger_fields, trigger_fields):  # type: ignore[attr-defined]
            self.string(primary["id"], f"{path}.primaryTrigger.id", pattern=ID_RE)  # type: ignore[attr-defined]
            self.enum(  # type: ignore[attr-defined]
                primary["kind"],
                f"{path}.primaryTrigger.kind",
                {"event", "scheduler", "durable-queue"},
            )
            self.string(primary["principal"], f"{path}.primaryTrigger.principal", pattern=ID_RE)  # type: ignore[attr-defined]
            self.boolean(primary["protected"], f"{path}.primaryTrigger.protected")  # type: ignore[attr-defined]

        watchdog = value["watchdog"]
        watchdog_fields = (
            "id",
            "kind",
            "principal",
            "protected",
            "maxSilenceSeconds",
            "triggerOnSilence",
        )
        if self.closed(watchdog, f"{path}.watchdog", watchdog_fields, watchdog_fields):  # type: ignore[attr-defined]
            self.string(watchdog["id"], f"{path}.watchdog.id", pattern=ID_RE)  # type: ignore[attr-defined]
            if watchdog["kind"] != "independent-scheduler":
                self.add(POLICY, f"{path}.watchdog.kind", "watchdog must be independent")  # type: ignore[attr-defined]
            self.string(watchdog["principal"], f"{path}.watchdog.principal", pattern=ID_RE)  # type: ignore[attr-defined]
            self.boolean(watchdog["protected"], f"{path}.watchdog.protected")  # type: ignore[attr-defined]
            self.integer(  # type: ignore[attr-defined]
                watchdog["maxSilenceSeconds"], f"{path}.watchdog.maxSilenceSeconds", 60, 86400
            )
            self.boolean(watchdog["triggerOnSilence"], f"{path}.watchdog.triggerOnSilence")  # type: ignore[attr-defined]

        heartbeat = value["heartbeat"]
        heartbeat_fields = (
            "expectedIntervalSeconds",
            "deliveryGraceSeconds",
            "receiptRequired",
            "protectedMonitor",
            "missedCycleReceiptRequired",
            "lateDeliveryPolicy",
            "manualRecoveryRestoresLiveness",
        )
        if self.closed(heartbeat, f"{path}.heartbeat", heartbeat_fields, heartbeat_fields):  # type: ignore[attr-defined]
            self.integer(  # type: ignore[attr-defined]
                heartbeat["expectedIntervalSeconds"],
                f"{path}.heartbeat.expectedIntervalSeconds",
                60,
                86400,
            )
            self.integer(  # type: ignore[attr-defined]
                heartbeat["deliveryGraceSeconds"],
                f"{path}.heartbeat.deliveryGraceSeconds",
                0,
                86400,
            )
            for field in (
                "receiptRequired",
                "protectedMonitor",
                "missedCycleReceiptRequired",
                "manualRecoveryRestoresLiveness",
            ):
                self.boolean(heartbeat[field], f"{path}.heartbeat.{field}")  # type: ignore[attr-defined]
            if heartbeat["lateDeliveryPolicy"] != "deduplicate-with-recovery":
                self.add(  # type: ignore[attr-defined]
                    POLICY,
                    f"{path}.heartbeat.lateDeliveryPolicy",
                    "late scheduled delivery must deduplicate with recovery",
                )

        invocation = value["invocationIdentity"]
        invocation_fields = (
            "correlationRequired",
            "providerRunIdentityRequired",
            "preDispatchBoundaryRequired",
            "postBoundaryOnly",
            "requiredBindings",
            "matrixChildCorrelationRequired",
            "ambiguousRunOutcome",
        )
        if self.closed(  # type: ignore[attr-defined]
            invocation,
            f"{path}.invocationIdentity",
            invocation_fields,
            invocation_fields,
        ):
            for field in (
                "correlationRequired",
                "providerRunIdentityRequired",
                "preDispatchBoundaryRequired",
                "postBoundaryOnly",
                "matrixChildCorrelationRequired",
            ):
                self.boolean(invocation[field], f"{path}.invocationIdentity.{field}")  # type: ignore[attr-defined]
            self.string_set(  # type: ignore[attr-defined]
                invocation["requiredBindings"],
                f"{path}.invocationIdentity.requiredBindings",
                minimum=1,
                allowed=REQUIRED_INVOCATION_BINDINGS,
            )
            if invocation["ambiguousRunOutcome"] != "failed":
                self.add(  # type: ignore[attr-defined]
                    POLICY,
                    f"{path}.invocationIdentity.ambiguousRunOutcome",
                    "ambiguous provider run selection must fail closed",
                )

        for field in (
            "independentPrincipals",
            "manualDispatchProvesLiveness",
            "perRepositoryIsolation",
            "unrelatedFailureBlocksMerge",
            "aggregateStatusAuthoritative",
        ):
            self.boolean(value[field], f"{path}.{field}")  # type: ignore[attr-defined]
        if value["missedTriggerStatus"] != "degraded":
            self.add(POLICY, f"{path}.missedTriggerStatus", "missed triggers must degrade status")  # type: ignore[attr-defined]

        registry = value["registry"]
        registry_fields = (
            "source",
            "digest",
            "protected",
            "singleSource",
            "requiredBindings",
            "driftCheck",
        )
        if self.closed(registry, f"{path}.registry", registry_fields, registry_fields):  # type: ignore[attr-defined]
            self.uri(registry["source"], f"{path}.registry.source")  # type: ignore[attr-defined]
            self.string(registry["digest"], f"{path}.registry.digest", pattern=DIGEST_RE)  # type: ignore[attr-defined]
            self.boolean(registry["protected"], f"{path}.registry.protected")  # type: ignore[attr-defined]
            self.boolean(registry["singleSource"], f"{path}.registry.singleSource")  # type: ignore[attr-defined]
            self.string_set(  # type: ignore[attr-defined]
                registry["requiredBindings"],
                f"{path}.registry.requiredBindings",
                minimum=1,
                allowed=REQUIRED_REGISTRY_BINDINGS,
            )
            self.boolean(registry["driftCheck"], f"{path}.registry.driftCheck")  # type: ignore[attr-defined]

        canary = value["canary"]
        canary_fields = ("mode", "maximumAgeSeconds", "manualDispatchCounts", "requiredReceipts")
        if self.closed(canary, f"{path}.canary", canary_fields, canary_fields):  # type: ignore[attr-defined]
            if canary["mode"] != "protected-low-risk-pr":
                self.add(  # type: ignore[attr-defined]
                    POLICY,
                    f"{path}.canary.mode",
                    "canary must traverse protected publication",
                )
            self.integer(  # type: ignore[attr-defined]
                canary["maximumAgeSeconds"], f"{path}.canary.maximumAgeSeconds", 60, 604800
            )
            self.boolean(canary["manualDispatchCounts"], f"{path}.canary.manualDispatchCounts")  # type: ignore[attr-defined]
            self.string_set(  # type: ignore[attr-defined]
                canary["requiredReceipts"],
                f"{path}.canary.requiredReceipts",
                minimum=1,
                allowed=REQUIRED_CANARY_RECEIPTS,
            )

    def pipeline_shape(self, value: Any, path: str) -> None:
        fields = ("states", "requiredGates", "onFailure", "onOutOfScope")
        if not self.closed(value, path, fields, fields):  # type: ignore[attr-defined]
            return
        states = self.string_set(value["states"], f"{path}.states", minimum=16)  # type: ignore[attr-defined]
        if states is not None and states != PIPELINE_STATES:
            self.add(  # type: ignore[attr-defined]
                CONTINUATION, f"{path}.states", "pipeline states must match the normative order"
            )
        gates = value["requiredGates"]
        if not isinstance(gates, list) or len(gates) < 15:
            self.add(SYNTAX, f"{path}.requiredGates", "expected at least fifteen gates")  # type: ignore[attr-defined]
        else:
            for index, gate in enumerate(gates):
                item_path = f"{path}.requiredGates[{index}]"
                fields = ("id", "stage", "kind", "producer", "protected", "failClosed")
                if not self.closed(gate, item_path, fields, fields):  # type: ignore[attr-defined]
                    continue
                self.string(gate["id"], f"{item_path}.id", pattern=ID_RE)  # type: ignore[attr-defined]
                self.enum(  # type: ignore[attr-defined]
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
                self.enum(  # type: ignore[attr-defined]
                    gate["kind"],
                    f"{item_path}.kind",
                    {"liveness", "deterministic", "independent-attestation", "read-back"},
                )
                self.string(gate["producer"], f"{item_path}.producer", pattern=ID_RE)  # type: ignore[attr-defined]
                self.boolean(gate["protected"], f"{item_path}.protected")  # type: ignore[attr-defined]
                self.boolean(gate["failClosed"], f"{item_path}.failClosed", True)  # type: ignore[attr-defined]
        if value["onFailure"] != "fail-closed":
            self.add(CONTINUATION, f"{path}.onFailure", "failure must fail closed")  # type: ignore[attr-defined]
        if value["onOutOfScope"] != "escalate":
            self.add(CONTINUATION, f"{path}.onOutOfScope", "out-of-scope work must escalate")  # type: ignore[attr-defined]

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
        if not self.closed(value, path, fields, fields):  # type: ignore[attr-defined]
            return
        if value["mode"] != "pull-request":
            self.add(HEAD, f"{path}.mode", "publication must use pull requests")  # type: ignore[attr-defined]
        self.enum(  # type: ignore[attr-defined]
            value["approval"],
            f"{path}.approval",
            {"trusted-validator-app", "signed-validator-attestation"},
        )
        self.string_set(value["requiredChecks"], f"{path}.requiredChecks", minimum=1)  # type: ignore[attr-defined]
        self.string_set(value["bindings"], f"{path}.bindings", minimum=1, allowed=REQUIRED_BINDINGS)  # type: ignore[attr-defined]
        if value["mergeMode"] != "protected-explicit":
            self.add(HEAD, f"{path}.mergeMode", "merge must use protected explicit execution")  # type: ignore[attr-defined]
        for field in (
            "sameRepositoryOnly",
            "recheckBaseBeforeMerge",
            "autonomousMerge",
            "nativeAutoMerge",
            "directDefaultBranchPush",
            "deleteBranchAfterMerge",
            "postMergeReadBack",
        ):
            self.boolean(value[field], f"{path}.{field}")  # type: ignore[attr-defined]

    def receipts_shape(self, value: Any, path: str) -> None:
        fields = ("store", "required", "redaction", "retentionDays")
        if not self.closed(value, path, fields, fields):  # type: ignore[attr-defined]
            return
        self.uri(value["store"], f"{path}.store")  # type: ignore[attr-defined]
        self.string_set(  # type: ignore[attr-defined]
            value["required"], f"{path}.required", minimum=22, allowed=REQUIRED_RECEIPTS
        )
        if value["redaction"] != "secret-free":
            self.add(RISK, f"{path}.redaction", "receipts must be secret-free")  # type: ignore[attr-defined]
        self.integer(value["retentionDays"], f"{path}.retentionDays", 30, 3650)  # type: ignore[attr-defined]

    def continuation_shape(self, value: Any, path: str) -> None:
        fields = (
            "enabled",
            "nextTaskWithoutHumanApproval",
            "closeOnlyAfterReadBack",
            "stopConditions",
        )
        if not self.closed(value, path, fields, fields):  # type: ignore[attr-defined]
            return
        self.boolean(value["enabled"], f"{path}.enabled", True)  # type: ignore[attr-defined]
        self.boolean(  # type: ignore[attr-defined]
            value["nextTaskWithoutHumanApproval"], f"{path}.nextTaskWithoutHumanApproval", True
        )
        self.boolean(value["closeOnlyAfterReadBack"], f"{path}.closeOnlyAfterReadBack", True)  # type: ignore[attr-defined]
        self.string_set(value["stopConditions"], f"{path}.stopConditions", minimum=1)  # type: ignore[attr-defined]

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
        if not self.closed(doc, path, fields, fields):  # type: ignore[attr-defined]
            return False
        if doc["$schema"] != "https://wellmanifest.com/schemas/autonomy-manifest/v6":
            self.add(SYNTAX, f"{path}.$schema", "unknown schema URI")  # type: ignore[attr-defined]
        if doc["schema"] != "wellmanifest.autonomy/profile/v6":
            self.add(SYNTAX, f"{path}.schema", "unknown profile version")  # type: ignore[attr-defined]
        self.string(doc["id"], f"{path}.id", pattern=ID_RE)  # type: ignore[attr-defined]
        self.string(doc["version"], f"{path}.version", pattern=SEMVER_RE)  # type: ignore[attr-defined]
        self.enum(doc["status"], f"{path}.status", {"experimental", "stable", "deprecated"})  # type: ignore[attr-defined]
        ownership = doc["ownership"]
        if self.closed(  # type: ignore[attr-defined]
            ownership,
            f"{path}.ownership",
            ("standardOwner", "runtimeOwners"),
            ("standardOwner", "runtimeOwners"),
        ):
            if ownership["standardOwner"] != "wellmanifest/autonomy":
                self.add(  # type: ignore[attr-defined]
                    PROFILE,
                    f"{path}.ownership.standardOwner",
                    "standard ownership must remain in wellmanifest/autonomy",
                )
            owners = self.string_set(  # type: ignore[attr-defined]
                ownership["runtimeOwners"], f"{path}.ownership.runtimeOwners", minimum=1
            )
            if owners:
                for index, owner in enumerate(owners):
                    if not owner.startswith(("subactor/", "semcod/")):
                        self.add(  # type: ignore[attr-defined]
                            PROFILE,
                            f"{path}.ownership.runtimeOwners[{index}]",
                            "runtime owner must be subactor/* or semcod/*",
                        )
        bindings = doc["bindings"]
        if not isinstance(bindings, list) or len(bindings) < 7:
            self.add(SYNTAX, f"{path}.bindings", "expected at least seven bindings")  # type: ignore[attr-defined]
        else:
            for index, binding in enumerate(bindings):
                self.profile_binding_shape(binding, f"{path}.bindings[{index}]")
        boundaries = doc["protectedBoundaries"]
        fields = (
            "profileDigestExternal",
            "durableQueueProtected",
            "watchdogPrincipalIndependent",
            "heartbeatEvidenceExternal",
            "invocationCorrelationProtected",
            "effectReceiptExternal",
            "registryDigestExternal",
            "effectivePolicyExternal",
            "approvalEventObservedExternally",
            "supersessionDispositionProtected",
            "targetOutcomeIsolated",
            "validatorPrincipalIndependent",
            "publisherCredentialProtected",
            "llmVerdictAdvisory",
        )
        if self.closed(boundaries, f"{path}.protectedBoundaries", fields, fields):  # type: ignore[attr-defined]
            for field in fields:
                self.boolean(boundaries[field], f"{path}.protectedBoundaries.{field}", True)  # type: ignore[attr-defined]
        return True

    def profile_binding_shape(self, value: Any, path: str) -> None:
        fields = ("stage", "product", "role", "mode", "capabilities", "contracts", "restrictions")
        if not self.closed(value, path, fields, fields):  # type: ignore[attr-defined]
            return
        self.enum(  # type: ignore[attr-defined]
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
        if not self.string(value["product"], f"{path}.product"):  # type: ignore[attr-defined]
            return
        if not value["product"].startswith(("subactor/", "semcod/", "wellmanifest/")):
            self.add(PROFILE, f"{path}.product", "unknown product owner")  # type: ignore[attr-defined]
        self.enum(value["role"], f"{path}.role", ROLES)  # type: ignore[attr-defined]
        self.enum(  # type: ignore[attr-defined]
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
        self.string_set(value["capabilities"], f"{path}.capabilities", minimum=1)  # type: ignore[attr-defined]
        contracts = self.string_set(value["contracts"], f"{path}.contracts")  # type: ignore[attr-defined]
        if contracts:
            for index, contract in enumerate(contracts):
                self.uri(contract, f"{path}.contracts[{index}]")  # type: ignore[attr-defined]
        self.string_set(value["restrictions"], f"{path}.restrictions", minimum=1)  # type: ignore[attr-defined]

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
        stages: set[str] = set()
        ownership = doc.get("ownership", {}) if isinstance(doc.get("ownership"), dict) else {}
        raw_owners = ownership.get("runtimeOwners", [])
        owners = (
            {item for item in raw_owners if isinstance(item, str)}
            if isinstance(raw_owners, list)
            else set()
        )
        raw_bindings = doc.get("bindings", [])
        for index, binding in enumerate(raw_bindings if isinstance(raw_bindings, list) else []):
            if not isinstance(binding, dict):
                continue
            stage = binding.get("stage")
            if isinstance(stage, str):
                stages.add(stage)
            if stage in expected and (binding.get("role"), binding.get("mode")) != expected[stage]:
                self.add(  # type: ignore[attr-defined]
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
                self.add(  # type: ignore[attr-defined]
                    PROFILE,
                    f"{path}.bindings[{index}].product",
                    "product is not declared as a runtime owner",
                )
        if stages != set(expected):
            self.add(  # type: ignore[attr-defined]
                PROFILE,
                f"{path}.bindings",
                "profile must cover all lifecycle stages; missing "
                f"{sorted(set(expected) - stages)}",
            )
