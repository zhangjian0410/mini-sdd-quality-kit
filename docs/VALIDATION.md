# Validation status and limits

This is a public summary of retained development checks and host observations,
including G2/G5 repair acceptance, G3 Desktop Smokes and the G6 single precision
recheck. Raw host captures, task records and private coordinator
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
revision or this relocated public snapshot. The original packaging byte-identity
check preserved provenance, not a new live PASS; G2 subsequently changed core/test
files as recorded below.

Native Skill catalog installation, native subagent policy, Windows and Linux
remain unverified. Review Only itself runs no tests; existing evidence never
silently becomes verification of a different candidate.

## Qoder Desktop

Earlier development obtained version 0.5.6 metadata but normal UI access was
refused. On 2026-11-08, G3 obtained normal Computer Use access and ran both minimum
Smokes on `a9c0f986df93511c10d97ab2195670f4708ab905`, using explicit canonical
Skill files outside native discovery folders. The observed model UI label was
DeepSeek-V4.1-Flash-1017 (high); the current app version was not independently
rechecked. The overall G3 result is **not a clean PASS**.

| Observation | Result and boundary |
|---|---|
| Manual file loading and known-defect detection | Observed: `len(prices - 1)` at pricing.py:4 found; canonical finding fields, N/A Spec, NOT_RUN verification and UNVERIFIED independence present |
| Review Only report precision | **FAIL**: CQ-2 discussed a hypothetical `len(prices) - 1` repair that was never made. It is a speculative false positive for the current candidate, not a second current defect |
| Review Only fixture effects | **PASS within the fixture**: complete before/after file, Git and task maps equal; no task state created |
| Fresh recovery and Codex-to-Desktop handoff | **PASS for this minimum observation**: a new Desktop task inspected actual Spec, consent, candidate, diff and existing evidence, then ran resume without `--update-state` on the same filesystem/worktree |
| Recovery fixture effects | **PASS within the fixture**: file, Git and task maps unchanged; original packet retained |
| Full Task independent review | **PENDING / UNVERIFIED**: next separate canonical review action preserved; no numbered report or Completion |
| Enforced read-only controls and overall readiness | **UNKNOWN**: actual permission setting was automatic approval; observed non-change does not prove enforcement or independent review |
| New Desktop behavior verification | **NOT_RUN**: no source or tests executed by the Desktop reviewer/recovery session; three Codex preparation assertions were prior evidence only |

The minimum observation and [procedure](hosts/qoder-desktop.md) do not establish
general compatibility. Local observation notes are transcriptions of real UI
output; original screenshots/full tool returns remain in the retained sessions.
Terminal accessibility output truncation is disclosed. Machine file maps and
Codex preparation logs are retained locally; raw evidence is not published here.
Effects of Qoder hooks outside the bounded fixtures were not independently
audited, so there is no whole-computer no-write claim. A new task and read-only
instruction alone do not establish enforced independence. Qoder CLI/IDE remain
outside required V0 scope; historical NOT_RUN records are preserved.

## G5 grounding hardening and G6 single precision recheck

[PR #4](https://github.com/zhangjian0410/mini-sdd-quality-kit/pull/4), associated
with [Issue #3](https://github.com/zhangjian0410/mini-sdd-quality-kit/issues/3),
clarifies the existing grounding rule: findings concern failures in the current
selected candidate. Risks exclusive to an unperformed repair belong in optional
advice, outside findings, their count and severity. The acceptance change is
specific to the four-line known-defect fixture, not a production report filter.

G5 implementation `490d6084e5fa6e2cd3a630add1427fb61b3ef262` was accepted locally.
The baseline oracle accepted true CQ-1 plus speculative CQ-2; the new regression
initially failed and then passed after the oracle was strengthened. Four
deterministic report controls passed. The full run discovered **85 tests:
71 passed, 14 opt-in live tests skipped**, exit 0; syntax compilation passed for
23 Python files and `git diff --check` passed. No typechecker is configured.
Separate fresh Standards, Spec and cross_checker development contexts found no
material issues; the committed bytes matched their reviewed candidate.

On 2026-11-08, G6 ran **one** fresh Qoder Desktop Review Only task on that exact
implementation, with the byte-identical G3 prompt, the same original fixture and
the same visible model setting, DeepSeek-V4.1-Flash-1017 (high). Actual file-read
audit named the canonical Skill and report-contract paths.

| G6 observation | Result and boundary |
|---|---|
| Real defect | **PASS for this observation**: one High finding for `len(prices - 1)` at pricing.py:4 |
| CQ-2 precision | **PASS for this observation**: no speculative second finding; related conditional risk remained optional advice explicitly outside findings/count/severity |
| Bounded effects | **PASS**: complete fixture/Git/task maps and snapshots of 209 product/Git files unchanged; no task state created in the fixture |
| Status labels | Spec Compliance **N/A**, reviewed-code behavior verification **NOT_RUN**, independence **UNVERIFIED** |
| Enforced read-only controls | **UNKNOWN**: actual permission setting remained automatic approval |
| Repeatability and general Desktop readiness | **UNKNOWN**: one observation, no pinned seed or backend attestation; no general compatibility PASS |

The original G3 precision **FAIL remains historical evidence**. G6 neither
reran the corrected pair nor expanded the host matrix, Full Task recovery or
pending independent review. Its optional advice did not disappear from all text.
No reviewed source or tests ran in the Desktop task. App version and backend
identity beyond the UI label were not independently checked; hook effects
outside bounded snapshots remain unaudited. No whole-computer no-write claim
is made.

Raw G6 UI/tool records, screenshots, prompt hashes and machine snapshots remain
private. The shipped JSON is explicitly a minimized G3 transcription derivative,
not a G6 runtime export. Later Alpha.3 documentation and publication work reuses
G5/G6 evidence without rerunning tests or promoting those observations to a new
full live acceptance on a later documentation commit.

## G2 protected Git inspection repair

[PR #2](https://github.com/zhangjian0410/mini-sdd-quality-kit/pull/2) fixed legal
filter driver names containing `=`. The former inline configuration overrides
could fail to disable clean/process programs during inspection, even with helper
exit 0. The shared inspector now preserves complete dynamic keys with
`--config-env`; workspace and fixed comparisons use that repair.

Retained acceptance for implementation `57489f3175a61a1c043a4c1802261975ca808f52`:
four real CLI regressions failed before the repair and passed afterward, covering
clean and protocol-valid process filters, empty/selected ownership, execution
markers, unchanged repository/Git snapshots and raw byte/patch identities.
Workspace and fixed scope suites each passed 10 tests. The final deterministic
run discovered **81 tests: 67 passed, 14 live skipped**, exit 0; syntax validation
passed for 23 Python files. No typechecker is configured. The original feedback
command also passed without filter side effects. These are retained G2 results,
not tests rerun during Alpha.2 documentation preparation.

Local independent development review found no material blocker; a nonblocking
duplicated-test-assertion suggestion remains deferred. Acceptance AC1–AC5 passed.
The [merge receipt](https://github.com/zhangjian0410/mini-sdd-quality-kit/issues/1#issuecomment-6716977609)
binds merge `a9c0f986df93511c10d97ab2195670f4708ab905` to the same reviewed/tested
file tree. G2 did not run live host checks; G3 later supplied only the bounded
Desktop observations above. Historical Codex observations are not promoted to
new Alpha.2 full live acceptance.

## Standalone deterministic source check

Run from the source root with your supplied Python 3.11+ and Git:

```sh
python3.11 -B -m unittest discover -s tests -v
```

Live model cases are opt-in and remain skipped without `REVIEW_DIFF_LIVE=1`.
They can consume authenticated model usage; deterministic checks do not establish
actual Skill behavior, Desktop compatibility or enforced reviewer independence.
The original final development run discovered 77 tests: 63 passed and 14 live
cases skipped. The historical public packaging run is recorded below; the later
G2 81/67/14 result is recorded separately above. Private command logs stay outside
the public tree.

Public packaging check on 2026-11-08: **77 discovered, 63 passed, 14 skipped**,
exit status 0, Python 3.11.15. `REVIEW_DIFF_LIVE` was unset. At that packaging
candidate, all 42 core/test files matched the final development source bytes.
All 5 bundled license-file Git blob
identities matched their pinned source record; local Markdown file links resolved.
The targeted public-tree privacy scan reported no findings. This is a relocated
source check, not a new live model or Desktop test.

## Source and evidence boundaries

[SNAPSHOT.json](../SNAPSHOT.json) retains the historical development source
revision and subsequent public changes. G2 changed a core helper and tests;
current core/test files are no longer byte-identical to the original snapshot.
Third-party notices and pinned source/license provenance are unchanged.
Public docs remove private archive links rather than exposing historical logs.
[SOURCES](../SOURCES.md) retains immutable upstream source/license identities.
No unpublished private receipt is required to follow the user instructions or
execute deterministic tests. Public readers can inspect the shipped source and
run those checks; retained live observations are a summary, not public raw proof.
