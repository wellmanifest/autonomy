"""Pure conformance checks; this module neither grants nor executes authority."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PROFILE = "wellmanifest.autonomy/supervisor-continuation/v1"
SHA = re.compile(r"^[a-f0-9]{40}$")
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")


def check_decision(record: dict) -> list[str]:
    """Check evidence facts produced by a protected runtime, not LLM assertions."""
    errors = []
    if not isinstance(record, dict):
        return ["AUTONOMY-SYNTAX-001"]
    action = record.get("action")
    if action not in {"request_human", "dispatch_validation", "wait", "repair",
                      "reconcile", "merge", "observe", "no_action"}:
        return ["AUTONOMY-SYNTAX-001"]
    if (record.get("validatorAvailable") is True
            and record.get("authorityVerified") is True
            and record.get("humanBoundary") is False
            and action == "request_human"):
        errors.append("SC-001")
    if action == "dispatch_validation":
        if not all(record.get(k) is True for k in
                   ("validatorAvailable", "authorityVerified",
                    "subjectCurrent", "independentActor")):
            errors.append("SC-001")
        if record.get("checks") != "success":
            errors.append("SC-002")
        if record.get("claimAcquired") is not True or not record.get("publicationKey"):
            errors.append("SC-004")
    if record.get("alreadyMerged") is True and action in {"dispatch_validation", "merge"}:
        errors.append("SC-003")
    if record.get("llmInvoked") is True and not any(record.get(k) is True for k in
            ("semanticChange", "followUpDue", "periodicReviewDue", "initialAssessment")):
        errors.append("SC-005")
    if record.get("effectCompleted") is True and not all(record.get(k) is True for k in
            ("receiptVerified", "readbackVerified", "effectVerified", "subjectCurrent")):
        errors.append("SC-006")
    return sorted(set(errors))


def check_adoption(record: dict) -> list[str]:
    if record.get("applicable") is False:
        return [] if record.get("reason") and record.get("evidenceRef") else ["SC-008"]
    if record.get("applicable") is not True:
        return ["SC-008"]
    valid = (record.get("profile") == PROFILE
             and bool(SHA.fullmatch(str(record.get("revision", ""))))
             and bool(DIGEST.fullmatch(str(record.get("digest", ""))))
             and record.get("publishedRevisionVerified") is True
             and record.get("conformancePassed") is True
             and bool(record.get("validationReceiptRef")))
    if record.get("effectCapable") is not False:
        valid = valid and record.get("runtimeReadbackVerified") is True and bool(
            record.get("runtimeReceiptRef"))
    return [] if valid else ["SC-008"]


def check_fleet(expected: list[str], records: list[dict]) -> dict:
    """Missing or duplicate targets fail coverage; no inferred fleet membership."""
    by_repo = {}
    duplicates = set()
    for row in records:
        repo = row.get("repository")
        if repo in by_repo:
            duplicates.add(repo)
        by_repo[repo] = row
    expected_set = set(expected)
    failures = {repo: check_adoption(by_repo[repo]) if repo in by_repo else ["SC-008"]
                for repo in sorted(expected_set)}
    for repo in duplicates:
        failures[str(repo)] = ["SC-008"]
    unexpected = sorted(str(repo) for repo in set(by_repo) - expected_set)
    return {"ok": not unexpected and not duplicates and not any(failures.values()),
            "expected": len(expected_set), "unexpected": unexpected,
            "failures": {repo: codes for repo, codes in failures.items() if codes}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("decision", "adoption", "fleet"))
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    data = json.loads(args.file.read_text())
    if args.kind == "fleet":
        result = check_fleet(data["expected"], data["records"])
    else:
        errors = (check_decision if args.kind == "decision" else check_adoption)(data)
        result = {"ok": not errors, "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
