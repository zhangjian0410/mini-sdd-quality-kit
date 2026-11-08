# Implementation, verification and candidate checkpoints

Use the current accepted Mini Spec, exact byte digest and actual user scope
confirmation. Inspect pre-existing changes and ownership, applicable repository
instructions and public verification seams before product edits. Leave unrelated
work intact and disclose exclusions. Record `begin` with the confirmed interpreter
using [task storage](storage.md). Invalid records, Spec or base stop this step.

Implement only accepted behavior using repository conventions. Ordinary in-scope
changes remain authorized. A material scope change needs a revised Mini Spec and
renewed approval; stop dependent work and explain the proposed change. Do not
use a checkpoint to expand scope or attribute someone else's work to the task.

## Proportional Verification Evidence

Choose checks for the actual AC and risk. Automated tests, actual manual behavior
observations and applicable static checks are usable; an automated suite is
optional. Execute selected checks, read complete outputs/exit statuses and assess
their sufficiency. Distinguish actual observations from model inference, static
reasoning, prior results and unrun checks. A static check cannot prove unrelated
runtime behavior; a passing command does not establish every AC.

Retain concise usable evidence references in the conversation or existing
authorized logs/results. Explain what those observations establish and why they
are adequate for the relevant AC. No per-AC screenshot, mandatory evidence file
or extra approval platform is required. A referenced log needs its real command,
result and tested input identity, not just a success label. The helper records
references; it neither executes checks nor judges sufficiency.

Necessary unavailable checks stay `NOT_RUN` or `UNKNOWN`. Use `INCOMPLETE` with
missing evidence and next actions; retain the implemented candidate for handoff.
Do not label affected behavior PASS.

## Fix the Review Candidate

Select exact root-relative product paths whose accepted ownership/relevance is
established. Reinspect actual committed, staged, unstaged and accepted untracked
changes against the fixed base; disclose exclusions and uncertain ownership.
The helper records base/HEAD/index/current raw-byte digests and file modes for
selected paths. It never runs filters, source, tests, builds or corrective tools.
Task/Git metadata (including case variants of the reserved `.specdd` and `.git`
path components), path escapes, symlinks, submodules and other nonregular selected
inputs are rejected rather than silently claimed as covered.

`checkpoint` fixes those inputs and references the actual verification assessment.
Selected dirty/untracked changes require a minimal `candidate-<ID>.json` manifest,
published without replacing older candidates. A clean committed candidate needs
no extra manifest: HEAD, fixed base and selected scope reconstruct it. Unrelated
paths do not affect selected identity; task metadata stays outside enumeration.

This is not an atomic filesystem/Git snapshot. Recheck selected inputs after
checks and before relying on the candidate. Changed inputs need a new identity
and affected verification; old evidence is not current approval. Review validation follows [Independent Review](review.md); fresh-session recovery
remains a separate checkpoint.

`SUFFICIENT` records the caller's assessment of actual evidence for this candidate
and produces `REVIEW_READY`; Independent Review remains outstanding. `INCOMPLETE`
produces `BLOCKED_VERIFICATION` with missing checks and next actions. Neither is
Independent Review PASS, Completion, Issue closure, merge, release or business
acceptance, or permission to change established Git/remote/workflow practices.
