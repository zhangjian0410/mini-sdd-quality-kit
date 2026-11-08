# Task storage and public helper

Use a user-provided Python 3.11+ interpreter. From any directory, pass the actual
Git worktree root and a task ID of 1–64 ASCII letters, digits, underscores or
hyphens, beginning with a letter or digit. Supply the Mini Spec bytes on stdin:

```text
<python> -B <skill>/scripts/task.py --root <root> create --task <id>
<python> -B <skill>/scripts/task.py --root <root> confirm --task <id> --spec-sha256 <digest> --consent-reference <actual-user-approval-reference>
<python> -B <skill>/scripts/task.py --root <root> revise --task <id> --previous-sha256 <current-digest>
<python> -B <skill>/scripts/task.py --root <root> spec-review --task <id> --spec-sha256 <current-digest>
<python> -B <skill>/scripts/task.py --root <root> begin --task <id>
<python> -B <skill>/scripts/task.py --root <root> checkpoint --task <id> --owned <path> [--owned <path> ...] --verification-status SUFFICIENT --assessment-reference <actual-assessment> --evidence-reference <actual-result-reference>
<python> -B <skill>/scripts/task.py --root <root> checkpoint --task <id> --owned <path> --verification-status INCOMPLETE --assessment-reference <actual-assessment> --missing <necessary-unrun-check>
<python> -B <skill>/scripts/task.py --root <root> resume --task <id> [--update-state]
```

`create` requires a new `.specdd/<id>/`; it writes only `spec.md` and `state.json`
and waits for consent. Existing task directories, symlinks and tracked task
storage are protected. Another active or unrecognized task record prevents a
new writer. A prior completed task may remain only when its minimal schema,
task/worktree identity, actual Spec digest/revision and fixed base are recognized.
This storage recognition does not certify Completion, review or stale approval.
No local exclusion is installed:
task records remain untracked; never stage them, include them in a PR, or treat
them as product changes. No tracked `.gitignore` modification is needed.

`confirm` validates the worktree identity, current Spec revision/digest and fixed
Git base before recording the actual consent reference. The caller must possess
the real user approval; this string cannot independently prove consent.

`revise` accepts a draft or an active implementation/verification checkpoint when
material scope changes. It requires the old digest and a new revision identity,
reads replacement Spec bytes on stdin and returns to `AWAITING_CONSENT`. It clears
current consent, candidate, verification and code-review approval, while preserving all
existing product bytes, candidate manifests and actual review files. The caller
must obtain renewed approval before further implementation; old evidence is not
approval for the revised scope. An `implementation_started` bit keeps the original
fixed base when already accepted implementation has later commits; the base must
remain an ancestor. Initial unimplemented drafts still reject unexpected HEAD
drift. This does not make a commit.

`spec-review` records an actual optional review body supplied on stdin, binds it
to the current Spec revision/digest, atomically publishes the next numbered report
without overwriting old attempts, and points `latest_review` to it. It does not
execute a review or prove its independence. Supply only actual observations;
leave it unused when optional review was skipped. A prior report may remain tied
to an older revision after `revise`; preserve that original binding and do not
interpret the pointer alone as current approval.

`begin` requires current scope consent and enters `IMPLEMENTING` without editing
product files. `checkpoint` uses explicitly owned paths, preserves fixed base and
Spec/consent binding, identifies the actual candidate and adds a small index of
verification references, assessment and missing checks. It accepts `IMPLEMENTING`,
`REVIEW_READY` or `BLOCKED_VERIFICATION`; it never runs verification or grants
Independent Review or Completion. See [implementation](implementation.md) for the
actual evidence and ownership duties. Repeated checkpoints preserve older
candidate manifests; never relabel old evidence to approve changed inputs.

The index carries schema version, task/worktree identity, phase, Spec path,
revision and digest, fixed base, candidate and latest review references, next
action, blocker, and an approval reference only after consent. Candidate is null
before an implementation checkpoint. `latest_review` is null unless a Spec Review was
actually recorded; a reference to it is not a code-review result. The index
contains neither duplicated AC nor all findings. Each file update is
atomic. The Spec/index pair is not a multi-file transaction: interruption can
leave an incomplete or mismatched record, which must be inspected and remains
blocked rather than trusted or silently overwritten. V0 assumes one writer;
there is no concurrent-write coordinator, lock service, backup cleanup or sync.

Exit 0 reports a successful local record operation; exit 2 reports `BLOCKED`
with a reason. An interpreter below 3.11 exits before any state write. Inspect
failures without deleting partial records or retrying against another task ID to
evade a collision. [Resume](resume.md) validates actual checkpoints without
performing Independent Review or certifying Completion. [Repair and Completion](completion.md)
adds bounded `repair --reason <confirmed-finding>` and `complete
--assessment-reference <existing-absolute-JSON-assessment>` operations. Completion
stores only the assessment reference/digest and current candidate/Spec/report
bindings in the index; all actual report attempts remain unchanged.
