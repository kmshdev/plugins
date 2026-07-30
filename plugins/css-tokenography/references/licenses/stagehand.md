# Stagehand license and experimental boundary

- Source: <https://github.com/browserbase/stagehand>
- Pinned package: `@browserbasehq/stagehand@3.7.1`
- Declared license: `MIT`
- Adoption: `experimental-discovery-only`

Stagehand may convert unfamiliar interactions into candidate deterministic
flows. It is not a release gate, a CSS semantic oracle, or an alternative
required CI framework. Its workspace is installed and run separately from the
deterministic browser laboratory.

`npm audit --json` on 2026-07-30 reported 18 transitive findings in the pinned
workspace: 16 low, 1 moderate, and 1 high, with no critical findings. This
reinforces the experimental, manual-only boundary.
