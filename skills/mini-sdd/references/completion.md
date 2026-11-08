# Repair, re-review and local Completion

Before relying on a checkpoint, run [resume](resume.md) and inspect the actual
Spec, consent, candidate, Verification Evidence, review and observer evidence.
Changed or malformed inputs stop reliance on the old approval. Preserve original
reports, manifests and evidence; identify current inputs and obtain affected
verification/re-review. Do not edit source first and then call that old report
current. Resume is a structural check; its status never substitutes for judgment.

Confirm each actual finding against the agreed AC, source and evidence. A violation
of applicable AC or a material behavioral, security or reliability defect
introduced by this task is a Blocking Finding. Keep it unresolved until an actual
repair and valid re-review establish its closure. A severity label alone does not
establish correctness. Disclose relevant non-blocking suggestions and clearly
unrelated pre-existing problems; do not turn them into sweeping cleanup.

For an ordinary repair within current consent, use the confirmed interpreter:

```text
<python> -B <skill>/scripts/task.py --root <root> repair --task <id> --reason <confirmed-in-scope-finding-and-remedy>
```

This first reuses resume/drift checks, then enters `IMPLEMENTING` under the same
consent and fixed base. It clears current candidate, verification and review
approval references; old files remain immutable history. Repair accepted code,
repeat affected proportional verification, `checkpoint` the latest actual inputs,
prepare current review inputs and obtain a new actual Independent `review-diff`.
An old report cannot approve a changed candidate. Actual attempts keep increasing
`code-NN.md` numbers. A repeated checkpoint also clears current review approval.

A material scope change needs a revised Mini Spec and renewed consent. After
validating the existing checkpoint, enter repair only to invalidate old approval,
then `revise` the Spec before dependent edits and `confirm` its new digest using
the actual user approval. Explain the material change. Do not relabel old consent
or call a new feature a repair. Completed tasks use the same validation before
reopening; no automatic Git or Issue action is part of this operation.

## Assess Completion

The coordinator inspects actual implementation against the authoritative AC,
proportional verification results and sufficiency, latest applicable review axes,
review coverage, limitations and independently inspectable observer evidence.
Require all of these for the latest candidate, with no unresolved Blocking
Findings. Nonempty axis strings, a reviewer PASS, an empty findings list, a
synthetic fixture, a state bit or a receipt schema alone cannot establish this.
Review-side `NOT_RUN` remains accurate: the reviewer inspects existing results;
the implementation coordinator owns actual verification and its adequacy.

The optional record helper can bind an existing ordinary canonical JSON
coordinator-assessment file with `complete --assessment-reference <absolute-path>`.
Keep that assessment in an already authorized evidence location; do not add
another required product document or per-AC testing platform. Its shape is:

- `version: 1`, current `candidate_id`, `spec_sha256` and actual `consent_reference`.
- `reviews`: map every actual `reviews/code-NN.md` path to its SHA-256 digest.
- `implementation`, `verification`, `review_authenticity`: the coordinator's
  inspected reasons addressing all agreed implementation/verification conditions
  and actual review provenance. Identify observed results and remaining limits.
- `axes`: `Spec Compliance` and `Code Quality`, each with `status: SATISFIED` and
  a grounded `rationale`. Full Task has an authoritative Spec, so both apply.
- `findings`: every historical finding, keyed by `review` path and `id`, with
  `disposition` and inspected `rationale`. Use `REPAIRED` only after a different
  candidate and later valid Independent Review; use `NON_BLOCKING` or
  `PRE_EXISTING` only with evidence supporting that judgment. An unresolved or
  unassessed Blocking Finding prevents Completion.
- `disclosed`: remaining non-blocking issues, exclusions and limitations. Preserve
  every latest review limitation verbatim and explain its practical effect. A
  necessary unresolved verification/review gap cannot be dismissed here.

The helper checks identities, coverage, evidence relationships, historical report
bytes and explicit judgments. It cannot authenticate an observer or decide the
truth, finding classification or sufficiency of those judgments. The coordinator
must do that work before invoking it. State stores only assessment reference and
digests, avoiding a duplicate AC/findings ledger. The helper never runs tests,
launches review, closes an Issue or publishes Git changes.

When any necessary check is unrun, review is pending/unverifiable, a Blocking
Finding remains, or inputs drift, hand off the actual candidate, unresolved
items, accessible evidence/launch packet and next actions. Keep affected behavior
`UNKNOWN`/`NOT_RUN` and task incomplete. On Completion, report the latest candidate,
actual evidence and independent review, disclosed remaining issues and local
`COMPLETE` status. This grants no Issue closure, commit, push, PR, merge, release
or business acceptance. Follow the team's separately authorized delivery process.

A fresh-session `resume` revalidates completed inputs and the assessment digest.
An unchanged inspected assessment is `ATTRIBUTABLE`, not a new automatic PASS.
Candidate, Spec, report, rules, verification, provenance or assessment drift
cannot retain approval. A historical `COMPLETE` without an assessment binding
stays `UNKNOWN` for inspection. No evidence is overwritten or cleaned up.
