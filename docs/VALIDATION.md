# Validation status and limits

This is a public summary of retained private development evidence and the new
standalone source check. Raw host captures, task records and private coordinator
logs are excluded. The product contract describes intended behavior; it does not
turn an unobserved capability into PASS.

## Retained actual Codex observations

Development on macOS used Codex CLI 0.167.0, Python 3.11.15 and Git 2.49.0.
Actual fresh processes explicitly loaded canonical Skill files outside native
Skill discovery. The known-defect/corrected review pair, no-Spec N/A reporting,
read-only command and file/Git effects, a Full Task implementation and a genuinely
fresh same-host recovery were observed. Recovery retained PENDING where separate
review evidence was unavailable. One neutral-request observation supplied a
negative control; it is not a universal guarantee against automatic invocation.

Separate bounded development review exercises retained the original Reviewer
text, including UNVERIFIED self-labels, and independent coordinator evidence for
launch identity, read-only/never settings, actions and before/after effects.
A role name or a report's own label was not accepted as proof of independence.
Those exercises do not validate all native subagent configurations. Independent
review remains an execution property to establish for each Full Task candidate.

The raw observations belong to their recorded development candidates. Later
small guard/header repairs were covered by deterministic checks and independent
development review; the complete live suite was not repeated on the final source
revision or this relocated public snapshot. Core/test byte identity with the
final development source preserves provenance, not a new live PASS.

Native Skill catalog installation, native subagent policy, Windows and Linux
remain unverified. Review Only itself runs no tests; existing evidence never
silently becomes verification of a different candidate.

## Qoder Desktop

Only application metadata (version 0.5.6) was obtained. Normal UI access was
refused. Actual Desktop file loading, known-defect review, read-only effects,
fresh recovery and Codex-to-Desktop handoff are **NOT_RUN**, with overall runtime
readiness **UNKNOWN**. The [Desktop procedure](hosts/qoder-desktop.md) describes
minimum future observations, not completed tests. Qoder CLI and Qoder IDE are
outside required V0 scope; old NOT_RUN evidence is preserved privately.

## Standalone deterministic source check

Run from the source root with your supplied Python 3.11+ and Git:

```sh
python3.11 -B -m unittest discover -s tests -v
```

Live model cases are opt-in and remain skipped without `REVIEW_DIFF_LIVE=1`.
They can consume authenticated model usage; deterministic checks do not establish
actual Skill behavior, Desktop compatibility or enforced reviewer independence.
The original final development run discovered 77 tests: 63 passed and 14 live
cases skipped. The public packaging run is recorded after execution in this
section; private command logs stay outside the public tree.

Public packaging check on 2026-11-08: **77 discovered, 63 passed, 14 skipped**,
exit status 0, Python 3.11.15. `REVIEW_DIFF_LIVE` was unset. All 42 core/test files
matched the final development source bytes. All 5 bundled license-file Git blob
identities matched their pinned source record; local Markdown file links resolved.
The targeted public-tree privacy scan reported no findings. This is a relocated
source check, not a new live model or Desktop test.

## Source and evidence boundaries

[SNAPSHOT.json](../SNAPSHOT.json) names the development source revision.
All 42 core Skill/test files, including third-party notices, are unchanged.
Public docs remove private archive links rather than exposing historical logs.
[SOURCES](../SOURCES.md) retains immutable upstream source/license identities.
No unpublished private receipt is required to follow the user instructions or
execute deterministic tests. Public readers can inspect the shipped source and
run those checks; retained live observations are a summary, not public raw proof.
