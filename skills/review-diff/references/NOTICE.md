# Method attribution

This Skill is a changed adaptation of methods from:

- Matt Pocock, `code-review`, MIT. Pinned source:
  <https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/code-review/SKILL.md>.
  Retains scoped, separate review axes and project-convention priority; replaces
  issue lookup and mandatory parallel reviewers with the Review Only contract.
  [MIT license and copyright notice](licenses/mattpocock-MIT.txt).
- Anthropic, `pr-test-analyzer`, Apache-2.0. Pinned source:
  <https://github.com/anthropics/claude-plugins-official/blob/0412be76f50ab4f4f8abff3753efa9269fbbca5b/plugins/pr-review-toolkit/agents/pr-test-analyzer.md>.
  Retains behavior-focused, risk-relevant test-gap analysis; removes PR lifecycle
  activation, mandatory scoring, and upstream output/workflow requirements.
  [Apache-2.0 license](licenses/anthropic-Apache-2.0.txt).

The adaptation adds explicit whole-file scope, input identity, no-Spec `N/A`,
read-only and no-execution controls, honest verification/independence labels,
grounded report fields, and chat-only output. It neither installs nor invokes the
upstream frameworks. Full provenance and source verification are indexed by the
kit's root source record; the bundled notices travel with this Skill folder.
