# Standards corrections

- Use the current Core Web Vitals thresholds from web.dev: LCP at or below 2.5 seconds, INP at or below 200 milliseconds, and CLS at or below 0.1. Evaluate field results at the 75th percentile, segmented by mobile and desktop; lab data is diagnostic, not real-user proof.
- Do not repeat the subgrid page's claim that Chromium support is still in development. Current platform documentation reports interoperable modern-browser support; verify target browsers rather than freezing version tables into the skill.
- Do not recommend `translateZ(0)`, `will-change`, or layer promotion as universal performance fixes. Animate transform and opacity when they satisfy the interaction, measure rendering cost, and add `will-change` briefly only when evidence justifies it.
- Do not treat `requestIdleCallback` as a universal long-task scheduler. Use deadline-aware scheduling, `scheduler.yield()` where available, task chunking, or a measured fallback, and preserve responsiveness over throughput.
- Do not preload resources merely because they are important in general. Preload only current-navigation resources discovered too late, include correct `as`/CORS metadata, and confirm the hint changes the critical path.
Primary checks: MDN CSS guides and web.dev Core Web Vitals and optimization articles. design.dev remains the requested topic and observed-tool coverage source.
