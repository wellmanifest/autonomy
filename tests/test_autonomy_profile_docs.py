from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AutonomyProfileAndDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile_path = ROOT / "profiles" / "subactor-semcod.profile.json"
        cls.profile = json.loads(cls.profile_path.read_text(encoding="utf-8"))

    def test_all_owned_python_modules_stay_under_500_lines(self) -> None:
        for folder in (ROOT / "src", ROOT / "tests"):
            for py_file in sorted(folder.glob("*.py")):
                line_count = len(py_file.read_text(encoding="utf-8").splitlines())
                self.assertLess(
                    line_count,
                    500,
                    f"{py_file.relative_to(ROOT)} has {line_count} lines (>= 500)",
                )

    def test_stable_profile_binds_deployed_durable_controller(self) -> None:
        self.assertEqual("0.8.1", self.profile["version"])
        self.assertEqual("stable", self.profile["status"])
        self.assertIn("subactor/platform", self.profile["ownership"]["runtimeOwners"])
        self.assertIn("subactor/deployment", self.profile["ownership"]["runtimeOwners"])
        self.assertTrue(
            any(
                b["product"] == "subactor/deployment" and b["stage"] == "observe"
                for b in self.profile["bindings"]
            )
        )
        self.assertTrue(self.profile["protectedBoundaries"]["heartbeatEvidenceExternal"])
        self.assertTrue(self.profile["protectedBoundaries"]["invocationCorrelationProtected"])
        self.assertTrue(self.profile["protectedBoundaries"]["effectReceiptExternal"])
        dispatch = next(
            binding
            for binding in self.profile["bindings"]
            if binding["stage"] == "dispatch" and binding["product"] == "subactor/autonom"
        )
        publish = next(
            binding
            for binding in self.profile["bindings"]
            if binding["stage"] == "publish" and binding["product"] == "subactor/autonom"
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
                "scheduler-heartbeat",
                "missed-cycle-recovery",
                "correlation-bound-run-selection",
                "post-boundary-run-discovery",
                "matrix-child-correlation",
                "late-delivery-deduplication",
                "human-assistance-request",
                "human-assistance-wait",
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
                "repo://subactor/validator-agent/.github/workflows/validator.yml",
                "repo://subactor/validator-agent/bin/dispatch-direct-pr.sh",
            },
            set(dispatch["contracts"]),
        )
        for restriction in (
            "lease-exceeds-effect-timeout",
            "candidate-checkout-excluded",
            "runtime-checkout-isolated",
            "supervisor-checkout-excluded",
            "policy-checkout-isolated",
            "rollout-trigger-quiesced",
            "rollback-same-boundary",
            "intent-before-implementation",
            "exact-contract-version-allowlist",
            "all-validation-surfaces",
            "bounded-provider-retries",
            "human-assistance-request-bound",
            "human-assistance-effects-frozen",
        ):
            self.assertIn(restriction, dispatch["restrictions"])
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
                "idempotent-effect-reconciliation",
                "already-applied-exact-receipt",
            },
            set(publish["capabilities"]),
        )
        for restriction in (
            "native-auto-merge-forbidden",
            "history-rewrite-forbidden",
            "ambiguous-check-contexts-fail-closed",
            "non-authoritative-status-ignored",
            "registry-drift-fails-closed",
            "approval-starts-new-evidence-epoch",
            "approval-triggered-checks-deferred-before-review",
            "post-approval-attempt-required",
            "delete-proven-equivalent-branch-after-integrated-proof",
            "provider-coupled-close-read-back",
            "unresolved-superseded-pr-remains-open",
            "at-most-one-authoritative-effect",
            "duplicate-review-merge-forbidden",
            "orphan-branch-preservation-policy",
            "provider-branch-inventory-authority",
            "human-assistance-response-bound",
            "human-assistance-approval-does-not-widen-grant",
        ):
            self.assertIn(restriction, publish["restrictions"])

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
            "MUST NOT repair, synthesize, or\nreplace the missing scheduler heartbeat",
            "MUST carry a stable correlation\nID into the provider's run identity",
            "pre-boundary run or a child\nfrom a different matrix invocation",
            "It MUST NOT submit\na second review or merge request",
            "closed-unmerged pull request is not an already-applied merge",
            "non-default branches with no authoritative owner mapping are treated as\n"
            "   unresolved work and MUST be preserved",
            "structured human-assistance request",
            "`effectsFrozen=true`",
            "MUST NOT\nedit, push, approve, merge, acquire a secret",
            "silently infer consent from\nan LLM",
            "exact, non-expired `approve` response",
        )
        for phrase in required_text:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, standard)

    def test_live_evidence_is_scoped_and_does_not_overclaim_watchdog_recovery(self) -> None:
        architecture = (ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
        for expected in (
            "fd960b35a9816246aec2629f619cf9ce42e68892fb8bab806697768f4ab795e2",
            "manual_dispatch=false",
            "giving a 50-minute lease for a service bounded to\n45 minutes",
            "No live missed-trigger watchdog recovery had been observed",
            "MUST NOT be presented as full operational\nconformance",
            "protected_registry_digest_mismatch",
            "4c2519ef8d4c4a632907d570ddb4b7aba81aa7b8dc5e24e77cc9f611bc9c19ea",
            "failed in `ExecStartPre`",
            "No Python controller was loaded",
            "c5ba6476482e20eaf0d1a01727cc9565cec977fe30c14712dd048eb4df3f85c0",
            "31830719505",
            "4940318952",
            "88953aa58a48526caf1134ba40b04d0f39e3ff39",
            "`ok=true`, `dry_run=false`, zero mutations",
            "31843668089",
            "31844397273",
            "GOV-BRANCH-LIFECYCLE-002",
            "31854603326",
            "4942176742",
            "31854007167",
            "3fe9659011372b734bc24302ed83eb0b49f9c95f",
        ):
            self.assertIn(expected, architecture)

    def test_public_schema_is_draft_2020_12_and_closed(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "autonomy-manifest.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual("https://wellmanifest.com/schemas/autonomy-manifest/v6", schema["$id"])
        self.assertFalse(schema["$defs"]["manifest"]["additionalProperties"])
        self.assertFalse(schema["$defs"]["profile"]["additionalProperties"])
        manifest_properties = schema["$defs"]["manifest"]["properties"]
        self.assertFalse(
            manifest_properties["queue"]["properties"]["effectReconciliation"][
                "additionalProperties"
            ]
        )
        self.assertFalse(
            manifest_properties["executionLiveness"]["properties"]["heartbeat"][
                "additionalProperties"
            ]
        )


if __name__ == "__main__":
    unittest.main()
