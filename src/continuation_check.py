"""Pure conformance checks; this module neither grants nor executes authority."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
from datetime import datetime
from pathlib import Path
from typing import Any

PROFILE = "wellmanifest.autonomy/supervisor-continuation/v1"
SHA = re.compile(r"^[a-f0-9]{40}$")
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
ASSISTANCE_PROFILE = "wellmanifest.autonomy/human-assistance/v1"
RISK_TIERS = {"low", "moderate", "high", "critical"}
HUMAN_DECISIONS = {"approve", "reject", "clarify", "withdraw", "expire"}
EFFECT_ACTIONS = {"dispatch_validation", "repair", "merge"}
DECISION_ACTIONS = {
    "request_human",
    "dispatch_validation",
    "wait",
    "repair",
    "reconcile",
    "merge",
    "observe",
    "no_action",
}
MAX_CONTINUATION_FILE_BYTES = 4 * 1024 * 1024
MAX_CONTINUATION_JSON_DEPTH = 64


def _is_nonempty_str(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_sha40(value: object) -> bool:
    return isinstance(value, str) and bool(SHA.fullmatch(value))


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and bool(DIGEST.fullmatch(value))


def _has_llm_consent_marker(record: dict[str, Any]) -> bool:
    source = record.get("consentSource")
    return (isinstance(source, str) and source in {"llm", "model", "agent"}) or record.get(
        "llmConsent"
    ) is True


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
    if not all(_is_nonempty_str(subject.get(field)) for field in required):
        return ["SC-009"]
    if not _is_sha40(subject["headSha"]) or not _is_sha40(subject["baseSha"]):
        return ["SC-009"]
    if subject["profile"] != PROFILE:
        return ["SC-009"]
    return []


def check_human_request(record: object) -> list[str]:
    """Validate a digest-bound request for human assistance.

    The checker validates shape and bindings only. A protected adapter must
    authenticate the caller and calculate ``requestDigest`` over the canonical
    request without that self-referential field.
    """
    if not isinstance(record, dict) or record.get("kind") != "human-assistance-request":
        return ["SC-009"]
    errors: list[str] = []
    for field in ("requestId", "reason", "question"):
        if not _is_nonempty_str(record.get(field)):
            errors.append("SC-009")
    if not _is_digest(record.get("requestDigest")):
        errors.append("SC-009")
    errors.extend(_subject_errors(record.get("subject")))
    if record.get("profile") != ASSISTANCE_PROFILE:
        errors.append("SC-009")
    risk_tier = record.get("riskTier")
    if not isinstance(risk_tier, str) or risk_tier not in RISK_TIERS:
        errors.append("SC-009")
    req_decision = record.get("requestedDecision")
    if not isinstance(req_decision, str) or req_decision not in HUMAN_DECISIONS:
        errors.append("SC-009")
    issued = _parse_time(record.get("issuedAt"))
    expires = _parse_time(record.get("expiresAt"))
    if issued is None or expires is None or expires <= issued:
        errors.append("SC-009")
    if record.get("status") != "pending" or record.get("effectsFrozen") is not True:
        errors.append("SC-010")
    if _has_llm_consent_marker(record):
        errors.append("SC-011")
    return sorted(set(errors))


def check_human_response(record: object, request: object = None) -> list[str]:
    """Validate a human/external-authority response against one request."""
    if not isinstance(record, dict) or record.get("kind") != "human-assistance-response":
        return ["SC-011"]
    bound_request = request if request is not None else record.get("request")
    if not isinstance(bound_request, dict):
        return ["SC-009"]
    errors = check_human_request(bound_request)
    if errors:
        return sorted(set(errors))
    if record.get("requestId") != bound_request.get("requestId"):
        errors.append("SC-011")
    if record.get("requestDigest") != bound_request.get("requestDigest"):
        errors.append("SC-011")
    if record.get("subject") != bound_request.get("subject"):
        errors.append("SC-011")
    if not _is_digest(record.get("responseDigest")):
        errors.append("SC-011")
    actor = record.get("actor")
    if (
        not isinstance(actor, dict)
        or not isinstance(actor.get("kind"), str)
        or actor["kind"] not in {"human", "external-authority"}
        or not _is_nonempty_str(actor.get("id"))
    ):
        errors.append("SC-011")
    decision = record.get("decision")
    if not isinstance(decision, str) or decision not in HUMAN_DECISIONS:
        errors.append("SC-011")
    responded = _parse_time(record.get("respondedAt"))
    issued = _parse_time(bound_request.get("issuedAt"))
    expires = _parse_time(bound_request.get("expiresAt"))
    if responded is None or issued is None or expires is None:
        errors.append("SC-011")
    elif responded < issued or responded >= expires:
        errors.append("SC-010")
    if _has_llm_consent_marker(record):
        errors.append("SC-011")
    conditions = record.get("conditions", [])
    if (
        not isinstance(conditions, list)
        or len(conditions) > 20
        or not all(_is_nonempty_str(condition) for condition in conditions)
    ):
        errors.append("SC-011")
    if conditions and not _is_digest(record.get("conditionsDigest")):
        errors.append("SC-011")
    return sorted(set(errors))


def check_decision(record: object) -> list[str]:
    """Check evidence facts produced by a protected runtime, not LLM assertions."""
    if not isinstance(record, dict):
        return ["AUTONOMY-SYNTAX-001"]
    action = record.get("action")
    if not isinstance(action, str) or action not in DECISION_ACTIONS:
        return ["AUTONOMY-SYNTAX-001"]
    errors: list[str] = []
    if "humanRequest" in record and record["humanRequest"] is not None:
        errors.extend(
            check_human_request(record["humanRequest"])
            if isinstance(record["humanRequest"], dict)
            else ["SC-009"]
        )
    if "humanResponse" in record and record["humanResponse"] is not None:
        errors.extend(
            check_human_response(record["humanResponse"], record.get("humanRequest"))
            if isinstance(record["humanResponse"], dict)
            else ["SC-011"]
        )
    if (
        record.get("validatorAvailable") is True
        and record.get("authorityVerified") is True
        and record.get("humanBoundary") is False
        and action == "request_human"
    ):
        errors.append("SC-001")
    if action == "request_human":
        if (
            record.get("humanBoundary") is True and not isinstance(record.get("humanRequest"), dict)
        ) or (
            record.get("humanBoundary") is not True
            and not (
                record.get("validatorAvailable") is True and record.get("authorityVerified") is True
            )
        ):
            errors.append("SC-009")
    if action == "wait" and record.get("humanBoundary") is True:
        request_errors = check_human_request(record.get("humanRequest"))
        if request_errors:
            errors.extend(request_errors)
        if record.get("effectsFrozen") is not True:
            errors.append("SC-010")
    if record.get("humanBoundary") is True and action in EFFECT_ACTIONS:
        response = record.get("humanResponse")
        if (
            not isinstance(response, dict)
            or response.get("decision") != "approve"
            or check_human_response(response, record.get("humanRequest"))
        ):
            errors.append("SC-010")
    if action == "dispatch_validation":
        if not all(
            record.get(k) is True
            for k in (
                "validatorAvailable",
                "authorityVerified",
                "subjectCurrent",
                "independentActor",
            )
        ):
            errors.append("SC-001")
        if record.get("checks") != "success":
            errors.append("SC-002")
        if record.get("claimAcquired") is not True or not _is_nonempty_str(
            record.get("publicationKey")
        ):
            errors.append("SC-004")
    if record.get("alreadyMerged") is True and action in {"dispatch_validation", "merge"}:
        errors.append("SC-003")
    if record.get("llmInvoked") is True and not any(
        record.get(k) is True
        for k in ("semanticChange", "followUpDue", "periodicReviewDue", "initialAssessment")
    ):
        errors.append("SC-005")
    if record.get("effectCompleted") is True and not all(
        record.get(k) is True
        for k in ("receiptVerified", "readbackVerified", "effectVerified", "subjectCurrent")
    ):
        errors.append("SC-006")
    return sorted(set(errors))


def check_adoption(record: object) -> list[str]:
    if not isinstance(record, dict):
        return ["SC-008"]
    if record.get("applicable") is False:
        return (
            []
            if _is_nonempty_str(record.get("reason"))
            and _is_nonempty_str(record.get("evidenceRef"))
            else ["SC-008"]
        )
    if record.get("applicable") is not True:
        return ["SC-008"]
    valid = (
        record.get("profile") == PROFILE
        and _is_sha40(record.get("revision"))
        and _is_digest(record.get("digest"))
        and record.get("publishedRevisionVerified") is True
        and record.get("conformancePassed") is True
        and _is_nonempty_str(record.get("validationReceiptRef"))
    )
    if record.get("effectCapable") is not False:
        valid = (
            valid
            and record.get("runtimeReadbackVerified") is True
            and _is_nonempty_str(record.get("runtimeReceiptRef"))
        )
    return [] if valid else ["SC-008"]


def check_fleet(expected: object, records: object) -> dict[str, Any]:
    """Missing or duplicate targets fail coverage; no inferred fleet membership."""
    if not isinstance(expected, list) or not all(_is_nonempty_str(repo) for repo in expected):
        return {
            "ok": False,
            "expected": 0,
            "unexpected": [],
            "failures": {"<expected>": ["SC-008"]},
        }
    if not isinstance(records, list):
        return {
            "ok": False,
            "expected": len(set(expected)),
            "unexpected": [],
            "failures": {"<records>": ["SC-008"]},
        }
    by_repo: dict[str, dict[str, Any]] = {}
    duplicates: set[str] = set()
    invalid_rows = 0
    for row in records:
        if not isinstance(row, dict):
            invalid_rows += 1
            continue
        repo = row.get("repository")
        if not _is_nonempty_str(repo):
            invalid_rows += 1
            continue
        assert isinstance(repo, str)
        if repo in by_repo:
            duplicates.add(repo)
        by_repo[repo] = row
    expected_set = set(expected)
    failures: dict[str, list[str]] = {
        repo: check_adoption(by_repo[repo]) if repo in by_repo else ["SC-008"]
        for repo in sorted(expected_set)
    }
    for repo in sorted(duplicates):
        failures[repo] = ["SC-008"]
    if invalid_rows:
        failures["<invalid-record>"] = ["SC-008"]
    unexpected = sorted(set(by_repo) - expected_set)
    return {
        "ok": not unexpected and not duplicates and not invalid_rows and not any(failures.values()),
        "expected": len(expected_set),
        "unexpected": unexpected,
        "failures": {repo: codes for repo, codes in failures.items() if codes},
    }


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _reject_nonfinite(constant: str) -> Any:
    raise ValueError(f"non-finite JSON constant: {constant}")


def _load_json_file(path: Path) -> Any:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(os.fspath(path), flags)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise ValueError("input must be a regular file")
        if st.st_size > MAX_CONTINUATION_FILE_BYTES:
            raise ValueError("input exceeds maximum byte budget")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_CONTINUATION_FILE_BYTES:
                raise ValueError("input exceeds maximum byte budget")
            chunks.append(chunk)
    finally:
        os.close(fd)
    text = b"".join(chunks).decode("utf-8")
    try:
        parsed = json.loads(
            text, object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_nonfinite
        )
    except RecursionError as error:
        raise ValueError("JSON nesting depth exceeded") from error
    stack: list[tuple[Any, int]] = [(parsed, 0)]
    while stack:
        current, depth = stack.pop()
        if depth > MAX_CONTINUATION_JSON_DEPTH:
            raise ValueError("JSON nesting depth exceeded")
        if isinstance(current, dict):
            stack.extend(
                (val, depth + 1) for val in current.values() if isinstance(val, (dict, list))
            )
        elif isinstance(current, list):
            stack.extend((val, depth + 1) for val in current if isinstance(val, (dict, list)))
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "kind", choices=("decision", "adoption", "fleet", "human-request", "human-response")
    )
    parser.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    try:
        data = _load_json_file(args.file)
    except (OSError, UnicodeDecodeError, ValueError, RecursionError):
        result: dict[str, Any] = {"ok": False, "errors": ["AUTONOMY-SYNTAX-001"]}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1
    if args.kind == "fleet":
        if not isinstance(data, dict) or "expected" not in data or "records" not in data:
            result = {"ok": False, "errors": ["AUTONOMY-SYNTAX-001"]}
        else:
            result = check_fleet(data["expected"], data["records"])
    elif args.kind == "human-request":
        errors = check_human_request(data)
        result = {"ok": not errors, "errors": errors}
    elif args.kind == "human-response":
        req = data.get("request") if isinstance(data, dict) else None
        errors = check_human_response(data, req)
        result = {"ok": not errors, "errors": errors}
    else:
        errors = (check_decision if args.kind == "decision" else check_adoption)(data)
        result = {"ok": not errors, "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
