"""Pure conformance checks; this module neither grants nor executes authority."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

PROFILE = "wellmanifest.autonomy/supervisor-continuation/v1"
SHA = re.compile(r"^[a-f0-9]{40}$")
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
ASSISTANCE_PROFILE = "wellmanifest.autonomy/human-assistance/v1"
RISK_TIERS = {"low", "moderate", "high", "critical"}
HUMAN_DECISIONS = {"approve", "reject", "clarify", "withdraw", "expire"}
EFFECT_ACTIONS = {"dispatch_validation", "repair", "merge"}


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _subject_errors(subject: object) -> list[str]:
    if not isinstance(subject, dict):
        return ["SC-009"]
    required = ("repository", "ticket", "headSha", "baseSha", "profile")
    if not all(isinstance(subject.get(field), str) and subject[field].strip()
               for field in required):
        return ["SC-009"]
    if not SHA.fullmatch(subject["headSha"]) or not SHA.fullmatch(subject["baseSha"]):
        return ["SC-009"]
    if subject["profile"] != PROFILE:
        return ["SC-009"]
    return []


def check_human_request(record: dict) -> list[str]:
    """Validate a digest-bound request for human assistance.

    The checker validates shape and bindings only. A protected adapter must
    authenticate the caller and calculate ``requestDigest`` over the canonical
    request without that self-referential field.
    """
    if not isinstance(record, dict) or record.get("kind") != "human-assistance-request":
        return ["SC-009"]
    errors = []
    for field in ("requestId", "reason", "question"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append("SC-009")
    if not DIGEST.fullmatch(str(record.get("requestDigest", ""))):
        errors.append("SC-009")
    errors.extend(_subject_errors(record.get("subject")))
    if record.get("profile") != ASSISTANCE_PROFILE:
        errors.append("SC-009")
    if record.get("riskTier") not in RISK_TIERS:
        errors.append("SC-009")
    if record.get("requestedDecision") not in HUMAN_DECISIONS:
        errors.append("SC-009")
    issued = _parse_time(record.get("issuedAt"))
    expires = _parse_time(record.get("expiresAt"))
    if issued is None or expires is None or expires <= issued:
        errors.append("SC-009")
    if record.get("status") != "pending" or record.get("effectsFrozen") is not True:
        errors.append("SC-010")
    if (record.get("consentSource") in {"llm", "model", "agent"}
            or record.get("llmConsent") is True):
        errors.append("SC-011")
    return sorted(set(errors))


def check_human_response(record: dict, request: dict | None = None) -> list[str]:
    """Validate a human/external-authority response against one request."""
    if not isinstance(record, dict) or record.get("kind") != "human-assistance-response":
        return ["SC-011"]
    request = request if request is not None else record.get("request")
    errors = check_human_request(request) if isinstance(request, dict) else ["SC-009"]
    if errors:
        return sorted(set(errors))
    if record.get("requestId") != request.get("requestId"):
        errors.append("SC-011")
    if record.get("requestDigest") != request.get("requestDigest"):
        errors.append("SC-011")
    if record.get("subject") != request.get("subject"):
        errors.append("SC-011")
    if not DIGEST.fullmatch(str(record.get("responseDigest", ""))):
        errors.append("SC-011")
    actor = record.get("actor")
    if (not isinstance(actor, dict) or actor.get("kind") not in {"human", "external-authority"}
            or not isinstance(actor.get("id"), str) or not actor["id"].strip()):
        errors.append("SC-011")
    if record.get("decision") not in HUMAN_DECISIONS:
        errors.append("SC-011")
    responded = _parse_time(record.get("respondedAt"))
    issued = _parse_time(request.get("issuedAt"))
    expires = _parse_time(request.get("expiresAt"))
    if responded is None or issued is None or expires is None:
        errors.append("SC-011")
    elif responded < issued or responded >= expires:
        errors.append("SC-010")
    if (record.get("consentSource") in {"llm", "model", "agent"}
            or record.get("llmConsent") is True):
        errors.append("SC-011")
    conditions = record.get("conditions", [])
    if not isinstance(conditions, list) or len(conditions) > 20 or not all(
            isinstance(condition, str) and condition.strip() for condition in conditions):
        errors.append("SC-011")
    if conditions and not DIGEST.fullmatch(str(record.get("conditionsDigest", ""))):
        errors.append("SC-011")
    return sorted(set(errors))


def check_decision(record: dict) -> list[str]:
    """Check evidence facts produced by a protected runtime, not LLM assertions."""
    errors = []
    if not isinstance(record, dict):
        return ["AUTONOMY-SYNTAX-001"]
    action = record.get("action")
    if action not in {"request_human", "dispatch_validation", "wait", "repair",
                      "reconcile", "merge", "observe", "no_action"}:
        return ["AUTONOMY-SYNTAX-001"]
    if isinstance(record.get("humanRequest"), dict):
        errors.extend(check_human_request(record["humanRequest"]))
    if isinstance(record.get("humanResponse"), dict):
        errors.extend(check_human_response(record["humanResponse"], record.get("humanRequest")))
    if (record.get("validatorAvailable") is True
            and record.get("authorityVerified") is True
            and record.get("humanBoundary") is False
            and action == "request_human"):
        errors.append("SC-001")
    if action == "request_human":
        if (record.get("humanBoundary") is True and not isinstance(
                record.get("humanRequest"), dict)) or (
                record.get("humanBoundary") is not True
                and not (record.get("validatorAvailable") is True
                         and record.get("authorityVerified") is True)):
            errors.append("SC-009")
    if action == "wait" and record.get("humanBoundary") is True:
        request_errors = check_human_request(record.get("humanRequest", {}))
        if request_errors:
            errors.extend(request_errors)
        if record.get("effectsFrozen") is not True:
            errors.append("SC-010")
    if record.get("humanBoundary") is True and action in EFFECT_ACTIONS:
        response = record.get("humanResponse")
        if (not isinstance(response, dict) or response.get("decision") != "approve"
                or check_human_response(response, record.get("humanRequest"))):
            errors.append("SC-010")
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
    parser.add_argument("kind", choices=("decision", "adoption", "fleet",
                                          "human-request", "human-response"))
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    data = json.loads(args.file.read_text())
    if args.kind == "fleet":
        result = check_fleet(data["expected"], data["records"])
    elif args.kind == "human-request":
        errors = check_human_request(data)
        result = {"ok": not errors, "errors": errors}
    elif args.kind == "human-response":
        errors = check_human_response(data, data.get("request"))
        result = {"ok": not errors, "errors": errors}
    else:
        errors = (check_decision if args.kind == "decision" else check_adoption)(data)
        result = {"ok": not errors, "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
