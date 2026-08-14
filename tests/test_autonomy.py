from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "autonomy_check.py"
SPEC = importlib.util.spec_from_file_location("autonomy_check", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
autonomy_check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = autonomy_check
SPEC.loader.exec_module(autonomy_check)


class AutonomyConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_path = ROOT / "examples" / "valid" / "project.autonomy.json"
        cls.profile_path = ROOT / "profiles" / "subactor-semcod.profile.json"
        cls.valid = json.loads(cls.valid_path.read_text(encoding="utf-8"))
        cls.profile = json.loads(cls.profile_path.read_text(encoding="utf-8"))

    def findings(self, document: dict) -> list:
        return autonomy_check.validate_document(document, profile_path=self.profile_path)

    def codes(self, document: dict) -> set[str]:
        return {finding.code for finding in self.findings(document)}

    def test_valid_manifest_and_profile_pass(self) -> None:
        self.assertEqual([], self.findings(self.valid))
        self.assertEqual(
            [],
            autonomy_check.validate_document(self.profile, profile_path=None),
        )

    def test_invalid_case_fixtures_emit_declared_codes(self) -> None:
        for path in sorted((ROOT / "examples" / "invalid").glob("*.json")):
            case = json.loads(path.read_text(encoding="utf-8"))
            observed = {
                finding.code
                for finding in autonomy_check.load_and_validate(
                    path,
                    profile_path=self.profile_path,
                )
            }
            self.assertLessEqual(set(case["expectedCodes"]), observed, path.name)

    def test_unknown_root_and_nested_fields_are_rejected(self) -> None:
        root = copy.deepcopy(self.valid)
        root["authorityOverride"] = True
        self.assertIn(autonomy_check.SYNTAX, self.codes(root))

        nested = copy.deepcopy(self.valid)
        nested["grant"]["constraints"]["bypass"] = True
        self.assertIn(autonomy_check.SYNTAX, self.codes(nested))

    def test_malformed_nested_values_fail_without_crashing(self) -> None:
        for section in (
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
        ):
            with self.subTest(section=section):
                mutation = copy.deepcopy(self.valid)
                mutation[section] = None
                self.assertIn(autonomy_check.SYNTAX, self.codes(mutation))

    def test_same_implementer_and_validator_principal_is_critical(self) -> None:
        mutation = copy.deepcopy(self.valid)
        roles = {role["role"]: role for role in mutation["fleet"]["roles"]}
        roles["validator"]["principal"] = roles["implementer"]["principal"]
        findings = self.findings(mutation)
        separation = [finding for finding in findings if finding.code == autonomy_check.SEPARATION]
        self.assertTrue(separation)
        self.assertTrue(all(finding.severity == "critical" for finding in separation))

    def test_model_diversity_is_not_required_for_real_independence(self) -> None:
        mutation = copy.deepcopy(self.valid)
        roles = {role["role"]: role for role in mutation["fleet"]["roles"]}
        roles["validator"]["model"] = roles["implementer"]["model"]
        self.assertEqual([], self.findings(mutation))

    def test_role_authority_ceiling_blocks_self_approval(self) -> None:
        mutation = copy.deepcopy(self.valid)
        implementer = next(
            role for role in mutation["fleet"]["roles"] if role["role"] == "implementer"
        )
        implementer["authorities"].append("approve-via-validator-app")
        self.assertIn(autonomy_check.SEPARATION, self.codes(mutation))

    def test_mandatory_excluded_effects_cannot_be_removed(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["riskPolicy"]["excludedEffects"].remove("grant-mutation")
        self.assertIn(autonomy_check.RISK, self.codes(mutation))

    def test_grant_temporal_order_and_evaluation_time_fail_closed(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["grant"]["reviewAt"] = "2026-10-01T00:00:00Z"
        self.assertIn(autonomy_check.GRANT, self.codes(mutation))

        at = datetime.fromisoformat("2026-10-02T00:00:00+00:00")
        findings = autonomy_check.validate_document(
            self.valid,
            at=at,
            profile_path=self.profile_path,
        )
        self.assertIn(autonomy_check.GRANT, {finding.code for finding in findings})

    def test_repository_and_default_branch_must_be_in_grant(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["grant"]["scope"]["repositories"] = ["example/other"]
        self.assertIn(autonomy_check.GRANT, self.codes(mutation))

    def test_exact_head_bindings_and_checks_are_required(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["publication"]["bindings"].remove("baseSha")
        mutation["publication"]["requiredChecks"].remove("security")
        self.assertIn(autonomy_check.HEAD, self.codes(mutation))

    def test_pipeline_order_and_stop_conditions_are_closed(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["pipeline"]["states"][3:5] = reversed(mutation["pipeline"]["states"][3:5])
        mutation["continuation"]["stopConditions"].remove("ambiguous-evidence")
        findings = self.codes(mutation)
        self.assertIn(autonomy_check.CONTINUATION, findings)

    def test_manual_dispatch_cannot_prove_trigger_or_canary_liveness(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["executionLiveness"]["manualDispatchProvesLiveness"] = True
        mutation["executionLiveness"]["canary"]["manualDispatchCounts"] = True
        findings = self.codes(mutation)
        self.assertIn(autonomy_check.POLICY, findings)
        self.assertIn(autonomy_check.BOUNDARY, findings)

    def test_primary_trigger_and_watchdog_must_be_independent(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["executionLiveness"]["watchdog"]["principal"] = mutation[
            "executionLiveness"
        ]["primaryTrigger"]["principal"]
        self.assertIn(autonomy_check.SEPARATION, self.codes(mutation))

    def test_queue_is_durable_at_least_once_and_replay_safe(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["queue"]["durable"] = False
        mutation["queue"]["delivery"] = "at-most-once"
        mutation["queue"]["idempotencyBindings"].remove("operation")
        self.assertIn(autonomy_check.POLICY, self.codes(mutation))

    def test_repository_outcomes_cannot_be_globally_fail_fast(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["executionLiveness"]["perRepositoryIsolation"] = False
        mutation["executionLiveness"]["unrelatedFailureBlocksMerge"] = True
        mutation["executionLiveness"]["aggregateStatusAuthoritative"] = True
        self.assertIn(autonomy_check.BOUNDARY, self.codes(mutation))

    def test_registry_drift_and_incomplete_bindings_fail_closed(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["executionLiveness"]["registry"]["driftCheck"] = False
        mutation["executionLiveness"]["registry"]["requiredBindings"].remove("mergePolicy")
        self.assertIn(autonomy_check.BOUNDARY, self.codes(mutation))

    def test_intent_checkpoint_and_base_refresh_fail_closed(self) -> None:
        missing_checkpoint = copy.deepcopy(self.valid)
        missing_checkpoint["changeControl"]["intentHistory"][
            "checkpointBeforeImplementation"
        ] = False
        self.assertIn(autonomy_check.SYNTAX, self.codes(missing_checkpoint))

        rewrite = copy.deepcopy(self.valid)
        rewrite["changeControl"]["baseRefresh"]["historyRewrite"] = True
        self.assertIn(autonomy_check.SYNTAX, self.codes(rewrite))

        unsafe_mode = copy.deepcopy(self.valid)
        unsafe_mode["changeControl"]["baseRefresh"]["mode"] = "force-rebase"
        self.assertIn(autonomy_check.BOUNDARY, self.codes(unsafe_mode))

    def test_contract_migration_requires_every_consumer_surface(self) -> None:
        partial = copy.deepcopy(self.valid)
        partial["changeControl"]["contractMigration"]["requiredSurfaces"].remove(
            "compose"
        )
        self.assertIn(autonomy_check.SYNTAX, self.codes(partial))

        late_resolution = copy.deepcopy(self.valid)
        late_resolution["changeControl"]["contractMigration"][
            "resolveBeforeConsumerExecution"
        ] = False
        self.assertIn(autonomy_check.SYNTAX, self.codes(late_resolution))

    def test_check_provenance_is_authoritative_and_unambiguous(self) -> None:
        ambiguous = copy.deepcopy(self.valid)
        ambiguous["changeControl"]["checkProvenance"][
            "duplicateContextPolicy"
        ] = "prefer-success"
        self.assertIn(autonomy_check.BOUNDARY, self.codes(ambiguous))

        incomplete = copy.deepcopy(self.valid)
        incomplete["changeControl"]["checkProvenance"]["requiredBindings"].remove(
            "event"
        )
        self.assertIn(autonomy_check.SYNTAX, self.codes(incomplete))

        unsafe_status = copy.deepcopy(self.valid)
        unsafe_status["changeControl"]["checkProvenance"][
            "nonAuthoritativeStatusBlocksMerge"
        ] = True
        self.assertIn(autonomy_check.SYNTAX, self.codes(unsafe_status))

    def test_provider_read_fallback_preserves_authority(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["changeControl"]["providerReads"][
            "fallbackMustPreserveAuthority"
        ] = False
        self.assertIn(autonomy_check.SYNTAX, self.codes(mutation))

    def test_post_approval_policy_convergence_is_mandatory(self) -> None:
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
            with self.subTest(field=field):
                mutation = copy.deepcopy(self.valid)
                mutation["changeControl"]["publicationConvergence"][field] = False
                self.assertIn(autonomy_check.SYNTAX, self.codes(mutation))

        unstable = copy.deepcopy(self.valid)
        unstable["changeControl"]["publicationConvergence"]["minimumStableReads"] = 1
        self.assertIn(autonomy_check.SYNTAX, self.codes(unstable))

        circular = copy.deepcopy(self.valid)
        circular["changeControl"]["publicationConvergence"][
            "preApprovalCheckPolicy"
        ] = "all-checks-terminal"
        self.assertIn(autonomy_check.BOUNDARY, self.codes(circular))

        incomplete = copy.deepcopy(self.valid)
        incomplete["changeControl"]["publicationConvergence"][
            "requiredRebindings"
        ].remove("approvalId")
        self.assertIn(autonomy_check.SYNTAX, self.codes(incomplete))

    def test_superseded_work_is_lossless_and_never_orphaned(self) -> None:
        unproved = copy.deepcopy(self.valid)
        unproved["changeControl"]["supersededWork"]["losslessProofRequired"] = False
        self.assertIn(autonomy_check.SYNTAX, self.codes(unproved))

        incomplete = copy.deepcopy(self.valid)
        incomplete["changeControl"]["supersededWork"]["requiredBindings"].remove(
            "receiptDigest"
        )
        self.assertIn(autonomy_check.SYNTAX, self.codes(incomplete))

        orphan = copy.deepcopy(self.valid)
        orphan["changeControl"]["supersededWork"][
            "equivalentBranchDisposition"
        ] = "close-and-preserve"
        self.assertIn(autonomy_check.BOUNDARY, self.codes(orphan))

        coupled = copy.deepcopy(self.valid)
        coupled["changeControl"]["supersededWork"]["closureEffect"][
            "providerCoupledEffectIsSingleMutation"
        ] = False
        self.assertIn(autonomy_check.SYNTAX, self.codes(coupled))

        stale_archive = copy.deepcopy(self.valid)
        stale_archive["changeControl"]["supersededWork"]["closureEffect"][
            "requiredReadBack"
        ].remove("archiveHeadPreserved")
        self.assertIn(autonomy_check.SYNTAX, self.codes(stale_archive))

        explicit_only = copy.deepcopy(self.valid)
        explicit_only["changeControl"]["supersededWork"]["closureEffect"][
            "allowedModes"
        ].remove("provider-coupled")
        self.assertIn(autonomy_check.SYNTAX, self.codes(explicit_only))

        unresolved = copy.deepcopy(self.valid)
        unresolved["changeControl"]["supersededWork"][
            "unresolvedBranchDisposition"
        ] = "close-pull-request"
        self.assertIn(autonomy_check.BOUNDARY, self.codes(unresolved))

    def test_native_auto_merge_cannot_replace_explicit_app_merge(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["publication"]["nativeAutoMerge"] = True
        mutation["publication"]["mergeMode"] = "platform-native"
        self.assertIn(autonomy_check.HEAD, self.codes(mutation))

    def test_canary_policy_rejects_stale_or_partial_proof_shape(self) -> None:
        stale = copy.deepcopy(self.valid)
        stale["executionLiveness"]["canary"]["maximumAgeSeconds"] = 604801
        self.assertIn(autonomy_check.SYNTAX, self.codes(stale))

        partial = copy.deepcopy(self.valid)
        partial["executionLiveness"]["canary"]["requiredReceipts"].remove("branch-cleanup")
        self.assertIn(autonomy_check.POLICY, self.codes(partial))

    def test_profile_digest_is_exact_byte_binding(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["subject"]["profile"]["digest"] = "sha256:" + "0" * 64
        self.assertIn(autonomy_check.PROFILE, self.codes(mutation))

    def test_profile_home_adopt_and_stage_boundaries_are_enforced(self) -> None:
        mutation = copy.deepcopy(self.profile)
        mutation["ownership"]["standardOwner"] = "subactor/autonom"
        binding = next(item for item in mutation["bindings"] if item["stage"] == "validate")
        binding["mode"] = "candidate-write"
        findings = autonomy_check.validate_document(mutation, profile_path=None)
        self.assertIn(autonomy_check.PROFILE, {finding.code for finding in findings})

    def test_stable_profile_binds_deployed_durable_controller(self) -> None:
        self.assertEqual("0.7.1", self.profile["version"])
        self.assertEqual("stable", self.profile["status"])
        dispatch = next(
            binding
            for binding in self.profile["bindings"]
            if binding["stage"] == "dispatch"
            and binding["product"] == "subactor/autonom"
        )
        publish = next(
            binding
            for binding in self.profile["bindings"]
            if binding["stage"] == "publish"
            and binding["product"] == "subactor/autonom"
        )
        self.assertLessEqual(
            {
                "write-ahead-operation",
                "fsync-checkpoint",
                "canary-recovery",
                "protected-source-preflight",
                "exact-runtime-pin",
                "protected-runtime-worktree",
                "quiesced-rollout",
                "supervisor-source-isolation",
                "intent-checkpoint",
                "contract-consumer-inventory",
                "provider-read-fallback",
                "watchdog-reconcile",
            },
            set(dispatch["capabilities"]),
        )
        self.assertLessEqual(
            {
                "repo://subactor/autonom/autonom/pull_request_state.py",
                "repo://subactor/autonom/autonom/pull_request_controller.py",
                "repo://subactor/autonom/scripts/deploy-pr-controller.sh",
                "repo://subactor/autonom/systemd/subactor-pr-controller.service",
                "repo://subactor/autonom/systemd/subactor-pr-controller.timer",
                "repo://subactor/validator-agent/config/direct-pr-registry.json",
            },
            set(dispatch["contracts"]),
        )
        self.assertIn("lease-exceeds-effect-timeout", dispatch["restrictions"])
        self.assertIn("candidate-checkout-excluded", dispatch["restrictions"])
        self.assertIn("runtime-checkout-isolated", dispatch["restrictions"])
        self.assertIn("supervisor-checkout-excluded", dispatch["restrictions"])
        self.assertIn("policy-checkout-isolated", dispatch["restrictions"])
        self.assertIn("rollout-trigger-quiesced", dispatch["restrictions"])
        self.assertIn("rollback-same-boundary", dispatch["restrictions"])
        self.assertIn("intent-before-implementation", dispatch["restrictions"])
        self.assertIn("exact-contract-version-allowlist", dispatch["restrictions"])
        self.assertIn("all-validation-surfaces", dispatch["restrictions"])
        self.assertIn("bounded-provider-retries", dispatch["restrictions"])
        self.assertLessEqual(
            {
                "exact-head-app-review",
                "explicit-app-merge",
                "merge-sha-read-back",
                "branch-cleanup",
                "successor-pr-base-refresh",
                "authoritative-check-provenance",
                "effective-policy-discovery",
                "pre-approval-check-partition",
                "post-approval-check-convergence",
                "provider-coupled-pr-closure",
                "lossless-superseded-branch-disposition",
                "durable-publication-checkpoint",
            },
            set(publish["capabilities"]),
        )
        self.assertIn("native-auto-merge-forbidden", publish["restrictions"])
        self.assertIn("history-rewrite-forbidden", publish["restrictions"])
        self.assertIn(
            "ambiguous-check-contexts-fail-closed", publish["restrictions"]
        )
        self.assertIn("non-authoritative-status-ignored", publish["restrictions"])
        self.assertIn("registry-drift-fails-closed", publish["restrictions"])
        self.assertIn(
            "approval-starts-new-evidence-epoch", publish["restrictions"]
        )
        self.assertIn(
            "approval-triggered-checks-deferred-before-review",
            publish["restrictions"],
        )
        self.assertIn("post-approval-attempt-required", publish["restrictions"])
        self.assertIn(
            "delete-proven-equivalent-branch-after-integrated-proof",
            publish["restrictions"],
        )
        self.assertIn(
            "provider-coupled-close-read-back",
            publish["restrictions"],
        )
        self.assertIn(
            "unresolved-superseded-pr-remains-open", publish["restrictions"]
        )

    def test_normative_durability_and_receipt_origin_rules_are_published(self) -> None:
        standard = (ROOT / "spec" / "AUTONOMY_STANDARD.md").read_text(encoding="utf-8")
        required_text = (
            "initial duration MUST exceed the maximum bounded duration",
            "queue record and claim MUST be durably committed",
            "flushing\nthe new bytes and directory metadata",
            "MUST clean an obsolete\nqueue or claim remnant",
            "checkpoint is the authority for completed local continuation state",
            "transport named\n`workflow_dispatch` is not by itself evidence of manual execution",
            "MUST NOT be loaded from a workspace used for candidate or\nconcurrent development",
            "supervisor outside the loaded\ncontroller code MUST fail closed",
            "not an exact runtime pin",
            "MUST NOT resolve through symlinks\nor files owned by a candidate",
            "quiesce every trigger and wait for or safely terminate",
            "MUST NOT resume an unpinned runtime",
            "requires a fresh automatic cycle bound\nto the new runtime pin",
            "intent checkpoint MUST precede",
            "successor pull request",
            "Compose override",
            "Duplicate\nsame-named contexts",
            "bounded provider retries",
            "complete effective required-check set",
            "starts a new evidence epoch",
            "two consecutive protected reads",
            "partition the protected required-check set",
            "fresh attempt submitted\nafter the exact approval timestamp",
            "request branch deletion while\nthe pull request is still open",
            "platform-coupled effect",
            "pull request MUST\nremain open as its explicit owner",
        )
        for phrase in required_text:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, standard)

    def test_live_evidence_is_scoped_and_does_not_overclaim_watchdog_recovery(self) -> None:
        architecture = (ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
        canary_receipt = "fd960b35a9816246aec2629f619cf9ce42e68892fb8bab806697768f4ab795e2"
        self.assertIn(canary_receipt, architecture)
        self.assertIn("manual_dispatch=false", architecture)
        self.assertIn("giving a 50-minute lease for a service bounded to\n45 minutes", architecture)
        self.assertIn("No live missed-trigger watchdog recovery had been observed", architecture)
        self.assertIn("MUST NOT be presented as full operational\nconformance", architecture)
        self.assertIn("protected_registry_digest_mismatch", architecture)
        protected_checkpoint = "4c2519ef8d4c4a632907d570ddb4b7aba81aa7b8dc5e24e77cc9f611bc9c19ea"
        self.assertIn(protected_checkpoint, architecture)
        self.assertIn("failed in `ExecStartPre`", architecture)
        self.assertIn("No Python controller was loaded", architecture)
        rollout_checkpoint = "c5ba6476482e20eaf0d1a01727cc9565cec977fe30c14712dd048eb4df3f85c0"
        self.assertIn(rollout_checkpoint, architecture)
        self.assertIn("31830719505", architecture)
        self.assertIn("4940318952", architecture)
        self.assertIn("88953aa58a48526caf1134ba40b04d0f39e3ff39", architecture)
        self.assertIn("`ok=true`, `dry_run=false`, zero mutations", architecture)
        self.assertIn("31843668089", architecture)
        self.assertIn("31844397273", architecture)
        self.assertIn("GOV-BRANCH-LIFECYCLE-002", architecture)

    def test_public_schema_is_draft_2020_12_and_closed(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "autonomy-manifest.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertFalse(schema["$defs"]["manifest"]["additionalProperties"])
        self.assertFalse(schema["$defs"]["profile"]["additionalProperties"])

    def test_invalid_case_cannot_escape_examples_root(self) -> None:
        case = {
            "schema": "wellmanifest.autonomy/invalid-case/v1",
            "base": "../../../README.md",
            "mutations": [{"op": "replace", "path": "/status", "value": "active"}],
            "expectedCodes": [autonomy_check.RISK],
        }
        _, findings = autonomy_check.apply_invalid_case(
            case,
            ROOT / "examples" / "invalid" / "synthetic.json",
        )
        self.assertIn(autonomy_check.RISK, {finding.code for finding in findings})


if __name__ == "__main__":
    unittest.main()
