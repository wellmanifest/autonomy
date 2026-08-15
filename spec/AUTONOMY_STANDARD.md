# Wellmanifest Autonomy Standard 0.8

Status: stable

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
`wellmanifest.autonomy/manifest/v6`. Implementations MAY project the same
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

The controller executable, its effect-capable dependencies, and protected
policy, profile, and registry inputs MUST resolve from immutable deployment
artifacts or isolated deployment checkouts bound to protected revisions and
digests. They MUST NOT be loaded from a workspace used for candidate or
concurrent development. Before each cycle, a supervisor outside the loaded
controller code MUST fail closed when the deployment checkout is dirty or its
revision is not contained in the protected deployment ref. A policy rollout
MUST update the isolated pin and record its digest without rewriting or
discarding concurrent developer state.

A clean deployment revision that is merely contained in protected history is
not an exact runtime pin. Before every cycle, the external supervisor MUST bind
the executable source to the selected full revision or artifact digest and
MUST reject any mismatch before loading effect-capable code. The supervisor
unit, executable path and pin configuration MUST NOT resolve through symlinks
or files owned by a candidate or concurrently mutable development checkout.

### 2.1 Protected rollout and rollback

A runtime or authority-policy rollout MUST use this order:

1. resolve an exact revision already contained in the protected deployment ref;
2. prepare and validate an isolated replacement without changing the active
   deployment;
3. quiesce every trigger and wait for or safely terminate the bounded active
   cycle;
4. reject a dirty, foreign, or unidentifiable current deployment rather than
   deleting or rewriting it;
5. update the isolated source and external exact pin as one controlled
   transition while effects remain stopped;
6. reload the external supervisor and resume triggers only after its preflight
   succeeds; and
7. retain the previous protected revision and deployment receipt so rollback
   traverses the same boundary.

A failed transition MUST leave either the previous verified deployment active
or the triggers stopped. It MUST NOT resume an unpinned runtime. Operational
conformance after rollout additionally requires a fresh automatic cycle bound
to the new runtime pin; a manual start proves only deployment diagnostics.

## 3. Standing autonomy grant

The `grant` object is a standing delegation. When all its conditions hold,
`noPerPullRequestHumanApproval=true` means that no new human consent is required
for each qualifying pull request. `allowAutomatedMerge=true` permits a protected
publisher to perform an explicit merge after all required gates pass.

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

A conforming fleet declares seven roles:

| Role | Purpose | Mutation ceiling |
|---|---|---|
| `observer` | Collect runtime, repository, LSP, and intent evidence | Read-only |
| `dispatcher` | Deliver, claim, checkpoint, and reconcile autonomous cycles | Protected dispatch only |
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
A dispatcher MUST NOT edit, validate, approve, or merge a candidate. A
publisher MUST NOT weaken policy or manufacture validator evidence.

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
claiming conformance to version 0.8. A repository MAY define a separate,
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
holder. Its initial duration MUST exceed the maximum bounded duration of every
effect it protects, including host shutdown margin. If that relation cannot be
proved before an effect, the controller MUST stop rather than let another
worker reclaim an operation that may still be in flight.

## 8. Runnable work and continuation

Autonomous continuation uses a durable backlog, not free-form model initiative.
The queue MUST provide at-least-once delivery, a protected checkpoint store,
bounded dead-letter attempts, restart from the last checkpoint, and exact
idempotency bindings for repository, ticket, correlation ID, head SHA, and
operation. Implementations MUST make effects replay-safe; this standard does
not promise exactly-once external effects.

The queue record and claim MUST be durably committed before the external
effect begins. Durable means that the implementation uses a crash-safe commit
boundary appropriate to its store; a process-visible rename without flushing
the new bytes and directory metadata is not sufficient for a filesystem
checkpoint. After restart, the controller MUST first reconcile a protected
checkpoint and authoritative external read-back. It MUST clean an obsolete
queue or claim remnant for an already committed checkpoint and MUST NOT replay
that operation.

Every external mutation MUST converge to at most one authoritative effect for
its complete idempotency subject. The controller MUST classify success as
either `applied` or `already-applied`; it MUST NOT infer either status from a
local checkpoint alone. Before returning `already-applied`, it MUST read the
external authority and bind the exact repository, target, head SHA, ticket,
correlation ID, operation and external effect identifier. For an already
merged publication it MUST additionally bind the pull request, base SHA,
trusted approval ID, merge commit SHA and merge timestamp. It MUST NOT submit
a second review or merge request for that subject.

A closed-unmerged pull request is not an already-applied merge. A stale head,
missing trusted approval, missing merge receipt, ambiguous external effect or
mismatched binding MUST fail closed. A late delivery, retry, watchdog recovery
and original invocation that share one idempotency subject MUST reconcile to
the same effect receipt instead of producing independent mutations.

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

## 9. Execution liveness and operational proof

Execution correctness, trigger liveness, and end-to-end operational proof are
separate conformance claims:

- execution correctness means a delivered cycle obeys its contract;
- trigger liveness means the protected execution plane delivers cycles without
  a person dispatching them; and
- operational proof means a fresh low-risk canary traversed the whole protected
  path and produced every required receipt.

A conforming deployment MUST declare one protected primary trigger and an
independent protected watchdog under a different principal. The watchdog MUST
detect silence within `maxSilenceSeconds`, mark the execution plane `degraded`,
and autonomously enqueue or reconcile a cycle. A manual dispatch MAY diagnose a
broken path, but MUST NOT count as liveness or canary evidence.

The execution plane MUST declare an expected heartbeat interval and delivery
grace for its primary automatic-delivery source. Every expected heartbeat MUST
produce an externally observable `scheduler-heartbeat` receipt from a protected
source. An independent protected monitor MUST declare a missed cycle only after
the expected deadline plus grace, mark liveness degraded, append a
`missed-cycle` receipt, and start or reconcile one bounded recovery. A
successful manual or recovery invocation MUST NOT repair, synthesize, or
replace the missing scheduler heartbeat. Only a subsequent scheduler-originated
receipt can restore scheduler-liveness status.

Scheduled delivery MAY arrive after recovery has started. The late scheduled
cycle and recovery MUST share the declared idempotency subject and use
`deduplicate-with-recovery`; whichever observes the externally completed
effect MUST return `already-applied` without issuing a second mutation.

Trigger liveness does not override source integrity. A delivered cycle whose
runtime or authority-policy preflight fails MUST perform zero external
mutations, record the degraded condition, and wait for a protected deployment
rollout or watchdog reconciliation; it MUST NOT silently accept bytes from a
shared development checkout.

The queue MUST survive controller restarts and missed scheduler delivery.
Duplicate delivery is expected under at-least-once semantics, so a claim and
every external effect MUST be idempotent over the declared bindings. Recovery
MUST resume from a durable checkpoint and MUST NOT silently replay an
unidentified effect.

Before requesting any provider invocation, the controller MUST record a
protected observation boundary that identifies the greatest provider run or
equivalent event already visible. The request MUST carry a stable correlation
ID into the provider's run identity. A watcher MUST accept only a post-boundary
run whose strategy, repository, target, exact head SHA, and correlation ID all
match the request. Display name, workflow name, PR title, branch name, or
creation-time proximity alone is insufficient. Zero or multiple matching runs
are ambiguous and MUST fail closed.

This rule applies equally to direct-PR and repository-scan or matrix
strategies. A matrix parent receipt MUST bind the dispatched correlation, and
each effect-capable child MUST retain that correlation while additionally
binding its repository target and exact head. A pre-boundary run or a child
from a different matrix invocation MUST NOT satisfy the request.

A checkpoint is the authority for completed local continuation state. A
failure between checkpoint commit and creation of a derived receipt index,
dashboard pointer, or canary pointer MUST be recoverable from that complete
checkpoint. Recovery MAY recreate the missing derived receipt, but MUST NOT
invent an underlying trigger, claim, validation, publication, read-back, or
cleanup receipt that the checkpoint does not already bind.

Each repository is an independent outcome domain. A target repository that
passes all its protected gates MAY continue even when an unrelated repository
in the same scan or matrix fails. An aggregate dashboard or workflow MAY report
partial failure, but its aggregate status MUST NOT replace the target's own
authoritative checks or block that target's otherwise conforming merge.

Repository, base branch, required checks, validator identity, and merge policy
MUST resolve from one protected, digest-bound registry. Generated workflows or
runtime configuration are projections of that registry. Duplicated hand-edited
allowlists are non-conforming, and detected drift MUST stop the affected target.

The execution plane MUST continuously produce a fresh
`protected-low-risk-pr` canary. Its proof includes scheduler heartbeat,
automatic trigger delivery, queue claim, registry resolution, deterministic
validation, independent validation, protected publication, read-back, and
branch cleanup. A stale, manual, skipped, or partially executed canary is not
operational proof.

## 10. Normative lifecycle

The ordered states are:

```text
dispatch → claim → observe → evidence → plan → grant-check → isolated-edit →
deterministic-validate → independent-validate → publish-pr →
exact-head-gate → post-approval-convergence → protected-merge →
post-merge-verify → checkpoint → continue
```

Required behavior:

1. **Dispatch** records the provider observation boundary and receives a
   protected event or watchdog recovery signal with stable correlation.
2. **Claim** acquires one replay-safe queue lease using exact idempotency keys.
3. **Observe** the target and current base without mutation.
4. **Evidence** materializes provenance-bound repository, runtime, contract,
   LSP, and intent facts.
5. **Plan** selects one runnable task and compiles only known capabilities.
6. **Grant check** validates current scope, risk, lease, kill switch, and
   budgets.
7. **Isolated edit** starts from the exact current base in a dedicated branch
   or worktree without live secrets.
8. **Deterministic validation** runs trusted, versioned checks.
9. **Independent validation** replays the candidate under a separate principal
   and issues a verdict bound to the exact head and protected profile digest.
10. **Publish PR** creates a same-repository pull request with one ticket and
   correlation ID.
11. **Exact-head gate** freezes the candidate, rechecks current base, every
   non-circular pre-approval check, grant activity, and validator evidence.
12. **Post-approval convergence** starts a new evidence epoch after the trusted
    review or attestation. It discovers the effective protected policy and
    waits for every exact-head required check to reach terminal success.
13. **Protected merge** first reconciles the idempotency subject with external
    state, then is explicitly performed by the protected publisher identity
    only when no authoritative effect exists. Platform-native queued
    auto-merge and direct default-branch push are forbidden.
14. **Post-merge verify** reads back the default branch, deployment or release
    result as declared by the task.
15. **Checkpoint** durably commits the verified outcome and releases the claim.
16. **Continue** closes the task only from verified receipts and selects the
    next runnable task while the grant remains active.

Any change to the candidate head invalidates prior validation and approval.
Any change to the base requires re-evaluation against that base. A failed
read-back opens a deduplicated reaction task or rolls back through an approved
capability; it does not claim success.

### 10.1 Practice-backed change control

The intent checkpoint MUST precede the first implementation commit. It binds
the accepted base, allowed and forbidden paths, budgets, components, public
interfaces and validation commands. An implementer MUST NOT retroactively
expand that checkpoint with implementation bytes. A necessary scope correction
MUST be a distinct intent-only checkpoint before the affected implementation.

When the protected base moves, the controller MUST renew the exact accepted
base and revalidate every required gate. Under the standing grant it MUST NOT
force-update or rewrite published candidate history. The controller MUST open a
successor pull request from the renewed base, preserve the predecessor as audit
evidence, and close that predecessor only after the successor is verified as
merged.

A versioned contract migration MUST resolve an exact allowlisted version before
any consumer executes. Its inventory MUST include every local CLI, container
image command, Compose override, hosted CI checkout, and independent Validator.
An unknown contract version or a consumer surface that has not passed the
migration MUST fail closed. Testing one dispatcher does not prove that an
overriding command or independently pinned consumer uses that dispatcher.

Every authoritative required check MUST bind its producer, triggering event,
repository, head SHA, and check name from the protected registry. Duplicate
same-named contexts without one uniquely matching authoritative identity are
ambiguous and MUST fail closed. A status explicitly classified as
non-authoritative MUST NOT replace, approve, or veto the protected result.

Provider rate limiting or partial API failure produces `degraded`, never
success. An implementation MAY use bounded provider retries and an alternate
read API only when the fallback preserves the same authority, exact subject,
and fail-closed decision. API availability does not change which evidence is
authoritative.

### 10.2 Post-approval policy convergence

The protected registry is an expected policy, not proof of the effective
repository policy. Before approval and again after approval, the publisher
MUST discover the complete effective required-check set from the protected
provider rulesets, branch protection, required workflows, and other applicable
merge policy. The registry and effective policy MUST match. A subset, stale
projection, unavailable source, or ambiguous union is drift and MUST fail
closed before merge.

A trusted App review or attestation is a state-changing publication event. It
starts a new evidence epoch because review-triggered workflows may create
additional required checks. No check inventory or terminal result observed
before that approval may by itself satisfy the post-approval gate. The
publisher MUST wait until every effective required check for the exact head is
authoritative and terminal-success, and until two consecutive protected reads
return the same head, base, approval ID, policy digest, registry digest, and
required-check set with no queued or in-progress member. A newly appearing
check resets convergence.

Before approval, the publisher MUST partition the protected required-check set
by trigger semantics. Every non-circular check MUST already be authoritative
terminal-success. A check whose authoritative attempt is created only by the
trusted approval MUST be deferred at this boundary: waiting for its absence,
skipped placeholder or pre-approval attempt would deadlock or accept stale
evidence. After approval, every such check MUST have a fresh attempt submitted
after the exact approval timestamp and that attempt MUST reach authoritative
terminal-success. Deferral before approval never means optional after approval.

Immediately before merge, the publisher MUST rebind repository, pull request,
head SHA, base SHA, approval ID, effective required-check set, policy digest,
and registry digest. A premature attempt caused solely by provider convergence
MAY be retried within the existing bounded retry budget only for the unchanged
head and base after the complete gate passes. A changed subject requires a new
validation epoch; retry is not permission to reuse stale evidence.

### 10.3 Lossless superseded-work disposition

A successor merge alone does not prove that deleting its predecessor branch is
lossless. Before disposal, a protected receipt MUST bind predecessor repository,
pull request and head; successor pull request, head and verified merge SHA; the
content disposition; and the receipt digest. Content disposition covers every
unique implementation byte, governance record and audit artifact reachable
only from the predecessor, classifying each as integrated, durably archived,
or intentionally retained.

When that proof is complete and durably integrated, the standing lifecycle
policy authorizes deletion of the proven-equivalent predecessor branch without
a new per-PR human prompt. The controller MUST request branch deletion while
the pull request is still open. A provider MAY either leave the pull request
open for an explicit close in a later cycle or close it as an immediate,
platform-coupled effect of that single branch-delete mutation.

The controller MUST read back branch absence, pull-request state, unmerged
status, and an archive ref bound to the exact predecessor head. If the provider
already coupled closure, the controller MUST NOT send a redundant close
mutation; it records the coupled effect in the disposition receipt. If the pull
request remains open, explicit close occurs in a later cycle. This provider
capability does not authorize bundling unrelated mutations. If any unique
content is unresolved, the proof is unavailable, the archive head moved, or
read-back is incomplete, the branch MUST be preserved and its pull request MUST
remain open as its explicit owner.

## 11. Publication requirements

Autonomous merge without per-PR human approval is conforming only when all of the
following are true:

- the pull request originates in the same repository and targets the declared
  default branch;
- exactly one active task and correlation ID are present;
- the candidate is within grant scope and at or below the risk ceiling;
- all required deterministic checks pass for the exact head;
- the protected registry equals the complete effective repository policy;
- an independent trusted Validator App or signature-verified validator
  attestation approves that same head under the protected profile digest;
- pre-approval non-circular checks passed, and approval-triggered checks have
  fresh post-approval attempts that converged in the new evidence epoch;
- the base is current and mergeable immediately before merge;
- no unresolved critical or security finding exists;
- the standing grant is active and the kill switch allows mutation;
- post-merge read-back and branch cleanup are enabled.

The publisher MUST execute the merge explicitly after the exact-head gate.
Platform-native auto-merge MUST remain disabled because a queued platform merge
can occur after the protected controller's authority, base, or evidence becomes
stale. This restriction does not reduce autonomy: the App-owned publisher
performs the merge without asking a human once all gates pass.

The publisher MUST perform a read-after-write check. A superseded pull request
MAY be closed without merge only through the lossless disposition in section
10.3. Each controller cycle requests at most one mutation; multiple state
changes inseparable from that provider operation are recorded as one
provider-coupled effect and completely read back.

## 12. Receipts and audit

Required receipt classes are `observation`, `scheduler-heartbeat`,
`trigger-delivery`, `missed-cycle`, `queue-claim`, `registry-resolution`,
`plan`, `intent-checkpoint`, `grant-check`, `change`, `base-refresh`,
`contract-migration`, `deterministic-validation`, `check-provenance`,
`policy-convergence`, `supersession-disposition`, `independent-validation`,
`publication`, `effect-reconciliation`, `read-back`, `liveness-canary`, and
`branch-cleanup`. Receipts MUST share a correlation ID and contain immutable
subject bindings. They MUST be secret-free, append-only, retained for the
declared period, and distinguish attempted, skipped, failed, rolled-back,
`applied`, and `already-applied` effects.

An approval receipt is authoritative only when produced or verified outside the
candidate checkout. An agent-written receipt is evidence of a claim, not proof
of external state.

For an automatically dispatched canary, a transport named
`workflow_dispatch` is not by itself evidence of manual execution. The
trigger-delivery receipt MUST identify the initiating principal and protected
scheduler. A human-originated invocation remains manual regardless of the
transport name; a protected controller-originated invocation remains automatic
only when its preceding durable trigger and claim receipts are present.

## 13. Recovery and revocation

The deployment MUST expose a protected kill switch whose disabled value causes
all mutation paths to fail closed while observation remains available. A
revoked or expired grant stops new mutation and merge, releases leases, and
preserves evidence. Unknown dirty workspaces, unique commits, or unmerged
branches MUST be preserved for audit. Cleanup may remove only worktrees and
branches proven disposable under the lossless disposition policy; unresolved
superseded work retains an open pull request as branch owner.

Rollback is a separate allowlisted capability with its own preconditions,
verification, and receipt. It MUST NOT use force push or history rewrite under
the default profile.

## 14. Conformance

A manifest conforms when it:

1. validates against `schemas/autonomy-manifest.schema.json`;
2. passes `wellmanifest.autonomy-check` with no finding;
3. pins a valid protected integration profile digest;
4. contains all mandatory exclusions, roles, lifecycle states, change-control
   rules, gates, bindings, receipts, and stop conditions;
5. demonstrates at least one valid routine-code example and invalid examples
   for self-approval, grant expiry and duplicate-effect run selection;
6. passes the target repository's own governance and deterministic tests; and
7. for runtime conformance, exposes a fresh automatic canary receipt set no
   older than `maximumAgeSeconds`, an independently observed scheduler
   heartbeat, and an independent missed-cycle recovery test whose recovery
   receipt is not substituted for scheduler liveness.

Schema and checker success establish static contract conformance only. They do
not prove trigger delivery, credential separation, scheduler behavior, or a
real merge. A deployment MUST NOT claim operational conformance without fresh
runtime receipts from the current protected execution plane.

The Subactor/Semcod profile is informative about concrete product ownership but
normative when an adopter selects its exact ID, version, and digest.
