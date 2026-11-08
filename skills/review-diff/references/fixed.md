# Fixed local comparisons

Resolve an explicit local base using a user-provided Python 3.11+ interpreter:

```text
python3.11 -B <skill>/scripts/fixed_scope.py --root <root> --base <ref> [--tip <ref>] [--owned <path> ...]
python3.11 -B <skill>/scripts/fixed_scope.py --root <root> --commit <ref> [--owned <path> ...]
```

`--base` uses the unique merge base with tip (default HEAD), then compares only
committed objects to tip. `--commit` compares a non-root commit to its first
parent; a merge commit thus means its first-parent delta, which must match the
user's intent. If the intended merge-parent comparison is unclear, ask or limit
scope. Root commits are unsupported by the single-commit form. Exact whole-file
scope is still available without a historical comparison. Do not silently turn
an ambiguous range or mixed request into a supported mode.

The helper performs no network lookup, fetch, remote mutation or PR resolution.
For a PR, use only supplied verified local base/tip information, otherwise state
the missing comparison information. Never guess a branch from a PR number.

Inspect `comparison.files` at their **committed** content, including base content
for deletions. Record resolved base, tip, merge-base, each selected layer's blob
SHA-256 and patch SHA-256. Each layer's line references refer to that layer.
Protected task metadata is excluded. Binary, symlink and submodule input must
retain the helper's limitations; decoded non-text is not complete text coverage.

The separate `workspace` member identifies staged, unstaged, untracked additions
relative to current HEAD. It does not extend the committed comparison. State
whether those additions were requested, inspected separately or excluded. Only
attribute clearly owned/relevant workspace paths; `--owned` applies to workspace
selection, not committed comparison paths. For committed-only requests, do not
review workspace contents, even when they hide or undo a committed defect. Full
current files cannot substitute for tip blobs. Disclose excluded unrelated files
and unestablished ownership. Include empty-layer observations accurately.

After code reading, repeat the same invocation and compare identities; changed
objects, HEAD or workspace patches invalidate earlier coverage claims. This is
not an atomic snapshot. No source, tests, builds, analyzers or corrective tools
are executed. Follow the existing protected Git-read contract.
