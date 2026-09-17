# ADR-003: Independently usable Codex workflow skills

Accepted 2026-09-11. Supersedes the compatibility entry and alias decisions in
[ADR-001](001-portable-skill.md) and [ADR-002](002-five-workflow-plugin.md).

Publish in kmshdev/plugins with `.codex-plugin/plugin.json` and named child
skills. The original acceptance had five; the 2026-09-17 scope amendment adds
`deploying-nautilus-runs` as a sixth workflow for persistent run delivery and
CI/CD. It does not add a root router or a custom subagent pipeline.
Remove the root SKILL entry and legacy nautilus-rust-v2 alias.
Each child includes its own references, evidence, examples and UI assets; copying
one child does not require the plugin or a source checkout. Canonical resources
are maintained centrally and materialized by the checked generator.

## Version baseline — amended 2026-09-17

The 2026-09-11 acceptance used Rust API 0.63.0. This amendment supersedes that
version baseline: the maintained plugin targets **NautilusTrader 0.64.0**, with
bundled examples pinned to `=0.64.0` and requiring Rust 1.98.1 or newer. The
independent-resource packaging decision above remains unchanged.

Existing applications retain their lockfiles, features and source overrides
unless an upgrade is requested; follow [version and native integration](../references/version-and-integration.md).
The Codex build version may carry a cache-busting suffix. Instructions encourage
short compile/run cycles and selective evidence, not repeated broad audits.
Current build evidence belongs in [BUILD-LOG](../BUILD-LOG.md); historical
qualification receipts retain the versions they actually tested.
