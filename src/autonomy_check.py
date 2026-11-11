#!/usr/bin/env python3
"""Dependency-free conformance checker for Wellmanifest Autonomy 0.8."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

_SRC_DIR = str(Path(__file__).resolve().parent)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from autonomy_change_shapes import ValidatorChangeShapesMixin  # noqa: E402
from autonomy_constants import (  # noqa: E402
    AUTHORITIES,
    BOUNDARY,
    CONTINUATION,
    CRITICAL_CODES,
    DEFAULT_PROFILE,
    DIGEST_RE,
    DIMENSIONS,
    ENV_RE,
    GRANT,
    HEAD,
    ID_RE,
    MANDATORY_EXCLUDED_EFFECTS,
    MAX_JSON_BYTES,
    MAX_JSON_DEPTH,
    PIPELINE_STATES,
    POLICY,
    PROFILE,
    PROVIDER_COUPLED_READ_BACKS,
    REPOSITORY_RE,
    REQUIRED_ACTIONS,
    REQUIRED_ALREADY_APPLIED_BINDINGS,
    REQUIRED_BINDINGS,
    REQUIRED_CANARY_RECEIPTS,
    REQUIRED_CHECK_PROVENANCE_BINDINGS,
    REQUIRED_CHECKS,
    REQUIRED_CONSUMER_SURFACES,
    REQUIRED_EFFECT_BINDINGS,
    REQUIRED_GATES,
    REQUIRED_IDEMPOTENCY_BINDINGS,
    REQUIRED_INVOCATION_BINDINGS,
    REQUIRED_POLICY_REBINDINGS,
    REQUIRED_RECEIPTS,
    REQUIRED_REGISTRY_BINDINGS,
    REQUIRED_STOP_CONDITIONS,
    REQUIRED_SUPERSESSION_BINDINGS,
    RFC3339_OFFSET_RE,
    RFC6901_INDEX_RE,
    RISK,
    RISK_ORDER,
    ROLE_AUTHORITY_CEILINGS,
    ROLES,
    ROOT,
    SEMVER_RE,
    SEPARATION,
    SHA_RE,
    SUPERSESSION_CLOSURE_MODES,
    SYNTAX,
    URI_RE,
    Finding,
    StrictJsonError,
    safe_read_json,
)
from autonomy_liveness_shapes import ValidatorLivenessShapesMixin  # noqa: E402
from autonomy_primitives import ValidatorPrimitivesMixin  # noqa: E402
from autonomy_semantics import ValidatorSemanticsMixin  # noqa: E402

__all__ = [
    "AUTHORITIES",
    "BOUNDARY",
    "CONTINUATION",
    "CRITICAL_CODES",
    "DEFAULT_PROFILE",
    "DIGEST_RE",
    "DIMENSIONS",
    "ENV_RE",
    "GRANT",
    "HEAD",
    "ID_RE",
    "MANDATORY_EXCLUDED_EFFECTS",
    "MAX_JSON_BYTES",
    "MAX_JSON_DEPTH",
    "PIPELINE_STATES",
    "POLICY",
    "PROFILE",
    "PROVIDER_COUPLED_READ_BACKS",
    "REPOSITORY_RE",
    "REQUIRED_ACTIONS",
    "REQUIRED_ALREADY_APPLIED_BINDINGS",
    "REQUIRED_BINDINGS",
    "REQUIRED_CANARY_RECEIPTS",
    "REQUIRED_CHECK_PROVENANCE_BINDINGS",
    "REQUIRED_CHECKS",
    "REQUIRED_CONSUMER_SURFACES",
    "REQUIRED_EFFECT_BINDINGS",
    "REQUIRED_GATES",
    "REQUIRED_IDEMPOTENCY_BINDINGS",
    "REQUIRED_INVOCATION_BINDINGS",
    "REQUIRED_POLICY_REBINDINGS",
    "REQUIRED_RECEIPTS",
    "REQUIRED_REGISTRY_BINDINGS",
    "REQUIRED_STOP_CONDITIONS",
    "REQUIRED_SUPERSESSION_BINDINGS",
    "RISK",
    "RISK_ORDER",
    "ROLE_AUTHORITY_CEILINGS",
    "ROLES",
    "ROOT",
    "SEMVER_RE",
    "SEPARATION",
    "SHA_RE",
    "SUPERSESSION_CLOSURE_MODES",
    "SYNTAX",
    "URI_RE",
    "Finding",
    "Validator",
    "apply_invalid_case",
    "iter_json_paths",
    "load_and_validate",
    "main",
    "parse_at",
    "render",
    "self_test",
    "validate_document",
]


class Validator(
    ValidatorPrimitivesMixin,
    ValidatorLivenessShapesMixin,
    ValidatorChangeShapesMixin,
    ValidatorSemanticsMixin,
):
    def __init__(self, *, at: datetime | None = None, profile_path: Path | None = None) -> None:
        self.at = at
        self.profile_path = profile_path
        self.findings: list[Finding] = []

    def verify_selected_profile(self, doc: dict[str, Any], path: str) -> None:
        profile_path = self.profile_path
        if profile_path is None:
            profile_path = DEFAULT_PROFILE
        try:
            raw, profile = safe_read_json(profile_path)
        except StrictJsonError as error:
            self.add(PROFILE, f"{path}.subject.profile", f"cannot read selected profile: {error}")
            return
        profile_validator = Validator(profile_path=None)
        before = len(profile_validator.findings)
        if (
            profile_validator.profile_shape(profile, "$.profile")
            and len(profile_validator.findings) == before
            and isinstance(profile, dict)
        ):
            profile_validator.profile_semantics(profile, "$.profile")
        for finding in profile_validator.findings:
            self.add(PROFILE, finding.path, finding.message)
        if not isinstance(profile, dict):
            return
        subject = doc.get("subject", {}) if isinstance(doc.get("subject"), dict) else {}
        selected = subject.get("profile", {}) if isinstance(subject.get("profile"), dict) else {}
        actual_digest = f"sha256:{hashlib.sha256(raw).hexdigest()}"
        if selected.get("id") != profile.get("id") or selected.get("version") != profile.get(
            "version"
        ):
            self.add(
                PROFILE,
                f"{path}.subject.profile",
                "selected profile ID/version does not match the profile file",
            )
        if selected.get("digest") != actual_digest:
            self.add(
                PROFILE,
                f"{path}.subject.profile.digest",
                "selected profile digest does not match exact bytes",
            )


def parse_at(value: str | None) -> datetime | None:
    if value is None:
        return None
    if RFC3339_OFFSET_RE.fullmatch(value) is None:
        raise ValueError("evaluation time must be an RFC 3339 date-time with offset")
    normalized = f"{value[:-1]}+00:00" if value.endswith(("Z", "z")) else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("evaluation time must include an offset")
    return parsed


def _resolve_array_index(token: str, length: int) -> int:
    if RFC6901_INDEX_RE.fullmatch(token) is None:
        raise IndexError(token)
    index = int(token)
    if index >= length:
        raise IndexError(token)
    return index


def _has_symlink_between(root: Path, candidate: Path) -> bool:
    current = candidate
    while True:
        if current.is_symlink():
            return True
        if current == root or current.parent == current:
            return current.is_symlink()
        current = current.parent


def apply_invalid_case(
    document: dict[str, Any], path: Path
) -> tuple[dict[str, Any] | None, list[Finding]]:
    validator = Validator()
    fields = ("schema", "base", "mutations", "expectedCodes")
    if not validator.closed(document, "$", fields, fields):
        return None, validator.findings
    if document.get("schema") != "wellmanifest.autonomy/invalid-case/v1":
        validator.add(SYNTAX, "$.schema", "unknown invalid-case version")
        return None, validator.findings
    base_value = document.get("base")
    if not isinstance(base_value, str) or not base_value or "\\" in base_value:
        validator.add(SYNTAX, "$.base", "expected a relative base path")
        return None, validator.findings
    if path.is_symlink() or path.parent.is_symlink() or path.parent.parent.is_symlink():
        validator.add(RISK, "$.base", "symlinks are forbidden in invalid-case paths")
        return None, validator.findings
    examples_root = path.parent.parent.resolve()
    raw_target = path.parent / base_value
    base_path = raw_target.resolve()
    try:
        base_path.relative_to(examples_root)
    except ValueError:
        validator.add(RISK, "$.base", "base path escapes the examples root")
        return None, validator.findings
    if _has_symlink_between(examples_root, raw_target) or _has_symlink_between(
        examples_root, base_path
    ):
        validator.add(RISK, "$.base", "symlinks are forbidden in invalid-case paths")
        return None, validator.findings
    if base_path.parent.name != "valid" or base_path.parent.parent != examples_root:
        validator.add(SYNTAX, "$.base", "base must resolve inside examples/valid")
        return None, validator.findings
    try:
        _, candidate = safe_read_json(base_path)
    except StrictJsonError as error:
        validator.add(SYNTAX, "$.base", f"cannot load base manifest: {error}")
        return None, validator.findings
    if not isinstance(candidate, dict):
        validator.add(SYNTAX, "$.base", "base manifest must be a JSON object")
        return None, validator.findings
    mutations = document.get("mutations")
    if not isinstance(mutations, list) or not mutations:
        validator.add(SYNTAX, "$.mutations", "expected at least one mutation")
        return None, validator.findings
    for index, mutation in enumerate(mutations):
        item_path = f"$.mutations[{index}]"
        if not validator.closed(
            mutation, item_path, ("op", "path", "value"), ("op", "path", "value")
        ):
            continue
        if mutation.get("op") != "replace":
            validator.add(RISK, f"{item_path}.op", "invalid cases allow replace only")
            continue
        pointer = mutation.get("path")
        if not isinstance(pointer, str) or not pointer.startswith("/") or pointer == "/":
            validator.add(SYNTAX, f"{item_path}.path", "expected a non-root JSON pointer")
            continue
        parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]
        target: Any = candidate
        try:
            for part in parts[:-1]:
                if isinstance(target, list):
                    target = target[_resolve_array_index(part, len(target))]
                elif isinstance(target, dict):
                    if part not in target:
                        raise KeyError(part)
                    target = target[part]
                else:
                    raise TypeError("non-container target")
            leaf = parts[-1]
            if isinstance(target, list):
                target[_resolve_array_index(leaf, len(target))] = copy.deepcopy(
                    mutation.get("value")
                )
            elif isinstance(target, dict):
                if leaf not in target:
                    raise KeyError(leaf)
                target[leaf] = copy.deepcopy(mutation.get("value"))
            else:
                raise TypeError("non-container target")
        except (KeyError, IndexError, ValueError, TypeError):
            validator.add(SYNTAX, f"{item_path}.path", "pointer does not select an existing value")
    expected = validator.string_set(document.get("expectedCodes"), "$.expectedCodes", minimum=1)
    if expected is not None:
        unknown = set(expected) - {SYNTAX, POLICY, BOUNDARY}
        if unknown:
            validator.add(SYNTAX, "$.expectedCodes", f"unknown diagnostic codes: {sorted(unknown)}")
    return candidate, validator.findings


def validate_document(
    document: Any,
    *,
    at: datetime | None = None,
    profile_path: Path | None = DEFAULT_PROFILE,
    path: str = "$",
) -> list[Finding]:
    validator = Validator(at=at, profile_path=profile_path)
    if not isinstance(document, dict):
        validator.add(SYNTAX, path, "expected a JSON object")
        return validator.findings
    schema = document.get("schema")
    if schema == "wellmanifest.autonomy/manifest/v6":
        before = len(validator.findings)
        if validator.manifest_shape(document, path) and len(validator.findings) == before:
            validator.manifest_semantics(document, path)
    elif schema == "wellmanifest.autonomy/profile/v6":
        before = len(validator.findings)
        if validator.profile_shape(document, path) and len(validator.findings) == before:
            validator.profile_semantics(document, path)
    else:
        validator.add(SYNTAX, f"{path}.schema", "unknown document schema")
    return sorted(
        validator.findings, key=lambda finding: (finding.code, finding.path, finding.message)
    )


def load_and_validate(
    path: Path,
    *,
    at: datetime | None = None,
    profile_path: Path | None = DEFAULT_PROFILE,
) -> list[Finding]:
    try:
        _, document = safe_read_json(path)
    except StrictJsonError as error:
        return [Finding(SYNTAX, "$", f"cannot load JSON: {error}", "error")]
    overlay_findings: list[Finding] = []
    if (
        isinstance(document, dict)
        and document.get("schema") == "wellmanifest.autonomy/invalid-case/v1"
    ):
        document, overlay_findings = apply_invalid_case(document, path)
        if document is None:
            return overlay_findings
    return overlay_findings + validate_document(document, at=at, profile_path=profile_path)


def iter_json_paths(paths: list[Path]) -> list[Path]:
    discovered: list[Path] = []
    for path in paths:
        if path.is_symlink() or not path.is_dir():
            discovered.append(path)
            continue
        dir_items: list[Path] = []
        for root_dir, dirs, files in os.walk(path, topdown=True, followlinks=False):
            root_path = Path(root_dir)
            dirs.sort()
            kept_dirs: list[str] = []
            for dname in dirs:
                candidate_dir = root_path / dname
                if candidate_dir.is_symlink():
                    dir_items.append(candidate_dir)
                else:
                    kept_dirs.append(dname)
            dirs[:] = kept_dirs
            for fname in sorted(files):
                candidate_file = root_path / fname
                if candidate_file.is_symlink() or fname.endswith(".json"):
                    dir_items.append(candidate_file)
        discovered.extend(sorted(dir_items) if dir_items else [path])
    return discovered


def render(path: Path, findings: list[Finding], output_format: str) -> str:
    if output_format == "json":
        payload = {
            "schema": "wellmanifest.autonomy/findings/v1",
            "producer": "wellmanifest.autonomy-check",
            "path": path.as_posix(),
            "valid": not findings,
            "findings": [asdict(finding) for finding in findings],
        }
        return json.dumps(payload, sort_keys=True)
    if not findings:
        return f"PASS {path.as_posix()}"
    return "\n".join(
        f"{finding.severity.upper()} {finding.code} "
        f"{path.as_posix()}:{finding.path} {finding.message}"
        for finding in findings
    )


def self_test() -> int:
    valid_path = ROOT / "examples" / "valid" / "project.autonomy.json"
    valid_findings = load_and_validate(valid_path)
    if valid_findings:
        print(render(valid_path.relative_to(ROOT), valid_findings, "text"), file=sys.stderr)
        return 1
    for path in sorted((ROOT / "examples" / "invalid").glob("*.json")):
        _, case = safe_read_json(path)
        expected = set(case["expectedCodes"])
        findings = load_and_validate(path)
        observed = {finding.code for finding in findings}
        if not expected <= observed:
            print(
                f"FAIL {path.relative_to(ROOT)} expected {sorted(expected)}, "
                f"observed {sorted(observed)}",
                file=sys.stderr,
            )
            return 1
    _, profile = safe_read_json(DEFAULT_PROFILE)
    profile_findings = validate_document(profile, profile_path=None)
    if profile_findings:
        print(render(DEFAULT_PROFILE.relative_to(ROOT), profile_findings, "text"), file=sys.stderr)
        return 1
    print("PASS autonomy self-test")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="autonomy-check")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser(
        "validate", help="validate manifests, profiles, or directories"
    )
    validate_parser.add_argument("paths", nargs="+", type=Path)
    validate_parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    validate_parser.add_argument("--at", help="evaluate grant activity at an RFC 3339 time")
    validate_parser.add_argument("--format", choices=("text", "json"), default="text")
    subparsers.add_parser("self-test", help="run bundled positive and negative conformance cases")
    args = parser.parse_args(argv)

    if args.command == "self-test":
        return self_test()

    try:
        at = parse_at(args.at)
    except ValueError as error:
        parser.error(str(error))
    failed = False
    for path in iter_json_paths(args.paths):
        findings = load_and_validate(path, at=at, profile_path=args.profile)
        print(render(path, findings, args.format))
        failed = failed or bool(findings)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
