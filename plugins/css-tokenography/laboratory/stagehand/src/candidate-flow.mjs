const PROTOCOL = "css-tokenography-stagehand-candidates/v1";
const FORBIDDEN_TOP_LEVEL_KEYS = new Set(["release", "coverage", "baselines", "browserReport"]);

function schemaError(message) {
  return new TypeError(`Invalid Stagehand candidate document: ${message}`);
}

function nonEmpty(value, name) {
  if (typeof value !== "string" || value.trim() === "") throw schemaError(`${name} must be a non-empty string`);
}

export function candidateFlowDocument({ generatedAt, candidates }) {
  if (!Array.isArray(candidates) || candidates.length === 0) {
    throw schemaError("candidates must contain at least one candidate flow");
  }
  const ids = new Set();
  const normalized = candidates.map((candidate, index) => {
    if (!candidate || typeof candidate !== "object") throw schemaError(`candidates[${index}] must be an object`);
    nonEmpty(candidate.id, `candidates[${index}].id`);
    nonEmpty(candidate.fixture, `candidates[${index}].fixture`);
    nonEmpty(candidate.goal, `candidates[${index}].goal`);
    if (ids.has(candidate.id)) throw schemaError(`candidates[${index}].id must be unique`);
    ids.add(candidate.id);
    if (!Array.isArray(candidate.steps) || candidate.steps.length === 0 || !candidate.steps.every((step) => typeof step === "string" && step.trim())) {
      throw schemaError(`candidates[${index}].steps must contain non-empty strings`);
    }
    return Object.freeze({
      id: candidate.id,
      fixture: candidate.fixture,
      goal: candidate.goal,
      steps: [...candidate.steps],
      requiresHumanReview: true,
      promotion: "candidate-only",
    });
  });

  return Object.freeze({
    protocol: PROTOCOL,
    generatedAt,
    experimental: true,
    authority: "candidate-only",
    candidates: normalized,
  });
}

export function validateCandidateDocument(document) {
  if (!document || typeof document !== "object") throw schemaError("document must be an object");
  for (const key of FORBIDDEN_TOP_LEVEL_KEYS) {
    if (key in document) throw schemaError(`${key} cannot be emitted by Stagehand`);
  }
  if (document.protocol !== PROTOCOL) throw schemaError(`protocol must equal ${PROTOCOL}`);
  if (document.experimental !== true || document.authority !== "candidate-only") {
    throw schemaError("document must remain experimental and candidate-only");
  }
  nonEmpty(document.generatedAt, "generatedAt");
  return candidateFlowDocument(document);
}

export { PROTOCOL };
