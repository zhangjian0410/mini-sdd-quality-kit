# Candidate-bound Independent Review

At `REVIEW_READY`, recheck the actual candidate, Spec revision/digest, accepted
scope, base, repository rules and available Verification Evidence. Use the
canonical sibling `review-diff/SKILL.md` and its report contract for both Spec
Compliance and Code Quality. Do not create another review core or invoke an
upstream review workflow. Run no tests or corrective tools on the review side.

The Full Task coordinator writes necessary task records. The separate reviewer
only inspects inputs and returns its actual report in conversation. An actor's
name, fresh-session assertion, instruction to remain read-only, or reviewer
self-declaration alone establishes no enforced controls. Inspect the actual
host context launch, effective sandbox/tool policy, delivered inputs and before/
after repository, Git and task observations. Native roles may inherit a
workspace-write sandbox; disclose that limitation and retain `PENDING` when
read-only enforcement cannot be established. Never test controls by writing into
the reviewed repository. Existing authorized observer checks run outside review.

## Pending launch packet

Use the confirmed Python 3.11+ interpreter and the public task helper:

```sh
<python> -B <mini-sdd>/scripts/task.py --root <worktree> review-packet \
  --task <id> --implementation-context <actual-context-reference> \
  --rule AGENTS.md --limitation '<actual unresolved control or evidence gap>'
```

Supply all relevant repository rules using repeated `--rule`; disclose missing
or unavailable rules with `--limitation`. The packet contains the worktree/task,
actual candidate layers and base, authoritative Spec content/revision/digest,
accepted scope, rules, Verification Evidence references, canonical review entry
and report requirements, read-only expectations and expected result identities.
Existing file evidence and assessment references carry exact byte digests; a
changed/missing/replaced file refuses import until inputs are reviewed again.
References that are not readable canonical files carry explicit `UNAVAILABLE`
limitations; strings alone are not observed verification. Evidence references
must remain accessible to the separate session. The packet
is reusable in another session with access to that worktree, Skill bundle and
evidence. It is not a self-contained portable code archive. No reviewer has run
merely because the helper produced a packet. Review stays `PENDING` and no
numbered attempt is created. Recheck inputs immediately before and after review.

## Preserve actual reports

After a real attempt, the coordinator submits the actual report as JSON on stdin
to `code-review --task <id>`. The envelope has:

- `version: 1`, `candidate_id`, `spec_sha256`, `base`, `packet_sha256`.
- Actual `reviewer` and `review_context` references, `coverage` as inspected
  candidate paths, `axes` with `Spec Compliance` and `Code Quality` conclusions,
  `limitations`, `verification: NOT_RUN`, and the actual readable `report` body.
- `findings`: each has `id`, `axis`, `severity`, `file`, positive integer `line`,
  `expected`, `actual`, `evidence`, `impact`, `remedy`, `verification: NOT_RUN`.
  Preserve original claims; an empty findings list does not prove correctness.
- `evidence`: inspected observer references `{source, path, sha256}` with source
  `manual` or `host-captured`. Paths are absolute canonical ordinary files.

Each observer receipt binds `candidate_id`, `packet_sha256`,
`implementation_context`, `review_context`, actual distinct `observer`, and
`provenance` matching the reference source. It includes inspectable nonempty
`separate_context`, `input_identity`, `no_writes` observations and
`read_only_controls: {enforcement, observation}`. Supported enforcement labels are
`sandbox-read-only`, `tool-policy-read-only`, `mount-read-only`; choose one only
when its actual operation is established. Link the underlying capture/config,
events, command audit and snapshots within these observations. Keep private raw
host data outside repositories and use accurate sanitized receipts when needed.
Manually supplied evidence is acceptable when independently inspectable; oral
confirmation and self-declaration are insufficient. Missing/unsupported controls,
stale evidence or unknown source leaves the actual report `UNVERIFIED/PENDING`.
A known shared implementation context is `SELF_CHECK/PENDING`.

The helper validates relationships, digests and required report fields. It cannot
prove receipt authenticity, truthful observations, meaningful coverage, adequate
controls or finding correctness. Before submitting, the coordinator must inspect
those matters and classify gaps honestly. Synthetic helper fixtures establish
validation behavior only; they never establish actual Independent Review.

Each actual attempt publishes the next exclusive `reviews/code-NN.md` and updates
`latest_review`; empty templates are refused and older reports remain intact.
Wrong candidate/Spec/base/packet inputs are refused. Valid independently observed
reports record `INDEPENDENT`, `REVIEWED`, and explicit evidence source; they do not
assert behavior checks passed, findings resolved or Completion. Partial coverage
and every substantive limitation remain in the report for later assessment.
Independent Review availability is not a host-wide acceptance claim.
