# Codex on macOS

Use the two canonical directories, `skills/review-diff` and `skills/mini-sdd`,
from one kit checkout. No personal AI system, package manager, third-party Python
package, hook, or repository configuration is required. Full Task requires a
user-provided Python **3.11+** interpreter; `python3` on macOS may be older.
Check the interpreter you intend to supply:

```sh
python3.11 -B -c 'import sys; print(sys.version); raise SystemExit(sys.version_info < (3,11))'
```

## Tested entry: strict manual file loading

Keep the checkout outside Codex's Skill discovery locations. Do not copy or link
it into `.agents/skills`, `.codex/skills`, or a user Skill directory for this path.
Start Codex in the existing repository and explicitly ask it to read the desired
canonical `SKILL.md`; relative references and sibling Skills stay together in the
checkout. This is **manual file loading**, not native Skill installation or a
claim that a `$skill-name` command was discovered.

For example, replace both absolute paths and start a read-only session:

```sh
codex exec --sandbox read-only -c 'approval_policy="never"' \
  --cd /absolute/path/to/repository \
  'Explicitly invoke review-diff by reading /absolute/path/to/kit/skills/review-diff/SKILL.md and its references. Review current workspace changes. No authoritative Spec is supplied. Return the report in chat; run no tests or corrective tools and write no files or task records.'
```

An explicit whole-file example is `Review exactly pricing.py as the complete
whole-file scope`. Supply a real fixed base when reviewing committed changes;
do not conflate that comparison with dirty workspace layers. The report should
identify inspected bytes and coverage, use Spec Compliance `N/A` without a Spec,
and preserve `NOT_RUN` for behavior verification. An empty finding list grants
neither correctness nor independent approval.

For Full Task, start a session whose existing permissions permit only the agreed
repository work, then enter:

```text
Explicitly invoke mini-sdd by reading /absolute/path/to/kit/skills/mini-sdd/SKILL.md.
Use /absolute/path/to/repository and my Python /absolute/path/to/python3.11.
Request: reject empty pricing inputs while preserving nonempty arithmetic mean.
Inspect the repository, present the Mini Spec and exact revision for my approval,
then implement only the approved scope. Preserve the existing Git workflow.
```

Full Task invocation permits its necessary local task records; implementation
waits for approval of the actual Spec revision and scope. Records are local
untracked `.specdd/<task-id>/` files; preserve them and keep them out of commits.
The kit does not install Python, create branches, commit, publish, or modify a
business repository's instructions, hooks, CI or tracked configuration.

Start a **new session** for recovery, on the same filesystem/worktree:

```text
Explicitly invoke mini-sdd by reading /absolute/path/to/kit/skills/mini-sdd/SKILL.md.
Resume task <task-id> in /absolute/path/to/repository using my supplied Python.
Read the actual Spec, consent, records, candidate/diff and existing evidence;
invoke the documented resume helper without --update-state for inspection.
Preserve unresolved review and verification gaps.
```

This recovers task files, rather than depending on Codex's old chat transcript.
Changed candidate, Spec, evidence or packet inputs require current checks and
appropriate re-review; an index cannot grant PASS.

## Controls and evidence

Review Only uses a read-only reviewer. For Full Task independent review, launch
a separate context with enforceable read-only controls, deliver the identified
candidate, Spec, rules and Verification Evidence, and independently inspect the
launch, actual command audit and before/after repository, Git and task effects.
Do not assume a native subagent inherits read-only controls. A role name or new
session alone proves no independence. If controls or provenance are unavailable,
use the canonical helper to retain a reusable Review Launch Packet and `PENDING`.

The [public validation summary](../VALIDATION.md), derived from retained private
development records, describes actual Codex CLI 0.167.0 observations on macOS. It separates helper checks,
actual Skill behavior and actual host runs. The smoke used ephemeral fresh
processes, `--ignore-user-config`, approval `never`, read-only review and isolated
runtime directories; fixture implementation used workspace-write. These flags
were checked against that binary's help. Existing authentication was reused by
the runtime; the coordinator did not inspect, copy or modify credentials.
Runtime credential-file metadata was not captured. Normal user
configuration and permissions still apply to the simpler examples above.

Native catalog installation, native subagent policy and other operating systems
remain unverified here. Official [Codex Skill documentation](https://learn.chatgpt.com/docs/build-skills)
describes discovery and invocation; documentation does not substitute for a host
smoke. Manual entry avoids adding an automatically matching catalog entry. The
neutral-request observation establishes only the tested negative control, not a
universal model-behavior guarantee.

## Upgrade and uninstall

For manual entry, keep the new kit checkout at a separate versioned path. Compare
its two Skill directories with your current copy, preserve any local edits, and
point the next explicit prompt at the chosen version. Keep both sibling Skills
and their scripts/references together. Validate existing task recovery before
continuing old records after an upgrade; changed core inputs can invalidate a
pending packet and require a new one. Do not replace task evidence to make it fit.

To uninstall this manual entry, stop referencing the checkout. There is no
installed entry, hook or global setting to remove. Archive or remove only your
own unchanged kit copy after preserving local edits. Keep repository work and
`.specdd/` records/evidence until their owner explicitly decides their retention.
If you separately installed catalog entries, inspect and remove only entries you
own; this manual-path smoke does not validate that installation or removal.
