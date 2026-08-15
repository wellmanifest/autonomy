# Subactor runtime ADOPT (Wellmanifest binding)

Normative autonomy remains **HOME** `wellmanifest/autonomy`.
Subactor products are **runtime owners** that **ADOPT** this pack.

## Fail-closed placement

| Field | Subactor runtime value |
| --- | --- |
| `home` | `subactor` |
| `shape` | `runtime_service` |
| `adopt` | includes `wellmanifest/autonomy` (and sibling packs as needed) |

`shape=runtime_service` **must not** set `home=wellmanifest`.
Phrase *"w ramach wellmanifest"* means ADOPT, not HOME.

## Machine-readable maps

1. **Integration profile (this pack):**
   `profiles/subactor-semcod.profile.json` — roles, stages, restrictions.
2. **Repo → pack matrix (Subactor runtime SSOT):**
   `repo://subactor/platform/config/adopt/wellmanifest.v1.json`

Deployment topology and procedures stay in
`repo://subactor/deployment/docs/{TOPOLOGY,PROCEDURES}.md`.
`semcod/redeploy` is a toolkit only.

## What not to invent

- A second "Subactor autonomy standard" that forks grant/merge semantics.
- Moving Platform or deployment narrative into wellmanifest as HOME.
- LLM-authored URI/vault/transport outside the approved capability catalog.
