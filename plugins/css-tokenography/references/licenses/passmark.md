# Passmark license and adoption decision

- Source: <https://github.com/bug0inc/passmark>
- Pinned package: `passmark@1.0.16`
- Upstream revision: `c5f30a48673f10b78c648202305a9231395476ec`
- npm publication date: `2026-06-08`
- Repository license: `FSL-1.1-ALv2`
- Package-manifest license string: `FSL-1.1-Apache-2.0`
- Future license for this release: Apache-2.0, effective `2028-06-08`
- Adoption: `approved-internal-use-only`

The user approved Passmark only for internal regression testing in this
marketplace repository. This decision does not approve use in a competing
commercial product or service, redistribution of a modified copy, or broader
organizational use. The upstream `LICENSE.md` terms remain authoritative over
the shorter package-manifest label.

Passmark stays outside the dependency-free plugin runtime. Its optional
laboratory must use synthetic local pages, disable telemetry by default, fail
closed on model disagreement, and keep CUA and video modes explicitly opt-in.
Model credentials, Redis, recordings, traces, and cached steps must never be
stored in the plugin or committed to the repository.

`npm audit --json` on 2026-07-30 reported 38 transitive findings in the pinned
workspace: 31 moderate and 7 high, with no critical findings. This is an
accepted, visible risk for the optional internal-use boundary, not evidence
that the dependency is safe for default execution. The workspace remains
excluded from required deterministic CI and must be re-audited before any
broader adoption.
