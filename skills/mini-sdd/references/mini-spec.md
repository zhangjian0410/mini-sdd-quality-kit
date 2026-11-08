# Mini Spec format

Use this structure for the authoritative `spec.md`. Fill it from the request,
accepted conversation and inspected repository facts. Headings name the public
record format; concise content is sufficient. A revision identifies this exact
agreement; its SHA-256 binds the actual bytes.

```markdown
# <Task goal>
Revision: 1

## Goal
<User-visible result and reason.>

## Current Behavior
<Observed behavior, relevant source and existing public test seams.>

## Change / Scope
<Accepted behavior and boundaries.>

## Acceptance Criteria
<Observable success, relevant error/edge behavior and compatibility.>

## Constraints / Non-goals
<Preserved workflow, compatibility and excluded work.>

## Verification
<Appropriate actual automated, manual or static checks and unresolved limits.>
```

State unresolved consequential questions before asking the user to approve.
Do not invent an answer, duplicate all findings into state, or require a separate
plan.md, design.md or tasks.md.
