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
- nth-child parsing follows the [CSS Syntax An+B microsyntax](https://www.w3.org/TR/css-syntax-3/#anb-microsyntax),
  including ASCII digits and CSS whitespace. The generator accepts only An+B
  plus one safe type or universal selector token; Selectors defines the broader
  [`:nth-child(An+B [of S]?)`](https://www.w3.org/TR/selectors-4/#the-nth-child-pseudo)
  form, which is intentionally outside this generator's input contract.
  Cubic-bezier enforces x coordinates in `[0,1]` while allowing finite y
  overshoot, matching [CSS Easing's cubic Bézier grammar](https://www.w3.org/TR/css-easing-2/#cubic-bezier-easing-functions).
- The gradient model is a bounded [CSS Images gradient](https://www.w3.org/TR/css-images-4/#gradients)
  subset. It requires at least two stops although the normative
  [color-stop list](https://www.w3.org/TR/css-images-4/#color-stop-syntax)
  accepts one or more, and it omits two-position stops, transition hints,
  `calc()`, explicit radial radii, numeric center positions, functional colors,
  and explicit interpolation-space or hue-path controls. Its report names the
  current [Oklab gradient-interpolation default](https://www.w3.org/TR/css-images-4/#coloring-gradient-line)
  as a draft semantic that still requires target-browser verification.
- The OKLCH converter accepts only six/eight-digit sRGB hex and performs the CSS
  Color 4 [Oklab-to-OkLCh conversion](https://www.w3.org/TR/css-color-4/#lab-to-lch)
  without gamut mapping or clamping. It reports hue as powerless at
  `C <= 0.000004`, the threshold in the normative
  [OkLCh syntax table](https://www.w3.org/TR/css-color-4/#specifying-oklab-oklch),
  following the [powerless-component rule](https://www.w3.org/TR/css-color-4/#powerless).
  Conversion output is not rendered-color or accessibility-conformance
  evidence.
- Border-radius accepts one to four primitive nonnegative length-percentage
  values per axis, matching the [border-radius shorthand grammar](https://www.w3.org/TR/css-backgrounds-3/#border-radius).
  Box-shadow requires every typed layer to state `inset`, both offsets, blur,
  spread, and color even where the [box-shadow grammar](https://www.w3.org/TR/css-backgrounds-3/#box-shadow)
  permits omitted components and defaults; it preserves the specified
  [front-to-back shadow order](https://www.w3.org/TR/css-backgrounds-3/#shadow-layers).
  `calc()`, `var()`, global keywords, functional colors, and newer length units
  outside the shared bounded grammar are not modeled.
- The Flexbox model intentionally stops before the browser layout algorithm.
  Its [main and cross axes](https://www.w3.org/TR/css-flexbox-1/#box-model) do not
  establish physical directions without writing mode and direction, and it
  reports [order-modified document order](https://www.w3.org/TR/css-flexbox-1/#order-property)
  separately from source order. Line breaking, intrinsic sizing, free-space
  distribution, growth, shrinkage, and computed item sizes remain
  browser-dependent. Gap accepts only `normal` or the shared primitive
  nonnegative length-percentage grammar defined for
  [row and column gutters](https://www.w3.org/TR/css-align-3/#column-row-gap).

Phase 2 normative claims use the W3C sections linked inline. Other primary
checks are MDN CSS guides and web.dev Core Web Vitals and optimization articles;
design.dev remains the requested topic and observed-tool coverage source.
