function preflightError(message) {
  return new Error(`Stagehand experimental preflight failed: ${message}`);
}

function requireEnv(env, name) {
  if (typeof env[name] !== "string" || env[name].trim() === "") {
    throw preflightError(`${name} must be set`);
  }
  return env[name];
}

function requireProviderCredential(env, model) {
  const provider = model.split("/", 1)[0];
  const credentials = {
    anthropic: "ANTHROPIC_API_KEY",
    google: "GOOGLE_GENERATIVE_AI_API_KEY",
    openai: "OPENAI_API_KEY",
  };
  if (!credentials[provider]) {
    throw preflightError("CSS_TOKENOGRAPHY_STAGEHAND_MODEL must use an anthropic, google, or openai provider");
  }
  requireEnv(env, credentials[provider]);
}

export function stagehandLiveConfig(env = process.env) {
  if (env.CSS_TOKENOGRAPHY_STAGEHAND_EXPERIMENT !== "1") {
    throw preflightError("CSS_TOKENOGRAPHY_STAGEHAND_EXPERIMENT=1 is required");
  }
  const baseUrl = requireEnv(env, "CSS_TOKENOGRAPHY_STAGEHAND_BASE_URL");
  const model = requireEnv(env, "CSS_TOKENOGRAPHY_STAGEHAND_MODEL");
  let parsedBaseUrl;
  try {
    parsedBaseUrl = new URL(baseUrl);
  } catch {
    throw preflightError("CSS_TOKENOGRAPHY_STAGEHAND_BASE_URL must be an absolute URL");
  }
  if (!new Set(["http:", "https:"]).has(parsedBaseUrl.protocol)) {
    throw preflightError("CSS_TOKENOGRAPHY_STAGEHAND_BASE_URL must use http:// or https://");
  }
  requireProviderCredential(env, model);
  return Object.freeze({ baseUrl: parsedBaseUrl, model });
}

/**
 * This is intentionally an isolated, manually invoked experimental adapter.
 * It returns observations for conversion to candidate-only JSON; it has no
 * import path to browser reports, coverage, baselines, or release decisions.
 */
export async function discoverWithStagehand({ fixture, goal, env = process.env }) {
  if (typeof fixture !== "string" || fixture.trim() === "") throw preflightError("fixture must be a non-empty string");
  if (typeof goal !== "string" || goal.trim() === "") throw preflightError("goal must be a non-empty string");
  const config = stagehandLiveConfig(env);
  const { Stagehand } = await import("@browserbasehq/stagehand");
  const stagehand = new Stagehand({ env: "LOCAL", model: config.model });
  try {
    await stagehand.init();
    const page = stagehand.context.pages()[0];
    await page.goto(new URL(`/fixtures/${fixture}.html`, config.baseUrl).toString());
    const actions = await stagehand.observe(goal);
    return [{
      fixture,
      goal,
      actions: actions.map((action) => action.description ?? String(action)),
    }];
  } finally {
    await stagehand.close();
  }
}
