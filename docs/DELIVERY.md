# Public source delivery

This snapshot contains exactly two canonical Skills, their Python 3.11+
standard-library helpers, references and third-party notices, plus tests and
portable documentation. Keep the sibling Skill directories together. Start with
[README](../README.md); the [V0 contract](V0-IMPLEMENTATION.md) defines intended
behavior, and [SOURCES](../SOURCES.md) records pinned third-party provenance.

This public tree is derived from development `main` at
`2f09ce38993548a5030d55b58603c84bd2a0d282`. All core Skill and test files retain
that revision's exact bytes. Public documentation was adapted to remove private
archive dependencies. The new Git repository has independent initial history;
original development commits, task records, host captures, personal configuration
and authentication are excluded.

The source snapshot is public on the repository's `main` branch. The current
[snapshot identity](../SNAPSHOT.json) prepares **v0.1.0-alpha.1** as the first
GitHub Pre-release, pending final approval. Its version is `0.1.0-alpha.1`, with
planned Tag `v0.1.0-alpha.1`; no Tag or GitHub Release has been created.
The development source revision above remains unchanged. Public source availability
and alpha preparation do not claim a stable release or fully validated V0 runtime
support. Runtime observations and limitations below retain their existing verdicts.

## Runtime status

| Host or capability | Observed status |
|---|---|
| Codex on macOS, strict manual loading | Actual review and Full Task/recovery observations; bounded support only |
| Codex native catalog installation and native subagent policy | NOT_RUN / unverified |
| Qoder Desktop | UNKNOWN / NOT_RUN; metadata alone is not compatibility proof |
| Windows and Linux | Unverified |
| Qoder CLI and Qoder IDE | Outside required V0 scope; historical NOT_RUN records are not converted to PASS |

The [validation summary](VALIDATION.md) distinguishes deterministic tests,
retained actual Codex observations and unverified Desktop capabilities. Raw
private records are not published; the summary is not a substitute for those raw
records or a claim that new live runs occurred on this relocated snapshot.

## Use and retention

Use [Codex manual entry](hosts/codex.md). The
[Desktop guide](hosts/qoder-desktop.md) is a conditional procedure awaiting actual
validation. Neither requires an installer, host core fork, personal AI framework,
global configuration change or credential transfer.

Task records remain in the user's own worktree and outside commits. Upgrades
select an explicit new kit path while preserving user edits and prior evidence;
removal stops manual loading and preserves task records. Git publishing and
business acceptance remain the owner's separate decisions.

## License

Original contributions use [MIT](../LICENSE). Bundled third-party MIT and
Apache-2.0 notices retain their original terms; see [SOURCES](../SOURCES.md).
