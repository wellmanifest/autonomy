import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from continuation_check import check_adoption, check_decision, check_fleet  # noqa: E402


class ContinuationTests(unittest.TestCase):
    def test_capability_does_not_grant_authority(self):
        self.assertIn("SC-001", check_decision({"action": "dispatch_validation",
                      "validatorAvailable": True, "authorityVerified": False}))

    def test_authorized_independent_path_avoids_human_loop(self):
        evidence = {"validatorAvailable": True, "authorityVerified": True,
                    "humanBoundary": False, "action": "request_human"}
        self.assertEqual(check_decision(evidence), ["SC-001"])
        evidence["humanBoundary"] = True
        self.assertEqual(check_decision(evidence), [])

    def test_exact_frozen_handoff_and_duplicate_merge(self):
        evidence = {"action": "dispatch_validation", "validatorAvailable": True,
                    "authorityVerified": True, "subjectCurrent": True,
                    "independentActor": True, "checks": "success",
                    "claimAcquired": True, "publicationKey": "protected-subject-1"}
        self.assertEqual(check_decision(evidence), [])
        for field, value, code in [("checks", "pending", "SC-002"),
                                   ("subjectCurrent", False, "SC-001"),
                                   ("claimAcquired", False, "SC-004"),
                                   ("alreadyMerged", True, "SC-003")]:
            self.assertIn(code, check_decision({**evidence, field: value}))

    def test_polling_is_not_progress_or_llm_trigger(self):
        self.assertEqual(check_decision({"action": "observe", "llmInvoked": True}), ["SC-005"])
        self.assertEqual(check_decision({"action": "observe", "llmInvoked": True,
                                       "periodicReviewDue": True}), [])
        self.assertIn("SC-006", check_decision({"action": "reconcile", "effectCompleted": True}))

    def test_static_success_does_not_prove_runtime_adoption(self):
        record = {"applicable": True, "profile": "wellmanifest.autonomy/supervisor-continuation/v1",
                  "revision": "a" * 40, "digest": "sha256:" + "b" * 64,
                  "publishedRevisionVerified": True, "conformancePassed": True,
                  "validationReceiptRef": "receipt://validation/1", "effectCapable": True}
        self.assertEqual(check_adoption(record), ["SC-008"])
        record.update(runtimeReadbackVerified=True, runtimeReceiptRef="receipt://runtime/1")
        self.assertEqual(check_adoption(record), [])

    def test_fleet_cannot_hide_missing_duplicate_or_unknown_consumers(self):
        row = {"repository": "subactor/a", "applicable": False,
               "reason": "No control plane", "evidenceRef": "git://inspected/sha"}
        self.assertTrue(check_fleet(["subactor/a"], [row])["ok"])
        self.assertFalse(check_fleet(["subactor/a", "subactor/b"], [row])["ok"])
        self.assertFalse(check_fleet(["subactor/a"], [row, row])["ok"])
        self.assertFalse(check_fleet([], [row])["ok"])
        self.assertEqual(check_decision({}), ["AUTONOMY-SYNTAX-001"])


if __name__ == "__main__":
    unittest.main()
