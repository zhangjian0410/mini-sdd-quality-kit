# Qoder Desktop: bounded observations and limitations

V0 targets Codex and Qoder Desktop. On 2026-11-08, G3 completed both minimum
Desktop observations on public candidate `a9c0f986df93511c10d97ab2195670f4708ab905`:
explicit canonical Review Only and fresh inspection-only recovery of a
Codex-produced Full Task on the same filesystem/worktree.

The real line-4 defect was found, but an extra finding described an unperformed
hypothetical repair: G3 report precision is **FAIL**. Bounded recovery and unchanged
fixture/Git/task effects are **PASS**. Enforced read-only controls and overall
readiness remain **UNKNOWN**; the actual permission setting was automatic
approval. Independent review stays **PENDING / UNVERIFIED**; new Desktop behavior
verification is **NOT_RUN**. These observations do not grant general Desktop
compatibility or complete V0 acceptance. See [validation](../VALIDATION.md).

After G5 minimally hardened the grounding rule and fixture acceptance, G6 ran
one fresh Review Only task on `490d6084e5fa6e2cd3a630add1427fb61b3ef262` with
the identical G3 prompt/fixture and the same model UI setting. This single
precision observation **PASS**: one real High finding; the hypothetical repair
risk appeared only as advice outside findings/count/severity. Fixture/Git/task
maps and product/Git snapshots were unchanged. Automatic approval remained
active, so enforced read-only controls remain **UNKNOWN**. Independence stays
**UNVERIFIED**, reviewed-code behavior verification **NOT_RUN**, and general
readiness **UNKNOWN**. G3 FAIL is preserved; no corrected-pair or Full Task
recovery rerun occurred. Details and evidence limits are in
[G5/G6 validation](../VALIDATION.md#g5-grounding-hardening-and-g6-single-precision-recheck).

Earlier development recorded version 0.5.6 metadata and refused application access;
that remains historical evidence, not the G3 result. The app version was not
independently rechecked for G3 or G6. Qoder CLI and Qoder IDE are outside required
V0 acceptance; their historical NOT_RUN records remain unchanged in the private
archive. No additional CLI/IDE installation or validation is required.

## Conditional manual entry

Use only when normal Desktop application and file access are available. Keep the
complete kit outside native Skill-discovery folders. Both canonical sibling
Skills, references, helpers and license notices stay together. Native commands,
auto-triggering, UI mode names and enforced read-only controls are unverified;
inspect actual controls rather than assuming CLI flags or IDE conventions.

Use a fresh Desktop context and a disposable authorized fixture. Full Task helpers
need user-provided Python 3.11+ and Git supporting `--no-lazy-fetch`. Nothing in
this guide installs dependencies or changes global host settings.

## Minimum observation procedure

An authorized operator should preserve prompts, actual results, control evidence
and before/after fixture, Git and task file maps outside the reviewed fixture.
Review Only inspects existing evidence and executes no source or tests.

1. Copy the [known-defect example](../../tests/fixtures/logic_bug/pricing.py) into
   an isolated fixture. Replace the paths in this prompt:

   ```text
   Read <KIT>/skills/review-diff/SKILL.md and its report contract explicitly.
   Review only <FIXTURE>/pricing.py as this proposed whole-file change.
   No authoritative Spec is supplied. Return grounded findings in chat.
   Inspect only; do not run tests, source, fixes, or write files/Git/task state.
   State actual coverage, N/A Spec Compliance, NOT_RUN behavior verification
   and honest independence/control limitations.
   ```

   Check for the actual `len(prices - 1)` bug at line 4, canonical finding fields
   and read-only effects. Reuse the fixture ground truth; no full host matrix is
   needed for this minimum observation.

2. Prepare an explicitly authorized disposable Codex Full Task using the
   [manual guide](codex.md) and canonical procedure. Retain a genuine PENDING
   Review Launch Packet with its Spec, consent, candidate and evidence. In a
   genuinely fresh Desktop context on the same filesystem/worktree, load
   `mini-sdd` explicitly and request inspection-only resume without
   `--update-state`. Verify the actual records and current diff, preserve PENDING
   and the next separate review action. This can test fresh recovery and one
   Codex-to-Desktop handoff together. No private development fixture is required.

A new chat or read-only instruction alone does not prove enforced independence.
If controls or provenance cannot be verified, retain the reusable packet and
PENDING. Record NOT_RUN or UNKNOWN for unavailable observations. Neither this
procedure nor Codex observations grant general Desktop PASS. The G3 run followed
this minimum scope; it did not rerun the complete host matrix or perform the
separate pending review. Local observer notes are UI transcriptions; terminal
accessibility output truncation and unaudited hook effects outside fixtures are
disclosed in the validation summary.

## Upgrade and removal

Select the kit path explicitly, preserving prior versions and user edits. Changed
packet inputs require current validation. Stop manual use by ceasing to load the
files; preserve task records, evidence and unrelated Desktop/workspace settings.
