# Review Only report contract

Return a readable report in chat. If the caller or host requests structured
output, express the same information in that format; formatting does not grant
permission to write files or change scope. Only an explicit export request
permits the requested report artifact; preserve an existing destination and
report the collision. The report retains all evidence and independence limits.

## Reviewed input and coverage

- Scope kind: `explicit-files`, `default-workspace` or `fixed-comparison`; actual repository root.
  For default discovery, include observed HEAD, staged/unstaged/untracked layers,
  full layer patch SHA-256 identities, ownership grounds and exclusions. Distinguish an empty
  workspace from a nonempty workspace whose ownership remains unresolved.
- For a fixed comparison, record resolved base, tip and merge-base, committed
  blob/patch identities and the committed range. Keep extra staged, unstaged and
  untracked workspace content and its identities separate; disclose exclusions.
- Selected paths, observed SHA-256 digest of each file, and lines actually read.
  Identify index content separately when it differs from current file content;
  identify deleted content from HEAD/index. Disclose binary or unreadable coverage.
  Report an unavailable digest as unknown rather than inventing it.
- Excluded or uninspected inputs, unavailable comparison history, attribution
  limits, and other coverage gaps. Whole-file review does not establish which
  lines a historical change introduced.

## Axes and execution evidence

- **Spec Compliance:** `N/A` when no authoritative Spec was provided, with the
  reason. For a supplied authoritative Spec, identify the actual source and
  revision or digest, applicable AC and coverage. Use `FINDINGS` for grounded
  violations, `PASS` only for fully supported applicable compliance, and
  `UNKNOWN` for missing or partial evidence. Spec PASS is not test or Independent
  Review PASS; static reading cannot establish runtime AC.
- **Code Quality:** grounded findings, no high-confidence findings in the
  inspected scope, or limited coverage, with a useful summary. These statements
  are not test PASS or a guarantee of correctness.
- **Independence:** `INDEPENDENT`, `SELF_CHECK`, or `UNVERIFIED`, with the evidence
  or limitation supporting that classification. Do not claim independent
  approval from a same-context or unverified review.
- **Verification:** `NOT_RUN` for behavior checks in this review. State which
  pre-existing evidence was available, and separate it from code reading and
  inferred consequences. No test, build, analyzer, or reviewed source is executed.

## Findings

For each high-confidence finding include:

- A distinct finding ID and axis (`Code Quality` or `Spec Compliance`).
- Severity proportional to the concrete impact.
- Selected file and precise line, expected versus actual behavior.
- Observed code evidence and the reasoning supporting the failure path.
- Impact, a practical remedy, and verification status (`NOT_RUN` for a runtime
  reproduction that this review did not perform).

Keep suggestions actionable and avoid style-only noise. If a field or input
cannot be established, disclose the limitation instead of filling it with a
plausible claim. An empty list has no findings to enumerate; do not invent a
placeholder issue just to fill the report.
