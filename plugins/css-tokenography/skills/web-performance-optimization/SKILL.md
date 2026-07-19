---
name: web-performance-optimization
description: Measure, diagnose, budget, and improve web loading, responsiveness, visual stability, rendering, resource delivery, caching, real-user monitoring, and regression risk. Use for Core Web Vitals, Lighthouse or RUM analysis, performance budgets, image/font delivery, long tasks, third-party scripts, and progressive enhancement.
---

# Web performance optimization

## Evidence hierarchy

1. Treat field data at the 75th percentile, segmented by mobile and desktop, as user-experience evidence.
2. Use lab traces to reproduce and diagnose, not to claim real-user success.
3. Record device, network, cache state, route, build, and collection tooling with every result.
4. Separate missing evidence from passing evidence.

## Core thresholds

- LCP: good at or below 2500 ms.
- INP: good at or below 200 ms.
- CLS: good at or below 0.1.

## Workflow

1. Establish a baseline and a page/interaction-specific budget.
2. Trace LCP discovery, request priority, server response, resource load, and render delay. Add preconnect/preload/fetch priority only when the waterfall proves discovery or priority is the problem.
3. Trace INP through input delay, handler work, and presentation delay. Break long tasks, reduce DOM/layout work, yield deliberately, and move suitable computation off the main thread.
4. Trace CLS sources, reserve media/advertising space, stabilize font metrics, and avoid inserting content above existing content.
5. Reduce CSS/JavaScript/image/font payloads from coverage and transfer evidence. Serve responsive images and appropriate modern formats; do not add codecs implicitly.
6. Choose cache headers and service-worker strategies by freshness semantics. Avoid caching personalized or rapidly changing responses as static assets.
7. Budget third-party scripts by bytes, requests, main-thread cost, privacy, and business owner. Delay or remove scripts whose value does not justify their cost.
8. Respect reduced-data, reduced-motion, battery/mobile constraints, and progressive enhancement.
9. Add RUM and regression monitoring with release/build attribution; keep lab and field dashboards distinct.

## Performance-budget CLI

Run `python3 scripts/performance_budget.py --input report.json --format json`. The analyzer accepts normalized `metrics`/`resources`, Lighthouse `audits`, or `web_vitals` JSON. Default budgets cover LCP, CLS, INP, JavaScript/CSS/image/font/total bytes, total requests, and third-party requests. Exit codes: `0` pass, `1` malformed input, `2` budget failure, `3` incomplete evidence. Use `--budget` for explicit overrides.

Collection is intentionally separate. Detect Lighthouse/browser tooling before collection, never download it implicitly, and report an unavailable collector as a blocker.

## Corrections

Do not preserve deprecated FID workflows, unconditional `requestIdleCallback`, stale support tables, universal `translateZ(0)`, or unconditional `will-change`. Primary sources: https://web.dev/articles/vitals and the optimization articles linked from it. Topic source: https://design.dev/guides/web-performance-optimization/.
