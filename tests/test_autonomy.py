from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import sys
import tempfile
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

    def test_effect_reconciliation_forbids_duplicate_review_or_merge(self) -> None:
        duplicate = copy.deepcopy(self.valid)
        duplicate["queue"]["effectReconciliation"]["repeatReviewOrMerge"] = True
        self.assertIn(autonomy_check.BOUNDARY, self.codes(duplicate))

        incomplete = copy.deepcopy(self.valid)
        incomplete["queue"]["effectReconciliation"][
            "alreadyAppliedRequiredBindings"
        ].remove("approvalId")
        self.assertIn(autonomy_check.BOUNDARY, self.codes(incomplete))

        closed_unmerged = copy.deepcopy(self.valid)
        closed_unmerged["queue"]["effectReconciliation"][
            "closedUnmergedOutcome"
        ] = "already-applied"
        self.assertIn(autonomy_check.POLICY, self.codes(closed_unmerged))

    def test_scheduler_heartbeat_is_independent_from_recovery(self) -> None:
        recovery = copy.deepcopy(self.valid)
        recovery["executionLiveness"]["heartbeat"]["manualRecoveryRestoresLiveness"] = True
        self.assertIn(autonomy_check.BOUNDARY, self.codes(recovery))

        missing_receipt = copy.deepcopy(self.valid)
        missing_receipt["executionLiveness"]["heartbeat"]["missedCycleReceiptRequired"] = False
        self.assertIn(autonomy_check.BOUNDARY, self.codes(missing_receipt))

        overlapping = copy.deepcopy(self.valid)
        overlapping["executionLiveness"]["heartbeat"]["lateDeliveryPolicy"] = "run-both"
        self.assertIn(autonomy_check.POLICY, self.codes(overlapping))

    def test_provider_run_selection_is_post_boundary_and_correlation_bound(self) -> None:
        mutation = copy.deepcopy(self.valid)
        invocation = mutation["executionLiveness"]["invocationIdentity"]
        invocation["postBoundaryOnly"] = False
        invocation["matrixChildCorrelationRequired"] = False
        invocation["requiredBindings"].remove("correlationId")
        self.assertIn(autonomy_check.BOUNDARY, self.codes(mutation))

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
        partial["changeControl"]["contractMigration"]["requiredSurfaces"].remove("compose")
        self.assertIn(autonomy_check.SYNTAX, self.codes(partial))

        late_resolution = copy.deepcopy(self.valid)
        late_resolution["changeControl"]["contractMigration"][
            "resolveBeforeConsumerExecution"
        ] = False
        self.assertIn(autonomy_check.SYNTAX, self.codes(late_resolution))

    def test_check_provenance_is_authoritative_and_unambiguous(self) -> None:
        ambiguous = copy.deepcopy(self.valid)
        ambiguous["changeControl"]["checkProvenance"]["duplicateContextPolicy"] = "prefer-success"
        self.assertIn(autonomy_check.BOUNDARY, self.codes(ambiguous))

        incomplete = copy.deepcopy(self.valid)
        incomplete["changeControl"]["checkProvenance"]["requiredBindings"].remove("event")
        self.assertIn(autonomy_check.SYNTAX, self.codes(incomplete))

        unsafe_status = copy.deepcopy(self.valid)
        unsafe_status["changeControl"]["checkProvenance"][
            "nonAuthoritativeStatusBlocksMerge"
        ] = True
        self.assertIn(autonomy_check.SYNTAX, self.codes(unsafe_status))

    def test_provider_read_fallback_preserves_authority(self) -> None:
        mutation = copy.deepcopy(self.valid)
        mutation["changeControl"]["providerReads"]["fallbackMustPreserveAuthority"] = False
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
        incomplete["changeControl"]["publicationConvergence"]["requiredRebindings"].remove(
            "approvalId"
        )
        self.assertIn(autonomy_check.SYNTAX, self.codes(incomplete))

    def test_superseded_work_is_lossless_and_never_orphaned(self) -> None:
        unproved = copy.deepcopy(self.valid)
        unproved["changeControl"]["supersededWork"]["losslessProofRequired"] = False
        self.assertIn(autonomy_check.SYNTAX, self.codes(unproved))

        incomplete = copy.deepcopy(self.valid)
        incomplete["changeControl"]["supersededWork"]["requiredBindings"].remove("receiptDigest")
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

    def test_strict_json_symlinks_non_object_profile_and_pointer_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            array_profile = tmp_root / "array.profile.json"
            array_profile.write_text("[]\n", encoding="utf-8")
            findings = autonomy_check.validate_document(self.valid, profile_path=array_profile)
            self.assertIn(autonomy_check.PROFILE, {finding.code for finding in findings})

            dup = tmp_root / "dup.json"
            dup.write_text('{"schema": "a", "schema": "b"}\n', encoding="utf-8")
            self.assertEqual(
                [autonomy_check.SYNTAX],
                [f.code for f in autonomy_check.load_and_validate(dup)],
            )

            deep = tmp_root / "deep.json"
            deep.write_text('{"a":' * 80 + "1" + "}" * 80, encoding="utf-8")
            self.assertEqual(
                [autonomy_check.SYNTAX],
                [f.code for f in autonomy_check.load_and_validate(deep)],
            )

            link = tmp_root / "link.json"
            link.symlink_to(self.valid_path)
            self.assertEqual(
                [autonomy_check.SYNTAX],
                [f.code for f in autonomy_check.load_and_validate(link)],
            )

            empty_dir = tmp_root / "empty"
            empty_dir.mkdir()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, autonomy_check.main(["validate", str(empty_dir)]))

        neg_case = {
            "schema": "wellmanifest.autonomy/invalid-case/v1",
            "base": "../valid/project.autonomy.json",
            "mutations": [{"op": "replace", "path": "/pipeline/states/-1", "value": "dispatch"}],
            "expectedCodes": [autonomy_check.SYNTAX],
        }
        _, ptr_findings = autonomy_check.apply_invalid_case(
            neg_case,
            ROOT / "examples" / "invalid" / "synthetic.json",
        )
        self.assertIn(autonomy_check.SYNTAX, {f.code for f in ptr_findings})

        glob_mutation = copy.deepcopy(self.valid)
        glob_mutation["grant"]["scope"]["pathAllow"] = ["src/.."]
        self.assertIn(autonomy_check.SYNTAX, self.codes(glob_mutation))

        ts_mutation = copy.deepcopy(self.valid)
        ts_mutation["grant"]["issuedAt"] = "2026-10-01 00:00:00+00:00"
        self.assertIn(autonomy_check.SYNTAX, self.codes(ts_mutation))
        with self.assertRaises(ValueError):
            autonomy_check.parse_at("2026-10-01 00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
