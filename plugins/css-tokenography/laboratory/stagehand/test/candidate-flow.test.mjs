import assert from "node:assert/strict";
import test from "node:test";

import { candidateFlowDocument, validateCandidateDocument } from "../src/candidate-flow.mjs";
import { stagehandLiveConfig } from "../src/stagehand-observer.mjs";

test("Stagehand output is explicit candidate-only evidence", () => {
  const document = candidateFlowDocument({
    generatedAt: "2026-07-30T00:00:00.000Z",
    candidates: [{ id: "stagehand-candidate-1", fixture: "grid", goal: "Inspect grid", steps: ["Observe the grid"] }],
  });

  assert.equal(document.authority, "candidate-only");
  assert.equal(document.candidates[0].requiresHumanReview, true);
  assert.equal(document.candidates[0].promotion, "candidate-only");
});

test("Stagehand output cannot carry release evidence", () => {
  const document = {
    ...candidateFlowDocument({
      generatedAt: "2026-07-30T00:00:00.000Z",
      candidates: [{ id: "stagehand-candidate-1", fixture: "grid", goal: "Inspect grid", steps: ["Observe the grid"] }],
    }),
    release: { status: "passed" },
  };

  assert.throws(() => validateCandidateDocument(document), /release cannot be emitted/);
});

test("Stagehand live discovery requires an explicit experimental opt-in before import or browser use", () => {
  assert.throws(() => stagehandLiveConfig({}), /CSS_TOKENOGRAPHY_STAGEHAND_EXPERIMENT=1 is required/);
});
