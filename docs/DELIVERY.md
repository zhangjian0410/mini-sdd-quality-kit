# Public source delivery

This snapshot contains exactly two canonical Skills, their Python 3.11+
standard-library helpers, references and third-party notices, plus tests and
portable documentation. Keep the sibling Skill directories together. Start with
[README](../README.md); the [V0 contract](V0-IMPLEMENTATION.md) defines intended
behavior, and [SOURCES](../SOURCES.md) records pinned third-party provenance.

This public tree is derived from development `main` at
`2f09ce38993548a5030d55b58603c84bd2a0d282`. The original packaging check established
core/test byte identity for its candidate. G2 later changed a core helper and
tests, so current files no longer retain complete byte identity with that source.
Public documentation was adapted to remove private
archive dependencies. The new Git repository has independent initial history;
original development commits, task records, host captures, personal configuration
and authentication are excluded.

The source snapshot is public on the repository's `main` branch.
[v0.1.0-alpha.1](https://github.com/zhangjian0410/mini-sdd-quality-kit/releases/tag/v0.1.0-alpha.1)
was published on 2026-11-08 at 01:59:01 UTC, targeting
`4f6141f7c23a299811ef0fd11809301b8b67936d`.
The current [snapshot identity](../SNAPSHOT.json) prepares **v0.1.0-alpha.2**
locally, with planned Tag `v0.1.0-alpha.2` and Pre-release status. Alpha.2 has not
been pushed, tagged or released by this preparation. PO accepted conditional
Alpha preparation with the disclosed limitations; publication remains a separate
authorization. See the [prepared release notes](releases/v0.1.0-alpha.2.md).

G2's filter repair was accepted on `57489f3175a61a1c043a4c1802261975ca808f52`
and merged as `a9c0f986df93511c10d97ab2195670f4708ab905`. That merged candidate is
the validation baseline for G3. Alpha.2 preparation changes only documentation
and metadata; it does not rerun product tests or host Smokes. The historical
development source above remains the provenance origin, not the current public
release candidate. This Alpha does not claim stable or fully validated V0 support.

## Runtime status

| Host or capability | Observed status |
|---|---|
| Codex on macOS, strict manual loading | Actual review and Full Task/recovery observations; bounded support only |
| Codex native catalog installation and native subagent policy | NOT_RUN / unverified |
| Qoder Desktop minimum recovery and fixture effects | Bounded **PASS**; actual manual file loading and known-defect detection observed |
| Qoder Desktop Review Only report precision | **FAIL**: extra speculative finding about an unperformed repair |
| Qoder Desktop enforced controls / overall readiness | **UNKNOWN**; no general compatibility PASS |
| Recovered Full Task independent review | **PENDING / UNVERIFIED**; reusable packet retained, no Completion |
| New Desktop behavior verification | **NOT_RUN**; existing Codex assertions were inspected only |
| Windows and Linux | Unverified |
| Qoder CLI and Qoder IDE | Outside required V0 scope; historical NOT_RUN records are not converted to PASS |

The [validation summary](VALIDATION.md) distinguishes deterministic tests,
retained actual Codex observations and unverified Desktop capabilities. Raw
private records are not published; the summary is not a substitute for those raw
records or a claim that new live runs occurred on this relocated snapshot.

## Use and retention

Use [Codex manual entry](hosts/codex.md). The
[Desktop guide](hosts/qoder-desktop.md) records the two actual minimum
observations and the reusable manual procedure with its remaining limitations.
Neither requires an installer, host core fork, personal AI framework,
global configuration change or credential transfer.

Task records remain in the user's own worktree and outside commits. Upgrades
select an explicit new kit path while preserving user edits and prior evidence;
removal stops manual loading and preserves task records. Git publishing and
business acceptance remain the owner's separate decisions.

## License

Original contributions use [MIT](../LICENSE). Bundled third-party MIT and
Apache-2.0 notices retain their original terms; see [SOURCES](../SOURCES.md).
