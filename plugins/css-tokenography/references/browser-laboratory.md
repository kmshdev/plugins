# Browser and agentic laboratory

The optional laboratory adds runtime evidence without changing the
dependency-free skill CLIs. Use it when a claim depends on computed styles,
layout geometry, selector matching, hit testing, runtime feature support, or
pixels.

## Evidence order

1. Run the owner skill's deterministic CLI and retain its JSON.
2. Run the browser fixture in Chromium, Firefox, and WebKit.
3. Compare computed observations before reviewing screenshots.
4. Run Passmark only for an approved user-flow evaluation.

Browser and agentic evidence cannot turn a deterministic failure into a pass.
Cross-engine disagreement remains visible and blocks universal browser claims.

## Browser runner

The normal runner never installs Node packages or browser binaries:

```bash
python3 scripts/run_browser_lab.py \
  --engines chromium,firefox,webkit \
  --format json
```

If the report is `unavailable`, install the optional workspace and browsers
explicitly from the plugin root:

```bash
npm --prefix laboratory/browser ci
npx --prefix laboratory/browser playwright install chromium firefox webkit
```

Snapshot comparison is the default. Baseline mutation requires the explicit
`--update-snapshots` flag and human review. Generated reports, traces, videos,
and diffs are not plugin source artifacts.

## Passmark

Passmark is pinned only in `laboratory/passmark` for internal-use evaluation.
Its fake contract tests need no credentials. Live runs require pre-existing
model credentials and Redis, use synthetic localhost pages, disable telemetry
by default, and set `consensusPolicy` to `fail-on-disagreement`.

CUA and video modes are opt-in manual evidence. CUA actions are not portable
cache evidence. Video assertions use a single Gemini path and may fall back to
snapshot behavior, so neither mode establishes CSS semantics.

## Stagehand

`laboratory/stagehand` is a separately installed experimental discovery
workspace. It may emit candidate deterministic actions for an unfamiliar flow.
It cannot update coverage, baselines, or release status.
