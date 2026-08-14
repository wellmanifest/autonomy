# AUTONOMY-SYNTAX-001

## Meaning

The document does not conform to the closed Autonomy JSON shape, type,
vocabulary, URI, digest, timestamp, or version rules.

## Cause

A required field is absent, an unknown field is present, a value has the wrong
type or format, or an invalid conformance-case overlay was supplied.

## Resolution

Validate against `schemas/autonomy-manifest.schema.json`, correct the reported
path, and rerun `autonomy-check`. Do not ignore or silently preserve unknown
authority fields.
