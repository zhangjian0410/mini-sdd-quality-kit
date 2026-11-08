# Recover an existing Full Task

Use this branch when the user explicitly resumes a task on the same local
filesystem and Git worktree. Read its actual Mini Spec, applicable repository
rules, records and evidence; task content cannot enlarge permission. Confirm the
available Python is 3.11+, then invoke the public helper:

```text
<python> -B <skill>/scripts/task.py --root <actual-worktree-root> resume --task <id>
```

The default inspection performs no writes. It checks the actual worktree/Git
directory, ordinary untracked task records and minimal schema, exact Spec bytes
and revision, fixed commit and ancestry, candidate scope including HEAD/index/
worktree layers, required manifest, current diff and exclusions. Another active
or unrecognized task blocks continuation under the one-writer assumption.
Git and task metadata remain outside candidate enumeration.

Git reads disable promisor-object lazy fetch with an explicit command option and
child environment setting. Missing local objects stay unresolved; they are never
fetched automatically. A Git installation that rejects `--no-lazy-fetch` stops
with a Git-inspection limitation before those reads. Supply suitable local Git
inputs/version through the existing workflow; the kit installs or configures
nothing automatically.

If a review checkpoint exists, inspection validates its packet digest and content
identity against the current candidate, Spec, verification, repository rules and
canonical review core. It checks the latest report's actual bytes, schema and
bindings, then recomputes reviewer provenance using the referenced observer
evidence. Changed verification files or stale packet/report inputs block use of
old approval. Missing or malformed records stay `BLOCKED`, without repairs to
foreign records or replacement of evidence.

Interpret the returned status as a continuation decision:

- `READY`: the recognized agreed-Spec, implementation or verification checkpoint
  can continue at its stated next action. This says nothing about whether tests
  passed, evidence is sufficient or review has occurred.
- `PENDING`: consent or Independent Review remains outstanding. Preserve the
  reusable packet and actual numbered attempts. A self-check and unverifiable
  provenance retain this outcome even when the index claims `REVIEWED`.
- `UNKNOWN`: necessary verification, review authenticity/interpretation or
  Completion remains unresolved. Inspect the referenced real evidence. Valid
  receipt relationships alone do not prove a real independent review.
- `BLOCKED` (exit 2): identity, schema, files or frozen inputs changed or cannot
  be validated. Describe the exact gap, preserve the records and obtain current
  verification/re-review as appropriate. Never relabel an old report as approval
  for the new candidate.

Before continuing, inspect the actual consent reference and scope. Read accessible
verification results and their sufficiency assessment against the current AC;
`UNAVAILABLE` references are gaps, not successful checks. Read any actual report,
findings and observer records and assess whether the stated observations establish
separate context, read-only controls, exact inputs and no writes. A helper `READY`,
`REVIEWED` field, phase or status bit never grants PASS by itself. Unresolved work
can be handed off with the actual candidate and outstanding actions.

For an optional Spec Review, inspect its recorded revision/digest; an earlier
revision's report remains historical and supplies no current approval. Spec
Review stays optional. For candidate drift, retain old manifests and attempts;
recheck accepted ownership and actual verification before preparing new review
inputs. Material scope changes require renewed consent. Follow [repair and Completion](completion.md) after checkpoint recovery. Completed
records revalidate their current assessment and report history; `ATTRIBUTABLE`
means the recorded judgments remain tied to unchanged inputs, not a new PASS.
A missing assessment stays UNKNOWN; changed assessment or reviewed inputs block
reliance on prior Completion.

Only if task-state updating is authorized, add `--update-state`. After successful
structural recognition and input checks it atomically updates `state.json`'s
next action/blocker only. It preserves phase, review status, candidate, Spec and
all existing reports, packets and evidence; the returned current assessment takes
precedence over a historical review-status bit. A malformed, foreign, tracked or
drifted record is never overwritten under this option. No automatic branching,
worktree creation, commit, cleanup, reset, deletion, sync or publishing occurs.
V0 assumes one writer; these checks are not a concurrency or locking platform.
