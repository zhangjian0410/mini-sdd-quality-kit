# Mini-SDD Quality Kit

Two canonical Skills for existing coding repositories:
[`review-diff`](skills/review-diff/SKILL.md) reviews a change in chat;
[`mini-sdd`](skills/mini-sdd/SKILL.md) carries an agreed task through implementation,
verification, independent review and recoverable local Completion or handoff.
Keep both complete sibling folders, references, helpers and license notices.

The first-batch V0 runtime hosts are **Codex and Qoder Desktop**, following the
PO scope correction of 2026-11-08. The initial observed platform is macOS.
Codex's strict manual entry and fresh-session recovery were observed. Desktop's
two minimum Smokes ran: bounded recovery and unchanged fixture effects **PASS**,
G3 Review Only report precision **FAIL**. After the G5 grounding repair,
G6's single precision recheck **PASS** on `490d608`: one real finding, with the
hypothetical repair risk kept outside findings. Enforced controls and overall
readiness remain **UNKNOWN**; Full Task independent review remains
**PENDING / UNVERIFIED**.
Desktop behavior verification was **NOT_RUN**. Windows/Linux are unverified. Qoder CLI and Qoder
IDE are outside required V0 acceptance; their historical records stay unchanged.
The [delivery evidence](docs/DELIVERY.md) separates package delivery from actual
runtime validation. The kit helps find defects without guaranteeing correctness.

## Obtain the source

Public source repository: <https://github.com/zhangjian0410/mini-sdd-quality-kit>.
The source is publicly available on `main`.
[v0.1.0-alpha.1](https://github.com/zhangjian0410/mini-sdd-quality-kit/releases/tag/v0.1.0-alpha.1)
is already published.
[v0.1.0-alpha.2](https://github.com/zhangjian0410/mini-sdd-quality-kit/releases/tag/v0.1.0-alpha.2)
was published as a GitHub Pre-release on 2026-11-08 at 04:43:26 UTC, with its Tag
pointing to `abf120f58a8ae8ccb844674410c162a0e7e4c64d`.
The [release notes](docs/releases/v0.1.0-alpha.2.md)
describe the G2 Git-filter repair, retained checks and G3 limitations. See
[SNAPSHOT.json](SNAPSHOT.json) for the historical development source and subsequent
public changes. This is a conditional Alpha pre-release, not complete V0 acceptance.
[v0.1.0-alpha.3](https://github.com/zhangjian0410/mini-sdd-quality-kit/releases/tag/v0.1.0-alpha.3)
was published as a GitHub Pre-release on 2026-11-08 05:43:02 UTC, targeting
merge `1d309dcfe606e80b1fbfc43d9b9fb0e693c986bb`. Its
[notes](docs/releases/v0.1.0-alpha.3.md) cover G5 hardening and G6's single-run
observation; [validation](docs/VALIDATION.md#g5-grounding-hardening-and-g6-single-precision-recheck)
retains their limits. Later publication-receipt documentation on `main` does not
move that Tag.
Download the complete source archive or clone the repository.
Keep the root `SOURCES.md`, both complete sibling Skill folders, their references,
helpers and license notices together. No personal bootstrap or framework is needed.

## Start without installing a framework

Keep a kit checkout outside host Skill-discovery folders and your business repo.
Explicitly ask your host to read the desired canonical file and its references.
This strict manual path creates no global auto-matching entry. Host syntax,
permissions and actual observations are in the [Codex](docs/hosts/codex.md) and
[Qoder Desktop](docs/hosts/qoder-desktop.md) guides.
Native catalog installation is a separate, incompletely tested alternative.

Helpers need **user-provided Python 3.11+** and only its standard library; Git is
needed for Git/task operations and must support `--no-lazy-fetch` (observed with
Git 2.49.0; an exact minimum version is not established). Verify the interpreter
you intend to supply:

```sh
/absolute/path/to/python3.11 -B -c 'import sys; print(sys.version); raise SystemExit(sys.version_info < (3,11))'
```

Review Only can inspect supported files without that interpreter, disclosing
missing helper/digest/coverage evidence. Full Task stops **before task or product
writes** if the supplied runtime is missing or too old. Nothing installs Python,
packages, a package manager, framework or personal runtime.

## Review Only

Start a read-only context and replace the paths:

```text
Explicitly read <KIT>/skills/review-diff/SKILL.md and its report contract.
In <REPO>, review current workspace changes. These paths belong to my change:
<OWNED PATHS>. Unrelated pre-existing work: <PATHS OR NONE>.
No authoritative Spec is supplied. Return the report only in chat.
```

Alternatively request exactly `<FILE>` as a whole file, or supply a fixed local
base/tip or commit. The [scope references](skills/review-diff/references/workspace.md)
and [fixed comparisons](skills/review-diff/references/fixed.md) distinguish staged,
unstaged, owned untracked and committed inputs. Ambiguous ownership/base limits
the review; a clean workspace is an empty default scope. Git status alone does
not prove ownership. Full Task metadata `.specdd/` is protected.

Optionally supply an authoritative Spec/AC and existing verification evidence.
The [report](skills/review-diff/references/report.md) identifies inspected bytes,
coverage, exclusions and grounded findings along Spec Compliance and Code Quality.
No Spec means **N/A**. Existing results retain their candidate and scope;
behavior checks in Review Only are **NOT_RUN**. Missing evidence remains UNKNOWN.
A same-context check is SELF_CHECK; unverifiable independence is UNVERIFIED.
No findings does not mean tests or independent approval passed.

Review Only creates no task, Spec or files, runs no reviewed code, tests, builds,
analyzers or corrective tools, and changes no Git or remote state. Its only
persistence exception is an explicit request such as `Export the final report to
<NEW-PATH>`; an existing destination or symlink is preserved as a collision.

## Full Task

Use a context whose existing permissions cover your requested repository work:

```text
Explicitly read <KIT>/skills/mini-sdd/SKILL.md and its references in <REPO>.
Use my Python <PYTHON-3.11+> and task ID <SAFE-ID>.
Request: <OBSERVABLE CHANGE AND CONSTRAINTS>.
Inspect current behavior and existing verification seams, present the Mini Spec
and its exact revision/scope for confirmation before implementation.
```

The canonical [Mini Spec template](skills/mini-sdd/references/mini-spec.md) has six
sections. Only consequential gaps need clarification; optional Spec Review stays
optional. Full Task records live locally in `.specdd/<SAFE-ID>/`: the Spec, tiny
index, actual numbered reviews and a candidate manifest only when needed.
Keep them uncommitted and out of PRs. Existing directories, tracked/symlinked
records and another active writer are protected. Supply separate worktrees for
parallel Full Tasks; the kit creates none. See [storage](skills/mini-sdd/references/storage.md).

Confirmation binds the actual Spec revision/digest and coding scope. Then follow
[implementation](skills/mini-sdd/references/implementation.md): change only owned
scope, use repository conventions and inspect appropriate automated, actual
manual or static results against AC and risk. A suite is optional; necessary
missing checks produce an incomplete handoff, not PASS. Identify the actual
candidate, including agreed dirty/untracked bytes, rather than HEAD alone.

[Independent Review](skills/mini-sdd/references/review.md) uses `review-diff` on
that candidate in a verifiably separate read-only context. Inspect input identity,
launch/observer evidence, actual actions and effects. A role name, fresh session
or verbal assertion alone is insufficient. If unavailable, retain a reusable
Review Launch Packet and **PENDING**, without inventing a numbered report.

[Repair and Completion](skills/mini-sdd/references/completion.md) confirm findings,
repair in scope, rerun affected checks, identify the new candidate and re-review
it. Ordinary repairs use existing consent; material scope changes require renewed
confirmation. Preserve prior attempts. Unresolved Blocking Findings or necessary
verification/review gaps prevent Completion. Non-blocking suggestions and clearly
unrelated issues can remain disclosed. Local COMPLETE means the latest candidate
meets the agreed implementation, evidence and Independent Review conditions;
it grants no Issue closure, merge, release or business acceptance.

## Resume, upgrade and remove

In a genuinely fresh session, explicitly load `mini-sdd` and request `Resume
<REPO>/.specdd/<ID> using <PYTHON>`. Follow [recovery](skills/mini-sdd/references/resume.md)
to validate actual worktree/schema/files, Spec/consent, base, candidate/current diff,
evidence and latest report/provenance before trusting the index. Default recovery
is inspection; state updates need explicit authorization. Drift requires current
checks and appropriate re-review. Preserve PENDING/UNKNOWN/BLOCKED and next actions.
Cross-host recovery requires the **same local filesystem and worktree**; the kit
provides no hidden upload or cross-device sync. Observed scope and remaining gaps are in
[delivery evidence](docs/DELIVERY.md).

Keep the old kit and local edits when upgrading. Compare versions, choose the new
canonical path explicitly and recheck recovery/host controls. Changed core inputs
can invalidate a pending packet; preserve its original bundle/evidence or prepare
new inputs and re-review. Never relabel historical approval. Stop manual use by
ceasing to reference the kit. For separately installed native entries, inspect and
remove only unchanged kit-owned copies/links; preserve modifications, unrelated
host files and `.specdd/` evidence. Host guides provide their specific boundaries.
The kit does not change business instructions, hooks, CI, tracked Git config or
established workflows, and does not automatically commit, push, publish or clean.

## Examples, provenance and development evidence

The [known-defect](tests/fixtures/logic_bug/pricing.py) and
[corrected](tests/fixtures/corrected/pricing.py) files are a small review pair.
The canonical [Spec template](skills/mini-sdd/references/mini-spec.md),
[report format](skills/review-diff/references/report.md) and
[launch-packet procedure](skills/mini-sdd/references/review.md) are reusable;
no parallel template rules are required. See [SOURCES.md](SOURCES.md) for five
pinned upstream methods/licenses, [V0 baseline](docs/V0-IMPLEMENTATION.md), and
[validation scope and limitations](docs/VALIDATION.md).

Run deterministic development checks with your supplied interpreter:

```sh
python3.11 -B -m unittest discover -s tests -v
```

Opt-in actual Codex tests require authenticated CLI access and may consume model
usage. Keep raw runtime captures outside this repository because bootstrap may
contain private context. To enable them, use `REVIEW_DIFF_LIVE=1` and set
`REVIEW_DIFF_EVIDENCE_DIR=<OUTSIDE-KIT-PATH>` for that command. Without the flag,
live cases are skipped and actual Skill behavior is NOT_RUN by that suite.
Private development instructions, raw model captures and historical task records
are excluded from this public source snapshot.

## License

Original contributions are licensed under the [MIT License](LICENSE).
Adapted third-party methods retain their own MIT or Apache-2.0 terms,
copyright notices and attribution. See [SOURCES.md](SOURCES.md) and both
[mini-sdd notices](skills/mini-sdd/references/NOTICE.md) and
[review-diff notices](skills/review-diff/references/NOTICE.md).
The root MIT License does not replace those bundled third-party terms.
