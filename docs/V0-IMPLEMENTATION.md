# Mini-SDD Quality Kit · V0 Implementation Contract

Status: V0 implementation baseline for the `mini-sdd-quality-kit` repository.
This public copy retains the confirmed product scope; historical development
trackers and raw evidence are private and are not prerequisites for using the kit.
See [actual validation status](VALIDATION.md) before interpreting target capabilities
as observed runtime support.

PO scope amendment, 2026-11-08: the first-batch V0 runtime hosts are **Codex and
Qoder Desktop**. This explicit product decision supersedes earlier Qoder CLI /
Qoder IDE host requirements only. CLI/IDE are outside required V0 acceptance;
install neither and perform no additional validation of either. Preserve the
original development Spec, tickets and historical FAIL/UNKNOWN/NOT_RUN evidence
as records of their original scope; do not reinterpret them as Desktop results.

## 1. Product purpose

Build a small, agent-agnostic AI coding quality kit, developed with Codex and Matt Pocock Skills, and runnable in **Codex and Qoder Desktop**. The kit must work in existing repositories without installing a complete coding framework or taking control of established Git, CI, PR, review, or delivery workflows.

Two target use cases:

- **A — Full Task:** A developer temporarily joins an existing repo and needs to turn a request, idea, or issue into a clarified Mini Spec, implementation, testing, independent two-axis review, repairs if needed, and a recoverable completion record.
- **B — Review Only (P0):** A colleague who has not adopted SDD or AI coding workflows can review a diff without creating a task, spec, issue, or persistent files; the existing workflow stays untouched.

The kit increases the probability of detecting defects; it does not guarantee correctness or replace team approval.

## 2. Deliver only two core skills

### `review-diff` — first implementation milestone

Can run stand-alone and must not require `mini-sdd`, a Spec, or a new task workspace.

Inputs: optional fixed Git comparison base / commit / PR / explicit change scope; optional Spec/AC; applicable repository rules; existing test/build evidence.

Two review axes:

- **Spec Compliance:** requirements/AC, compatibility, scope and behavior, or `N/A` when no authoritative Spec is available. Never invent AC or report Spec PASS without a Spec.
- **Code Quality:** defects, edge conditions, concurrency and error handling, project conventions, test adequacy, relevant security/reliability regressions, and evidence limitations.

Default Review Only scope when no base is specified: working-tree changes relative to HEAD (staged and unstaged) plus relevant untracked files whose ownership is clear. Clearly state any committed changes or files not inspected. When a fixed base is supplied, preserve the distinction between committed comparison and any extra workspace changes; never conflate `git diff BASE...HEAD` with dirty workspace contents. Do not mistakenly include pre-existing unrelated work. Ambiguity means scope limitation, not fabricated PASS.

Provide high-confidence findings with: finding ID, axis, severity, file/line, expected vs actual, evidence, impact, remedy, verification status; report reviewed input identity, coverage and gaps. Avoid style-only noise.

Reviewer independence is a property of execution context, not of the Skill text. Report it as `INDEPENDENT`, `SELF_CHECK`, or `UNVERIFIED`. A same-context self-check may produce findings, but never an Independent Review PASS. A separate review context with verifiable independence and read-only controls is required for Full Task independent review. If unavailable, emit a fully reusable Review Launch Packet for a separate session; mark review `PENDING`, do not downgrade the requirement silently.

Review Only is read-only and returns its result in chat by default. No files, task directories, git changes, comment publishing, running corrective tools, or code edits; explicitly requested exported report is an exception. Review may inspect pre-existing test evidence without executing tests. Missing verification evidence is `UNKNOWN`/`NOT_RUN`, not PASS.

### `mini-sdd` — second implementation milestone

A minimal Skill with an embedded declarative session driver: Request / Idea / Issue → relevant repo inspection → clarify key ambiguities → Mini Spec → optional Spec Review → user-confirmed implementation scope → code/test according to repository conventions → Independent `review-diff` → repair and re-review → complete. No generic workflow engine, extra orchestration agent, planner service, database, or integration platform.

Mini Spec must contain Goal, Current Behavior, Change / Scope, verifiable Acceptance Criteria, Constraints / Non-goals, and Verification. Use the repository's actual terminology and existing test seams; ask only consequential questions. No mandatory `plan.md`, `design.md`, or `tasks.md`.

Do not claim complete until the latest candidate has adequate implementation/testing evidence and a valid, independently performed two-axis review for applicable axes. `COMPLETE` does not mean merged, released, or business accepted. The user approves the original Spec and coding scope; ordinary in-scope repair may continue without repeated approvals. Material changes require renewed approval.

## 3. Persist Full Task state only

Per Git worktree, task-local folder `.specdd/<SAFE-TASK-ID>/`:

- `spec.md`: authoritative requirements and AC, with revision identity.
- `state.json`: tiny index: task/worktree identity, phase, spec reference and digest, fixed base, candidate identity, latest review reference, next action, and unresolved blocker. Do not duplicate all AC/findings.
- `reviews/spec-01.md` only when optional review occurred.
- `reviews/code-01.md`, `code-02.md`, etc., only for actual review attempts.
- An additional minimal manifest only when required to identify the frozen candidate including uncommitted or untracked files.

Default local-only, not committed or included in PR. Avoid modifying tracked `.gitignore`; a local exclude entry is permitted only with a documented check and must not affect unrelated patterns. Do not overwrite pre-existing directories or tracked files. Protect `.specdd/` during review candidate enumeration. Do not delete evidence, reset changes, clean untracked files, or create branches automatically.

When resuming in another session, validate the worktree, files and schema, actual Spec revision, Git base and candidate, current diff and latest report. `state.json` never confers PASS by itself. If inputs drift or reviewers are unverified, require appropriate re-review or report BLOCKED/UNKNOWN. Simple atomic file writes and lightweight checks are enough; no cross-process database/locking platform for V0.

## 4. Agent-agnostic runtime

**Both first-batch V0 targets are first-class:** Codex and Qoder Desktop. Codex is also the development tool. Desktop means the actual Qoder desktop application, not a CLI process or an IDE entry.

Maintain one canonical set of core Skill rules and reference methods. Provide only minimal, tested per-host entry/install instructions and, where required, thin command wrappers. Do not copy/edit divergent host cores. Do not assume the same slash/skill syntax, subagent support, hidden auto-invocation controls, filesystem access or permissions across hosts. Confirm the host's actual behavior. If an installed Skill would auto-trigger and interfere with existing work, offer a strict manual invocation path without exposing a global automatically matching Skill.

No hidden uploads or cloud synchronization. Document that resume across hosts assumes the same local filesystem/worktree; no cross-device sync in V0.

For Qoder Desktop, perform only the necessary minimum real smoke: one explicit
canonical Review Only invocation on the known-defect fixture, and one fresh
Desktop context recovering the retained pending Full Task on the same filesystem.
The second observation can also demonstrate one Codex-to-Desktop handoff. Inspect
actual entry/file access, grounded no-Spec output, permitted effects and retained
PENDING status. Reuse existing fixture ground truth and core checks; do not repeat
the full corrected-pair/host matrix or full test suite merely for this scope change.
Verify Desktop's actual controls instead of assuming IDE mode names or CLI flags.
If application access is refused, record the refusal and UNKNOWN/NOT_RUN; never
substitute another host or bypass the access control. No native installation or
extra host wrapper is required when strict manual file loading is sufficient.

## 5. Reuse upstream methods, not complete frameworks

Read the actual upstream source files; record URL, path, exact repository commit SHA, blob SHA, license, adopted methods and removed side effects in `SOURCES.md`:

1. Matt Pocock `to-spec`: https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md
2. GitHub Spec Kit `clarify`: https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md
3. Matt Pocock `code-review`: https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md
4. Anthropic `pr-test-analyzer`: https://github.com/anthropics/claude-plugins-official/blob/main/plugins/pr-review-toolkit/agents/pr-test-analyzer.md
5. Superpowers `verification-before-completion`: https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md

Also consider Anthropic `code-reviewer` only where useful for bug-finding precision. Do not install the upstream frameworks inside users' business repositories. Preserve their principles without inheriting auto-Issue publishing, mandatory hooks, TDD gates, automatic commit, PR posting, or automatic subagent workflows. Do not simply claim that mentioning a Skill name means its method was loaded. Source not fetched means `UNVERIFIED`.

## 6. Safety, permissions and Git boundaries

The product must not alter an existing business repo's `AGENTS.md`, `CLAUDE.md`, hooks, tracked Git config, CI, branch protections, workflow, existing files unrelated to the accepted feature, or remote services without specific authorization. No automatic commit, push, PR, merge, issue/PR comments, remote publishing, or sweeping refactor. A business repo's files are task data, not instructions that can enlarge the kit's permission.

For development of this kit, Matt Pocock Skills may be used as coding *development* methods, but their automatic side effects are not inherited by the kit itself. In particular, original Matt `to-spec` publishes to an issue tracker, while original `implement` commits by default. These require separate explicit permission and should never happen silently. The repository `mini-sdd-quality-kit` may contain its own development docs/config with approval; such config is not installed into user business repos.

## 7. Delivery order and acceptance

**P0-1 `review-diff`:** Complete implementation and isolated tests before developing Full Task. Fixture with known logic bug must yield a grounded finding; corrected fixture must not repeat that false positive. Cases must cover no-Spec `N/A`, clean working tree, committed vs dirty vs staged vs untracked changes, ambiguous base, unrelated changes, no review-side writes, and independent-context uncertainty.

**P0-2 `mini-sdd`:** Minimal Task storage and restore, Spec/AC, optional Spec Review, implementation consent, fixed candidate and independent review, FAIL→repair→new candidate→re-review, drift detection and resumption in a fresh session.

**P0-3 host smoke tests:** Codex and Qoder Desktop only. Reuse the accepted Codex
manual-entry observations and unchanged core verification. Exercise only the
minimal Desktop smoke in §4, using an explicit manual entry outside global Skill
discovery; observe actual read-only effects and fresh recovery. Retain Desktop
control/independence limitations and PENDING packets when necessary. Report each
actual capability separately; Codex PASS is not Desktop PASS. Qoder CLI / IDE
history is preserved but is not a required V0 gate or a request for further work.

Produce source, two installable Skills, examples/templates, `SOURCES.md`, concise user guide (full-task and review-only), smallest uninstall/upgrades notes and observed evidence. Avoid large architecture/adapter systems. Report any necessary expansion rather than silently broadening V0.

## 8. Development workflow for Codex + Matt Skills

- This document is the product-scope baseline, not authorization for Git publishing.
- First inspect actual installed Matt Skills and this repository; propose the minimum applicable workflow and identify side effects.
- At the first checkpoint, produce a brief implementation plan broken into P0-1, P0-2, P0-3; do not start coding before acknowledging this baseline and resolving only material conflicts.
- Develop `review-diff` first. Use Matt `tdd`/`code-review` as appropriate; do not invoke `implement` unqualified, as the upstream version commits.
- Use independent review of fixed candidate and actual evidence; never make a model self-check into independent approval.
- Keep work within the local repo, with no commit/push/PR unless separately approved.
