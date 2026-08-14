# Wellmanifest Autonomy Standard 0.1

Status: experimental

Namespace: `wellmanifest.autonomy`

Normative keywords: MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT and MAY are to
be interpreted as requirement levels.

## 1. Purpose

This standard defines how a software repository delegates continuing
development to a governed fleet of agents. A conforming deployment can select
routine work, change code, create a pull request, obtain independent automated
approval, merge, verify the result, and select the next task without asking a
human to approve each pull request.

Autonomy is always relative to a declared subject, active standing grant,
closed capability catalog, risk ceiling, resource budget, and protected
publication boundary. It is not general permission for an LLM to execute tools.

The canonical interchange form is JSON conforming to
`wellmanifest.autonomy/manifest/v1`. Implementations MAY project the same
semantics into YAML, Protobuf, CQRS messages, AQL/EQL, or URI Process contracts,
but a projection MUST preserve every authority restriction and immutable
binding.

## 2. Ownership and adoption

`wellmanifest/autonomy` owns the standard, schema, conformance rules, and
profiles. It does not own an agent runtime. Subactor, Semcod, GitHub Apps,
CI systems, and other products implement the standard in their own
repositories.

Adoption is valid only when the target repository pins:

1. an immutable revision of this standard;
2. one immutable runtime profile and its SHA-256 digest;
3. a repository policy digest that the pull request cannot modify to approve
   itself; and
4. an active standing grant issued by an authority external to the agent fleet.

The protected controller MUST resolve policy and profile data independently of
the candidate pull-request checkout. Repository-authored copies are evidence,
not authority.

## 3. Standing autonomy grant

The `grant` object is a standing delegation. When all its conditions hold,
`noPerPullRequestHumanApproval=true` means that no new human consent is required
for each qualifying pull request. `allowAutomatedMerge=true` permits a protected
publisher to enable or perform merge after all required gates pass.

The grant MUST bind:

- its issuer and stable grant URI;
- one or more exact repository identifiers and target branches;
- allowlisted and denied paths;
- a closed action set;
- a maximum autonomous risk tier;
- issuance, activation, review, and expiry times;
- the expected value of a kill switch; and
- explicit prohibitions on self-extension and self-renewal.

An agent MUST NOT issue, extend, renew, replace, reinterpret, or disable its own
grant. A new repository, branch, action, risk tier, path, credential class, or
publication identity is an authority expansion and MUST fail closed until an
external issuer provides a new grant. Revocation takes effect before the next
mutation and invalidates any unused lease.

Grant activity is evaluated at least before edit, before push, before approval,
and immediately before merge. A valid grant at planning time does not authorize
an operation after expiry or revocation.

## 4. Roles and separation of duties

A conforming fleet declares six roles:

| Role | Purpose | Mutation ceiling |
|---|---|---|
| `observer` | Collect runtime, repository, LSP, and intent evidence | Read-only |
| `planner` | Select a runnable task and compile a bounded plan | Proposal only |
| `implementer` | Edit an isolated branch/worktree and produce a candidate | Candidate branch only |
| `validator` | Reproduce checks and issue a bound verdict | Attestation/review only |
| `publisher` | Freeze, approve through a trusted App, merge, and read back | Protected publication only |
| `auditor` | Preserve secret-free receipts and detect drift | Append-only audit |

The implementer, validator, and publisher MUST use different principals,
credentials, workspaces, and approval identities. The validator MUST evaluate
the exact candidate head from an isolated checkout. Different prompts, model
names, sessions, or agent labels alone do not establish independence.

An observer or digital twin MUST NOT mutate. A planner or LLM MUST NOT invent a
URI, transport, secret reference, capability, or execution policy. An
implementer MUST NOT approve or merge. A validator MUST NOT edit the candidate.
A publisher MUST NOT weaken policy or manufacture validator evidence.

The protected Validator App MAY provide the trusted approval that replaces a
human review. Its evidence MUST bind repository, pull request, current head,
current base, ticket, grant, profile digest, and actor. A generic bot review or
Markdown note is not trusted approval.

## 5. Evidence and epistemic boundary

Observations, facts, inferences, proposals, executions, and verifications are
different classes of evidence and MUST remain distinguishable.

- LSP, AST, test, Git, runtime probe, and contract outputs are observations.
- LLM summaries and plans are claims or proposals until independently checked.
- A green test suite is not evidence that an unexercised runtime path works.
- `skipped`, `waiting_external`, `unknown`, and `no_candidate` are not success.
- Diagnosis never grants repair authority.
- A digital twin observes and aggregates; it never grants authority.

Evidence MUST carry producer identity, subject revision, configuration or
profile digest, observation time, completeness, and a correlation identifier.
Secret values MUST be redacted before evidence reaches an LLM or durable audit
store.

## 6. Risk policy

Risk is classified as `low`, `moderate`, `high`, or `critical`. The standing
grant declares an autonomous ceiling. Work above that ceiling MUST be routed to
human review or another explicitly named external authority.

The initial standard requires these excluded effects in every grant:

- secret acquisition, rotation, or disclosure;
- destructive infrastructure or data operations;
- billing and financial commitment;
- legal or regulatory acceptance;
- identity and access-policy changes;
- security-boundary weakening;
- governance or authority-policy changes;
- mutation, renewal, or extension of the autonomy grant;
- force push or history rewrite;
- direct push to the default branch; and
- publication through an untrusted dependency or package identity.

An adopter MAY exclude more effects but MUST NOT remove these exclusions while
claiming conformance to version 0.1. A repository MAY define a separate,
externally issued high-risk profile; that profile is not the default autonomous
code-development grant.

## 7. Resource and change budgets

The manifest MUST bound files, components, public interfaces, runtime
dependencies, active time, monetary cost, retries, consecutive cycles,
concurrency, cooldown, and lease duration. A controller MUST measure actual
usage and stop before exceeding a budget. Budget exhaustion creates one
deduplicated escalation receipt; it MUST NOT create an unbounded retry loop.

One controller cycle performs at most one external mutation. Parallel tasks MAY
run only when their write scopes do not overlap and the declared concurrency
budget permits it. A lease MUST expire and MUST NOT be silently renewed by its
holder.

## 8. Runnable work and continuation

Autonomous continuation uses a durable backlog, not free-form model initiative.
The queue MUST expose a deterministic `runnable` decision based on status,
dependencies, scope ownership, freshness, deduplication, conflict, active
lease, and human-boundary labels.

The initial selection policy is `runnable-priority-dag`: select the highest
priority fresh task whose dependencies are terminal-success, whose scope is
available, and which carries no human or autonomy-frontier label. Bugs MAY sort
ahead of features within the same priority. The selected task and plan MUST be
bound by stable identifiers and digests before editing.

After a verified merge or release, `nextTaskWithoutHumanApproval=true` allows
the controller to select the next runnable item under the same active grant.
The loop stops on revocation, expiry, kill switch, no candidate, out-of-scope
work, failed independent validation, exhausted budget, repeated failure,
ambiguous evidence, or unavailable protected authority. It MUST record the stop
condition instead of reporting completion.

## 9. Normative lifecycle

The ordered states are:

```text
observe → evidence → plan → grant-check → isolated-edit →
deterministic-validate → independent-validate → publish-pr →
exact-head-gate → auto-merge → post-merge-verify → continue
```

Required behavior:

1. **Observe** the target and current base without mutation.
2. **Evidence** materializes provenance-bound repository, runtime, contract,
   LSP, and intent facts.
3. **Plan** selects one runnable task and compiles only known capabilities.
4. **Grant check** validates current scope, risk, lease, kill switch, and
   budgets.
5. **Isolated edit** starts from the exact current base in a dedicated branch
   or worktree without live secrets.
6. **Deterministic validation** runs trusted, versioned checks.
7. **Independent validation** replays the candidate under a separate principal
   and issues a verdict bound to the exact head and protected profile digest.
8. **Publish PR** creates a same-repository pull request with one ticket and
   correlation ID.
9. **Exact-head gate** freezes the candidate, rechecks current base, required
   checks, grant activity, and validator evidence.
10. **Auto-merge** uses only the protected publisher identity. Direct default
    branch push is forbidden.
11. **Post-merge verify** reads back the default branch, deployment or release
    result as declared by the task.
12. **Continue** closes the task only from verified receipts and selects the
    next runnable task while the grant remains active.

Any change to the candidate head invalidates prior validation and approval.
Any change to the base requires re-evaluation against that base. A failed
read-back opens a deduplicated reaction task or rolls back through an approved
capability; it does not claim success.

## 10. Publication requirements

Automated merge without per-PR human approval is conforming only when all of the
following are true:

- the pull request originates in the same repository and targets the declared
  default branch;
- exactly one active task and correlation ID are present;
- the candidate is within grant scope and at or below the risk ceiling;
- all required deterministic checks pass for the exact head;
- an independent trusted Validator App or signature-verified validator
  attestation approves that same head under the protected profile digest;
- the base is current and mergeable immediately before merge;
- no unresolved critical or security finding exists;
- the standing grant is active and the kill switch allows mutation;
- post-merge read-back and branch cleanup are enabled.

The publisher MUST perform a read-after-write check. A superseded pull request
MAY be closed without merge only after proving that its declared successor from
the same repository was merged. Each controller cycle performs at most one
mutation.

## 11. Receipts and audit

Required receipt classes are `observation`, `plan`, `grant-check`, `change`,
`deterministic-validation`, `independent-validation`, `publication`, and
`read-back`. Receipts MUST share a correlation ID and contain immutable subject
bindings. They MUST be secret-free, append-only, retained for the declared
period, and distinguish attempted, skipped, failed, rolled-back, and completed
effects.

An approval receipt is authoritative only when produced or verified outside the
candidate checkout. An agent-written receipt is evidence of a claim, not proof
of external state.

## 12. Recovery and revocation

The deployment MUST expose a protected kill switch whose disabled value causes
all mutation paths to fail closed while observation remains available. A
revoked or expired grant stops new mutation and merge, releases leases, and
preserves evidence. Unknown dirty workspaces, unique commits, or unmerged
branches MUST be preserved for audit; cleanup may remove only verified
disposable worktrees and branches according to repository lifecycle policy.

Rollback is a separate allowlisted capability with its own preconditions,
verification, and receipt. It MUST NOT use force push or history rewrite under
the default profile.

## 13. Conformance

A manifest conforms when it:

1. validates against `schemas/autonomy-manifest.schema.json`;
2. passes `wellmanifest.autonomy-check` with no finding;
3. pins a valid protected integration profile digest;
4. contains all mandatory exclusions, roles, lifecycle states, gates,
   bindings, receipts, and stop conditions;
5. demonstrates at least one valid routine-code example and invalid examples
   for self-approval and grant expiry; and
6. passes the target repository's own governance and deterministic tests.

The Subactor/Semcod profile is informative about concrete product ownership but
normative when an adopter selects its exact ID, version, and digest.
