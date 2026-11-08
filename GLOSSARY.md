# Mini-SDD Quality Kit

Terms from the confirmed [V0 product baseline](docs/V0-IMPLEMENTATION.md) and
accepted design clarifications.

## Language

**Review Only**:
A standalone, read-only review of a defined change scope. It requires no Full Task
or Mini Spec and returns its result in chat unless an export is explicitly requested.

**Full Task**:
A coding task that carries an agreed Mini Spec through implementation, verification,
independent review, repairs and a recoverable completion record.

**Mini Spec**:
The authoritative description of a Full Task's goal, current behavior, change scope,
acceptance criteria, constraints and verification.

**Review Candidate**:
The identified version of the changes and relevant inputs examined in a review.
It includes in-scope uncommitted and untracked files when those are part of the changes.

**Spec Compliance**:
The review axis that assesses changes against authoritative requirements and
acceptance criteria. It is not applicable when no authoritative Spec is available.

**Code Quality**:
The review axis that assesses defects, edge conditions, project conventions,
test adequacy and relevant security or reliability regressions.

**Independent Review**:
A review performed in a separate context with verifiable independence and read-only
controls. A check performed in the implementation context is a self-check.

**Review Launch Packet**:
A reusable set of review inputs prepared for a separate review session when an
independent review cannot be performed in the current environment.

**Verification Evidence**:
Observed results from automated tests, actual manual behavior checks or applicable
static checks, assessed against the acceptance criteria and change risk. Model
inference is distinguishable from these actual verification results.

**Blocking Finding**:
A confirmed finding that violates an applicable acceptance criterion or identifies
a material behavioral, security or reliability defect introduced by the task's
changes. It prevents Completion until repaired and re-reviewed.

**Completion**:
The state reached when the latest Full Task candidate meets the agreed local
implementation, verification and independent review conditions, with no unresolved
Blocking Findings. It does not imply closure of an associated Issue, merge,
release or business acceptance.
