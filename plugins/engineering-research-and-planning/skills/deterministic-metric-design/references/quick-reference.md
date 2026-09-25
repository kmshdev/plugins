# Quick reference

### 1. Construct Definition & Operationalization (CRITICAL)

- [`def-name-the-latent-construct`](./def-name-the-latent-construct.md) — Name the unobservable property before writing any formula
- [`def-separate-construct-from-proxy`](./def-separate-construct-from-proxy.md) — Keep construct, proxy, and their assumed link distinct
- [`def-write-falsifiable-operational-definition`](./def-write-falsifiable-operational-definition.md) — Specify the exact procedure that yields the number
- [`def-fix-unit-of-analysis`](./def-fix-unit-of-analysis.md) — Pin the unit of analysis and the measurement boundary
- [`def-anchor-to-the-decision`](./def-anchor-to-the-decision.md) — Attach the decision and action threshold the metric drives
- [`def-operationalize-behavior-and-size`](./def-operationalize-behavior-and-size.md) — Define "behavior" (≈) and "size" so a formatter can't move them

### 2. Computability & Tractability (CRITICAL)

- [`comp-do-not-define-metric-as-uncomputable-ideal`](./comp-do-not-define-metric-as-uncomputable-ideal.md) — Don't define the metric as Kolmogorov complexity
- [`comp-respect-rices-theorem-for-semantic-properties`](./comp-respect-rices-theorem-for-semantic-properties.md) — Use sound approximations for undecidable semantic facts
- [`comp-choose-a-decidable-observational-equivalence`](./comp-choose-a-decidable-observational-equivalence.md) — Replace undecidable equivalence with a checkable ≈
- [`comp-design-a-proxy-with-a-proven-error-direction`](./comp-design-a-proxy-with-a-proven-error-direction.md) — Give the proxy a sound bound that never over-states
- [`comp-keep-the-metric-tractable`](./comp-keep-the-metric-tractable.md) — Pick a near-linear proxy, not an NP-hard optimum
- [`comp-bound-approximation-error-explicitly`](./comp-bound-approximation-error-explicitly.md) — Quantify and report the proxy↔ideal gap
- [`comp-prefer-monotone-confluent-transformations`](./comp-prefer-monotone-confluent-transformations.md) — Confluent, terminating rewrites give a unique fixed point

### 3. Measurement-Theoretic Foundations (HIGH)

- [`meas-declare-the-scale-type`](./meas-declare-the-scale-type.md) — Declare nominal/ordinal/interval/ratio before any statistic
- [`meas-only-admissible-statistics`](./meas-only-admissible-statistics.md) — Use only statistics invariant under the scale's transforms
- [`meas-establish-meaningful-zero-and-unit`](./meas-establish-meaningful-zero-and-unit.md) — Give a true zero and a named unit for ratio claims
- [`meas-preserve-the-empirical-relation`](./meas-preserve-the-empirical-relation.md) — Verify the metric orders known anchor cases correctly
- [`meas-avoid-ad-hoc-weighted-sums`](./meas-avoid-ad-hoc-weighted-sums.md) — Don't sum incommensurable scales with arbitrary weights

### 4. Proof of Metric Properties (HIGH)

- [`prop-prove-monotonicity`](./prop-prove-monotonicity.md) — Prove the score moves the right way when the construct does
- [`prop-prove-invariance-under-irrelevant-transforms`](./prop-prove-invariance-under-irrelevant-transforms.md) — Prove invariance to renaming and formatting
- [`prop-ensure-sensitivity-to-relevant-change`](./prop-ensure-sensitivity-to-relevant-change.md) — Ensure it still discriminates (no saturation)
- [`prop-check-weyuker-briand-axioms`](./prop-check-weyuker-briand-axioms.md) — Check the published axioms for your measure type
- [`prop-prove-boundedness-and-handle-empty`](./prop-prove-boundedness-and-handle-empty.md) — Prove the range; define the empty / zero-denominator case
- [`prop-prove-or-disclaim-composability`](./prop-prove-or-disclaim-composability.md) — Prove additivity before aggregating, or refuse to sum

### 5. Determinism & Reproducibility (HIGH)

- [`det-make-the-metric-a-pure-function`](./det-make-the-metric-a-pure-function.md) — No hidden time, network, or global state
- [`det-pin-iteration-and-tie-break-order`](./det-pin-iteration-and-tie-break-order.md) — Sort by a total key; seed any randomness
- [`det-pin-the-input-representation`](./det-pin-the-input-representation.md) — Fix exactly which representation (AST stage) you measure
- [`det-control-floating-point-and-accumulation`](./det-control-floating-point-and-accumulation.md) — Fix summation order and rounding precision
- [`det-version-and-record-the-toolchain`](./det-version-and-record-the-toolchain.md) — Emit metric version, tool versions, and input hash

### 6. Construct Validity & Calibration (MEDIUM-HIGH)

- [`valid-converge-with-accepted-measure`](./valid-converge-with-accepted-measure.md) — Show convergence with a trusted measure of the construct
- [`valid-discriminant-not-just-loc`](./valid-discriminant-not-just-loc.md) — Prove incremental signal beyond LOC / size
- [`valid-predictive-validity-against-outcome`](./valid-predictive-validity-against-outcome.md) — Show it predicts the real outcome out-of-sample
- [`valid-beat-the-trivial-baseline`](./valid-beat-the-trivial-baseline.md) — Quote the lift over a dumb baseline
- [`valid-calibrate-thresholds-to-ground-truth`](./valid-calibrate-thresholds-to-ground-truth.md) — Derive thresholds from data, not round numbers
- [`valid-validate-out-of-sample`](./valid-validate-out-of-sample.md) — Use a holdout / temporal split to avoid overfitting the corpus

### 7. Optimization Safety & Anti-Gaming (MEDIUM)

- [`game-make-cheapest-improvement-the-right-one`](./game-make-cheapest-improvement-the-right-one.md) — Make the cheapest score gain the genuine one
- [`game-recognize-goodhart-variants`](./game-recognize-goodhart-variants.md) — Anticipate regressional / extremal / causal Goodhart
- [`game-pair-with-guardrail-metrics`](./game-pair-with-guardrail-metrics.md) — Add counter-metrics that veto a regressing "win"
- [`game-hard-block-construct-violating-wins`](./game-hard-block-construct-violating-wins.md) — Gate on invariants; never use a tradable soft penalty
- [`game-detect-reward-hacking-with-audits`](./game-detect-reward-hacking-with-audits.md) — Spot-audit top scores; watch proxy↔outcome drift

### 8. Aggregation, Reporting & Adoption (LOW-MEDIUM)

- [`agg-respect-scale-in-aggregation`](./agg-respect-scale-in-aggregation.md) — Aggregate the way the scale permits (no mean of ordinal)
- [`agg-report-uncertainty-not-false-precision`](./agg-report-uncertainty-not-false-precision.md) — Report intervals / bounds, not false precision
- [`agg-version-the-metric-publicly`](./agg-version-the-metric-publicly.md) — Semver + changelog so consumers stay comparable
- [`agg-ship-reference-impl-and-test-vectors`](./agg-ship-reference-impl-and-test-vectors.md) — Publish test vectors so implementations agree
