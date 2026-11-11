import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from continuation_check import (  # noqa: E402
    check_adoption,
    check_decision,
    check_fleet,
    check_human_request,
    check_human_response,
)
from continuation_check import (
    main as continuation_main,
)


class ContinuationTests(unittest.TestCase):
    def human_request(self):
        return {
            "kind": "human-assistance-request",
            "requestId": "human-assist/example-1",
            "requestDigest": "sha256:" + "a" * 64,
            "profile": "wellmanifest.autonomy/human-assistance/v1",
            "subject": {
                "repository": "example/example-api",
                "ticket": "ticket-123",
                "headSha": "1" * 40,
                "baseSha": "2" * 40,
                "profile": "wellmanifest.autonomy/supervisor-continuation/v1",
            },
            "riskTier": "high",
            "reason": "production access is outside the standing grant",
            "question": "Approve the bounded production operation?",
            "requestedDecision": "approve",
            "issuedAt": "2026-09-15T08:00:00Z",
            "expiresAt": "2026-09-15T09:00:00Z",
            "status": "pending",
            "effectsFrozen": True,
        }

    def test_capability_does_not_grant_authority(self):
        self.assertIn(
            "SC-001",
            check_decision(
                {
                    "action": "dispatch_validation",
                    "validatorAvailable": True,
                    "authorityVerified": False,
                }
            ),
        )

    def test_authorized_independent_path_avoids_human_loop(self):
        evidence = {
            "validatorAvailable": True,
            "authorityVerified": True,
            "humanBoundary": False,
            "action": "request_human",
            "humanRequest": self.human_request(),
        }
        self.assertEqual(check_decision(evidence), ["SC-001"])
        evidence["humanBoundary"] = True
        self.assertEqual(check_decision(evidence), [])

    def test_human_assistance_is_digest_and_subject_bound(self):
        request = self.human_request()
        self.assertEqual(check_human_request(request), [])
        response = {
            "kind": "human-assistance-response",
            "request": request,
            "requestId": request["requestId"],
            "requestDigest": request["requestDigest"],
            "subject": request["subject"],
            "responseDigest": "sha256:" + "b" * 64,
            "actor": {"kind": "human", "id": "authority:founder"},
            "decision": "approve",
            "respondedAt": "2026-09-15T08:30:00Z",
            "conditions": ["one bounded operation"],
            "conditionsDigest": "sha256:" + "d" * 64,
        }
        self.assertEqual(check_human_response(response), [])
        response["subject"] = {**request["subject"], "headSha": "3" * 40}
        self.assertIn("SC-011", check_human_response(response))

    def test_waiting_for_human_freezes_effects_and_expiry_is_not_success(self):
        request = self.human_request()
        waiting = {
            "action": "wait",
            "humanBoundary": True,
            "humanRequest": request,
            "effectsFrozen": True,
        }
        self.assertEqual(check_decision(waiting), [])
        waiting["effectsFrozen"] = False
        self.assertIn("SC-010", check_decision(waiting))
        expired = {**request, "expiresAt": "2026-09-15T08:01:00Z"}
        response = {
            "kind": "human-assistance-response",
            "request": expired,
            "requestId": expired["requestId"],
            "requestDigest": expired["requestDigest"],
            "subject": expired["subject"],
            "responseDigest": "sha256:" + "c" * 64,
            "actor": {"kind": "human", "id": "authority:founder"},
            "decision": "approve",
            "respondedAt": "2026-09-15T08:30:00Z",
        }
        self.assertIn("SC-010", check_human_response(response))

    def test_llm_cannot_supply_consent_or_unbound_conditions(self):
        request = self.human_request()
        request["llmConsent"] = True
        self.assertIn("SC-011", check_human_request(request))
        request.pop("llmConsent")
        response = {
            "kind": "human-assistance-response",
            "request": request,
            "requestId": request["requestId"],
            "requestDigest": request["requestDigest"],
            "subject": request["subject"],
            "responseDigest": "sha256:" + "e" * 64,
            "actor": {"kind": "human", "id": "authority:founder"},
            "decision": "approve",
            "respondedAt": "2026-09-15T08:30:00Z",
            "conditions": ["bounded"],
            "consentSource": "llm",
        }
        self.assertIn("SC-011", check_human_response(response))

    def test_exact_frozen_handoff_and_duplicate_merge(self):
        evidence = {
            "action": "dispatch_validation",
            "validatorAvailable": True,
            "authorityVerified": True,
            "subjectCurrent": True,
            "independentActor": True,
            "checks": "success",
            "claimAcquired": True,
            "publicationKey": "protected-subject-1",
        }
        self.assertEqual(check_decision(evidence), [])
        for field, value, code in [
            ("checks", "pending", "SC-002"),
            ("subjectCurrent", False, "SC-001"),
            ("claimAcquired", False, "SC-004"),
            ("publicationKey", "   ", "SC-004"),
            ("publicationKey", True, "SC-004"),
            ("alreadyMerged", True, "SC-003"),
        ]:
            self.assertIn(code, check_decision({**evidence, field: value}))

    def test_polling_is_not_progress_or_llm_trigger(self):
        self.assertEqual(check_decision({"action": "observe", "llmInvoked": True}), ["SC-005"])
        self.assertEqual(
            check_decision({"action": "observe", "llmInvoked": True, "periodicReviewDue": True}), []
        )
        self.assertIn("SC-006", check_decision({"action": "reconcile", "effectCompleted": True}))

    def test_static_success_does_not_prove_runtime_adoption(self):
        record = {
            "applicable": True,
            "profile": "wellmanifest.autonomy/supervisor-continuation/v1",
            "revision": "a" * 40,
            "digest": "sha256:" + "b" * 64,
            "publishedRevisionVerified": True,
            "conformancePassed": True,
            "validationReceiptRef": "receipt://validation/1",
            "effectCapable": True,
        }
        self.assertEqual(check_adoption(record), ["SC-008"])
        record.update(runtimeReadbackVerified=True, runtimeReceiptRef="receipt://runtime/1")
        self.assertEqual(check_adoption(record), [])

    def test_fleet_cannot_hide_missing_duplicate_or_unknown_consumers(self):
        row = {
            "repository": "subactor/a",
            "applicable": False,
            "reason": "No control plane",
            "evidenceRef": "git://inspected/sha",
        }
        self.assertTrue(check_fleet(["subactor/a"], [row])["ok"])
        self.assertFalse(check_fleet(["subactor/a", "subactor/b"], [row])["ok"])
        self.assertFalse(check_fleet(["subactor/a"], [row, row])["ok"])
        self.assertFalse(check_fleet([], [row])["ok"])
        self.assertEqual(check_decision({}), ["AUTONOMY-SYNTAX-001"])

    def test_unhashable_and_non_dict_inputs_fail_closed_without_type_error(self):
        self.assertEqual(check_decision({"action": {"bad": 1}}), ["AUTONOMY-SYNTAX-001"])
        self.assertIn("SC-009", check_decision({"action": "observe", "humanRequest": "not-a-dict"}))
        self.assertIn(
            "SC-011", check_decision({"action": "observe", "humanResponse": ["not-a-dict"]})
        )

        bad_req = {
            **self.human_request(),
            "riskTier": {"unhashable": 1},
            "requestedDecision": ["unhashable"],
            "consentSource": {"nested": 1},
        }
        self.assertIn("SC-009", check_human_request(bad_req))

        valid_req = self.human_request()
        bad_resp = {
            "kind": "human-assistance-response",
            "request": valid_req,
            "requestId": valid_req["requestId"],
            "requestDigest": valid_req["requestDigest"],
            "subject": valid_req["subject"],
            "responseDigest": "sha256:" + "b" * 64,
            "actor": {"kind": ["unhashable"], "id": "authority:founder"},
            "decision": {"unhashable": 1},
            "respondedAt": "2026-09-15T08:30:00Z",
            "consentSource": ["unhashable"],
        }
        self.assertIn("SC-011", check_human_response(bad_resp))

        self.assertEqual(check_adoption(["not-a-dict"]), ["SC-008"])
        self.assertEqual(
            check_adoption({"applicable": False, "reason": "   ", "evidenceRef": "git://sha"}),
            ["SC-008"],
        )
        self.assertFalse(
            check_fleet(["subactor/a"], ["not-a-dict", {"repository": {"bad": 1}}])["ok"]
        )
        self.assertFalse(check_fleet([""], [])["ok"])

    def test_cli_rejects_symlinks_duplicate_keys_and_nonfinite_constants(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid_file = root / "decision.json"
            valid_file.write_text(json.dumps({"action": "observe"}), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = continuation_main(["decision", str(valid_file)])
            self.assertEqual(rc, 0)
            self.assertTrue(json.loads(buf.getvalue())["ok"])

            symlink_file = root / "link.json"
            os.symlink(valid_file, symlink_file)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = continuation_main(["decision", str(symlink_file)])
            self.assertEqual(rc, 1)
            self.assertEqual(json.loads(buf.getvalue())["errors"], ["AUTONOMY-SYNTAX-001"])

            dup_file = root / "dup.json"
            dup_file.write_text('{"action": "observe", "action": "merge"}', encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = continuation_main(["decision", str(dup_file)])
            self.assertEqual(rc, 1)

            nan_file = root / "nan.json"
            nan_file.write_text('{"action": "observe", "score": NaN}', encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = continuation_main(["decision", str(nan_file)])
            self.assertEqual(rc, 1)

            bad_fleet = root / "bad_fleet.json"
            bad_fleet.write_text('["not-an-object"]', encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = continuation_main(["fleet", str(bad_fleet)])
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
