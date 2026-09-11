# ADR-003: Five independently usable Codex skills

Accepted 2026-09-11. Supersedes the compatibility entry and alias decisions in
[ADR-001](001-portable-skill.md) and [ADR-002](002-five-workflow-plugin.md).

Publish in kmshdev/plugins with `.codex-plugin/plugin.json` and exactly five
child skills. Remove the root SKILL entry and legacy nautilus-rust-v2 alias.
Each child includes its own references, evidence, examples and UI assets; copying
one child does not require the plugin or a source checkout. Canonical resources
are maintained centrally and materialized by the checked generator.

The Rust API baseline is 0.63.0; the Codex build version may carry a cache-busting
suffix. Instructions encourage short compile/run cycles and selective evidence,
not repeated broad audits. Current build evidence belongs in [BUILD-LOG](../BUILD-LOG.md).
