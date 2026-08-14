# wellmanifest/autonomy

Normative Wellmanifest domain pack for autonomous software-development
continuation by a governed fleet of Subactor agents and Semcod tools.

After a project adopts this standard and an authorized principal issues an
active standing autonomy grant, qualifying work may be selected, implemented,
validated, opened as a pull request, approved by an independent trusted
Validator App, merged, verified, and followed by the next task without a human
approval on every pull request.

The grant is bounded. It cannot authorize its own renewal or expansion, and an
implementing agent cannot validate or approve its own change. Out-of-scope,
high-risk, destructive, secret-bearing, or ambiguous work fails closed and is
escalated.

## Repository boundary

This repository owns:

- the normative autonomy manifest and standing-grant semantics;
- agent-role separation, risk budgets, merge gates, and continuation rules;
- a Subactor/Semcod integration profile;
- deterministic conformance fixtures and a dependency-free validator.

This repository does not host an agent, GitHub App, queue, scheduler, LLM,
repository mirror, or mutation runtime. Those systems remain owned by
`subactor/*` and `semcod/*` and adopt this domain pack.

## Planned entry points

- `spec/AUTONOMY_STANDARD.md` — normative requirements;
- `schemas/autonomy-manifest.schema.json` — strict JSON contract;
- `profiles/subactor-semcod.profile.json` — integration profile;
- `src/autonomy_check.py` — deterministic conformance CLI;
- `docs/ARCHITECTURE.md` and `docs/LOGIC_FLOW.md` — deployment guidance.

Status: `0.1.0-dev`, governed implementation in `project/ticket-001`.
