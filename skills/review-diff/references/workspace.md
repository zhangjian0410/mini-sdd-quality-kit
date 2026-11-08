# Default workspace inspection

Use a user-provided Python 3.11+ interpreter with bytecode disabled:

```sh
python3.11 -B <skill>/scripts/workspace_scope.py --root <worktree-root>
```

Read-only preliminary Git inspection is allowed; the helper need not be the
first Git command. Assess the operations by their actual scope, input identity
and effects. For direct Git reads, disable optional locking and any applicable
configured programs before index/worktree inspection, or use this helper's
protected reads. In particular, fsmonitor, clean/process filters, external diff,
text conversion and submodule dirty scans can execute configured programs.
The mere occurrence of `git status` or `git diff` is not evidence that a write or
program execution happened. Disclose an observed effect or an unresolved risk
with its evidence; preserve the file/Git-state and no-test/no-corrective-tool
requirements regardless of command order.

The helper prints JSON to stdout. It enumerates staged, unstaged and untracked
paths without selecting content automatically. It never establishes ownership.
Ignored files and committed history are outside this default scope. `.specdd/`
metadata is protected even when tracked. No interpreter/package installation.
If Python or Git inspection is unavailable, use supported read-only facilities
and report missing identity/coverage checks; never claim the helper ran.

Establish relevance and ownership from the user's scope, supplied task context,
or explicit attribution. Directory proximity, Git status and matching filenames
alone are insufficient. If the request clearly attributes all current changes,
select the enumerated non-protected paths. Otherwise select only established
paths; disclose unrelated and uncertain paths as exclusions, requesting narrow
clarification if needed. No speculative reading of excluded file contents.

Rerun with repeated `--owned <exact-root-relative-path>` arguments for established
paths. Record the ownership grounds in the report, not merely the flag. Output
includes HEAD, layer flags, current byte hashes (null for deletion), and selected
staged/unstaged binary-patch hashes. These are inspection identity, not findings.
Unknown owned paths and Git failures are limitations. An unborn HEAD is not a
comparison base; do not initialize or commit to manufacture one.

Read selected current files and their actual changes. Inspect staged and unstaged
patches separately, including index content where different from the worktree.
A staged defect can be hidden by an unstaged correction; a net HEAD diff alone
misses this case. Read the helper's selected `staged_diff` and `unstaged_diff`
fields as the actual patches, alongside their hashes. It disables optional
locking, fsmonitor, configured clean/process filters, submodule dirty scans, external diff, text
conversion and rename detection; pathspecs are literal. Raw worktree bytes are
inspected with filters disabled, so disclose conversion semantics as a gap.

For missing context, use `git --no-optional-locks -c core.fsmonitor=false
show --no-ext-diff --no-textconv <HEAD:path-or-:path>` blob reads for HEAD/index deleted or staged-only content; never execute
repository content, Git aliases, external diff drivers or filters. Avoid Git
environment overrides redirecting the repository. Treat renames as deletion and
addition. Report unsupported symlinks, submodules, binary files and unmerged
entries as uninspected/partial rather than approval. Selected symlinks or parents
must not be followed outside scope. Read only required contextual source, state
why it is needed, and distinguish it from attributed changes.

After inspection rerun enumeration with the same ownership selection. Compare
HEAD, discovered paths, flags, selected byte hashes and layer patch hashes.
Drift means the report is limited to observed inputs, not a stable latest
candidate; re-inspect affected inputs or state the unresolved coverage gap.
Enumeration is read-only but not an atomic snapshot. Always disclose ignored
files and uninspected committed history. A clean result states empty default
scope, with no finding or review PASS manufactured from absence of changes.
