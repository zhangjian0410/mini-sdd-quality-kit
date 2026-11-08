# Issue tracker: GitHub

Development issues and specs live in this repository's GitHub Issues.
Use the gh CLI; infer the repository from git remote -v.

## Conventions

- Read: gh issue view <number> --comments --json number,title,body,labels,comments
- List: gh issue list --state open --json number,title,body,labels
- Create: gh issue create --title "..." --body-file <file>
- Comment: gh issue comment <number> --body-file <file>
- Label: gh issue edit <number> --add-label "..." / --remove-label "..."
- Close: gh issue close <number> --comment "..."

Use body files for multiline content. See triage-labels.md for triage roles.
Development specs must reference docs/V0-IMPLEMENTATION.md.
GitHub Issues are separate from the product's local .specdd/ Full Task records.

## Skill operations

"Publish to the issue tracker" means create a GitHub issue.
"Fetch the relevant ticket" means read the issue and its comments.
Remote mutations require authorization covering the action.

## Pull requests as a triage surface

PRs as a request surface: no.
