# Source methods

The five adopted methods below record immutable upstream commit, source blob and
license identities. Bundled license files and attribution notices are part of the
public package. Original development receipts and raw runtime captures remain in
the private development archive and are intentionally not distributed.

The development source audit rechecked upstream source/license bytes on 2026-11-07.
The public packaging check verifies bundled license blob identities and preserves
all core source bytes; it is not a new network fetch or independent proof of an
earlier actor's reading chronology. Source URLs below permit separate inspection.
Installed Skill names alone establish neither loading nor adoption.

## Matt Pocock code-review

- Repository: <https://github.com/mattpocock/skills>.
- Repository commit SHA: `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`.
- Source path: `skills/engineering/code-review/SKILL.md`.
- [Pinned source URL](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/code-review/SKILL.md).
- Source blob SHA: `83183e0ad36fd0eef25d37c7e483284b7e34c1f0`.
- License: MIT; copyright 2026 Matt Pocock.
- License path: `LICENSE`; blob SHA `f1dd2c09108dde1a5f56097cee8461b3ea834499`.
- [Pinned license](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/LICENSE).
- [Included license notice](skills/review-diff/references/licenses/mattpocock-MIT.txt).
- Adopted methods: identify actual scoped inputs, keep requirements and quality
  concerns separate, prioritize repository conventions, and ground findings.
- Adaptation: product axes are Spec Compliance and Code Quality, with no-Spec
  `N/A`, explicit coverage limits, and execution-based independence labels.
- Removed side effects: mandatory issue/spec-reference lookup, mandatory Git
  comparison for an explicit whole-file request, and automatic parallel reviewer
  dispatch. The pinned code-review source does not publish issues; issue publication
  is removed from to-spec below. Development review remains separate from product behavior.

## Anthropic pr-test-analyzer

- Repository: <https://github.com/anthropics/claude-plugins-official>.
- Repository commit SHA: `0412be76f50ab4f4f8abff3753efa9269fbbca5b`.
- Source path: `plugins/pr-review-toolkit/agents/pr-test-analyzer.md`.
- [Pinned source URL](https://github.com/anthropics/claude-plugins-official/blob/0412be76f50ab4f4f8abff3753efa9269fbbca5b/plugins/pr-review-toolkit/agents/pr-test-analyzer.md).
- Source blob SHA: `05b342b9175af85c5d7404bac67f5c62da375aa2`.
- License: Apache-2.0, verified at the plugin's own license path. Its blob matches
  the repository-root license at the same pinned commit.
- License path: `plugins/pr-review-toolkit/LICENSE`; blob SHA
  `d645695673349e3947e8e5ae42332d0ac3164cd7`.
- [Pinned plugin license](https://github.com/anthropics/claude-plugins-official/blob/0412be76f50ab4f4f8abff3753efa9269fbbca5b/plugins/pr-review-toolkit/LICENSE).
- [Included license](skills/review-diff/references/licenses/anthropic-Apache-2.0.txt).
- Adopted methods: assess behavioral coverage, important error paths and edge
  cases, regression value, test brittleness, and cost/benefit rather than a line
  coverage target or trivial-test checklist.
- Removed side effects: PR-created/updated/pre-merge activation assumptions,
  standalone analyzer-agent dispatch, mandatory 1–10 rating, and prescribed
  upstream report headings. Review Only inspects existing evidence and runs no
  tests, builds, analyzers, or corrective tools.

## Matt Pocock to-spec

- Repository: <https://github.com/mattpocock/skills>.
- Repository commit SHA: `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`.
- Source path: `skills/engineering/to-spec/SKILL.md`.
- [Pinned source](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/to-spec/SKILL.md).
- Source blob SHA: `3f52599ae2a4347aee5a07432c2707518e691a7f`.
- License: MIT, copyright 2026 Matt Pocock; `LICENSE` blob
  `f1dd2c09108dde1a5f56097cee8461b3ea834499`.
- [Pinned license](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/LICENSE),
  [included notice](skills/mini-sdd/references/licenses/mattpocock-MIT.txt).
- Adopted methods (condensed): repository-informed synthesis, actual repository
  terminology, existing public verification seams and testable scope. The core
  does not retain the upstream explicit glossary/ADR inspection procedure.
- Removed side effects: issue publication, triage labels, setup requirements,
  exhaustive story-list format and mandatory issue-tracker storage. Mini SDD
  uses six concise sections, explicit consent and local task-only records.

## GitHub Spec Kit clarify

- Repository: <https://github.com/github/spec-kit>.
- Repository commit SHA: `c43849408ac0de2ca6a52f14eaae71449776057b`.
- Source path: `templates/commands/clarify.md`.
- [Pinned source](https://github.com/github/spec-kit/blob/c43849408ac0de2ca6a52f14eaae71449776057b/templates/commands/clarify.md).
- Source blob SHA: `f48d8bd703d7eb3fe4eadf2d3d283ca508e6bb80`.
- License: MIT, copyright GitHub, Inc.; `LICENSE` blob
  `28a50fa22639e32febe14e4ffc7a732b0ba8c90a`.
- [Pinned license](https://github.com/github/spec-kit/blob/c43849408ac0de2ca6a52f14eaae71449776057b/LICENSE),
  [included notice](skills/mini-sdd/references/licenses/spec-kit-MIT.txt).
- Adopted methods (condensed): prioritize consequential unanswered questions,
  incorporate accepted answers, and use verifiable, consistent scope. The full
  upstream ambiguity taxonomy and coverage-scan procedure are not retained.
- Removed side effects: extension hook discovery and execution, prerequisite
  scripts, mandatory Spec Kit layout, fixed question quota, checklist machinery,
  planning handoffs and framework setup. No upstream plugin is activated.

## Superpowers verification-before-completion

- Repository: <https://github.com/obra/superpowers>.
- Repository commit SHA: `22f0b463e7a5e579904dd6211a520321035526f7`.
- Source path: `skills/verification-before-completion/SKILL.md`.
- [Pinned source](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/verification-before-completion/SKILL.md).
- Source blob SHA: `7d45333cc4a49c57a80df6c1fe2fa777a207afbc`.
- License: MIT, copyright 2025 Jesse Vincent; `LICENSE` blob
  `abf0390320aa14406af7a520b9b0739fdda9bf08`.
- [Pinned license](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/LICENSE),
  [included notice](skills/mini-sdd/references/licenses/superpowers-MIT.txt).
- Adopted methods: identify an appropriate check before a claim, execute it,
  inspect actual output/exit status and requirements, retain unverified gaps,
  and verify delegated results rather than trust success assertions.
- Adaptations/removals: actual manual/static evidence is valid according to AC
  and risk; no mandatory repeated full suite per message, universal test mandate,
  framework install/enable, automatic commit, push or PR workflow is inherited.

## Not adopted

Anthropic `code-reviewer` is `NOT_ADOPTED`; its content was not fetched in the development
source receipts and its provenance remains `UNVERIFIED`. No upstream framework or plugin
was installed or enabled by this source verification.
