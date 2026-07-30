import manifest from "../../../references/browser-fixtures.json" with { type: "json" };

export const ENGINES = Object.freeze(["chromium", "firefox", "webkit"]);

const assertionsById = Object.freeze({
  "gradient-runtime": [{ path: "computed.backgroundImage", includes: "linear-gradient" }, { path: "layout.target.width", equals: 320 }],
  "transform-runtime": [{ path: "computed.transform", notEquals: "none" }, { path: "layout.target.width", greaterThan: 100 }],
  "filter-runtime": [{ path: "computed.filter", includes: "blur(" }],
  "backdrop-filter-runtime": [{ path: "computed.backgroundColor", includes: "rgba" }],
  "grid-runtime": [{ path: "computed.display", equals: "grid" }, { path: "layout.named.first.x", lessThan: "layout.named.second.x" }],
  "subgrid-runtime": [{ path: "computed.display", equals: "grid" }],
  "flexbox-runtime": [{ path: "computed.display", equals: "flex" }, { path: "layout.named.first.x", lessThan: "layout.named.second.x" }, { path: "flexLines.0", lessThan: "flexLines.2" }],
  "stacking-hit-test-runtime": [{ path: "hitTest.targetId", equals: "top-layer" }],
  "selector-matching-runtime": [{ path: "selectors.matching", equals: ["match-a", "match-c"] }],
  "feature-detection-runtime": [{ path: "features.cssGrid", equals: true }, { path: "features.flexbox", equals: true }],
});

function fixture(row) {
  const filename = row.fixture.replace("laboratory/browser/fixtures/", "");
  return Object.freeze({
    id: row.id,
    owner: row.owner,
    claimIds: row.claim_ids,
    path: `/fixtures/${filename}`,
    collectors: row.collectors,
    requiredEngines: row.required_engines,
    visualBaseline: row.visual_baseline,
    assertions: assertionsById[row.id] ?? [],
  });
}

/**
 * The browser layer deliberately asserts portable mechanics and retains feature
 * support values as observations. It never converts a known engine difference
 * (for example backdrop-filter support) into a made-up universal claim.
 */
export const FIXTURES = Object.freeze(manifest.map(fixture));

export function fixtureById(id) {
  return FIXTURES.find((fixtureDefinition) => fixtureDefinition.id === id);
}
