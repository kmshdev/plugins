# Standards corrections

- The color contrast CLI implements only WCAG 2.2 relative-luminance color-pair thresholds. Thresholds use the full-precision ratio while `display_ratio` is rounded separately; a displayed `4.50:1` can therefore remain below the `4.5:1` AA boundary. The result is not a page or product conformance claim. APCA is not implemented: it is beta and polarity-sensitive, and it is not a WCAG 3 conformance method. See the [official APCA project documentation](https://git.apcacontrast.com/documentation/) and the current [WCAG 3 Working Draft](https://www.w3.org/TR/wcag-3.0/).
- Use the current Core Web Vitals thresholds from web.dev: LCP at or below 2.5 seconds, INP at or below 200 milliseconds, and CLS at or below 0.1. Evaluate field results at the 75th percentile, segmented by mobile and desktop; lab data is diagnostic, not real-user proof.
- Do not repeat the subgrid page's claim that Chromium support is still in development. Current platform documentation reports interoperable modern-browser support; verify target browsers rather than freezing version tables into the skill.
- Do not recommend `translateZ(0)`, `will-change`, or layer promotion as universal performance fixes. Animate transform and opacity when they satisfy the interaction, measure rendering cost, and add `will-change` briefly only when evidence justifies it.
- Do not treat `requestIdleCallback` as a universal long-task scheduler. Use deadline-aware scheduling, `scheduler.yield()` where available, task chunking, or a measured fallback, and preserve responsiveness over throughput.
- Do not preload resources merely because they are important in general. Preload only current-navigation resources discovered too late, include correct `as`/CORS metadata, and confirm the hint changes the critical path.

## Phase 2 bounded standards differences

- The numeric tools implement deterministic arithmetic and CSS serialization
  from explicit inputs. They do not read computed styles: PX/REM requires the
  caller's root size, and aspect-ratio output does not predict the used size of
  a box. Integral aspect ratios are reduced exactly; non-integral inputs retain
  binary64 precision rather than inventing a rational source value.
- nth-child parsing follows the CSS Syntax An+B token boundaries, including
  ASCII digits and CSS whitespace. The generator accepts only An+B plus one
  safe type or universal selector token; the broader `of <complex-real-selector-list>`
  form belongs to selector matching and is intentionally outside this input
  contract. Cubic-bezier enforces x coordinates in `[0,1]` while allowing finite
  y overshoot, as required by CSS Easing.
- The gradient model is a bounded CSS Images subset. It requires at least two
  stops and omits two-position stops, transition hints, `calc()`, explicit
  radial radii, numeric center positions, functional colors, and explicit
  interpolation-space or hue-path controls. Its report names CSS Images 4's
  current Oklab default as a draft semantic that still requires target-browser
  verification.
- The OKLCH converter accepts only six/eight-digit sRGB hex and performs the CSS
  Color 4 conversion without gamut mapping or clamping. It reports powerless
  hue separately at `C <= 0.000004`; conversion output is not rendered-color or
  accessibility-conformance evidence.
- Border-radius accepts one to four primitive nonnegative length-percentage
  values per axis. Box-shadow requires every typed layer to state `inset`, both
  offsets, blur, spread, and color even where CSS text syntax permits omitted
  components and defaults. `calc()`, `var()`, global keywords, functional colors,
  and newer length units outside the shared bounded grammar are not modeled.
- The Flexbox model intentionally stops before the browser layout algorithm.
  Logical axes do not establish physical directions without writing mode and
  direction; line breaking, intrinsic sizing, free-space distribution, growth,
  shrinkage, and computed item sizes remain browser-dependent. Gap accepts only
  `normal` or the shared primitive nonnegative length-percentage grammar.

Primary checks: MDN CSS guides and web.dev Core Web Vitals and optimization articles. design.dev remains the requested topic and observed-tool coverage source.
