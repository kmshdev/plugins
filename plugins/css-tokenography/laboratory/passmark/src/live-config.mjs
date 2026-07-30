import net from "node:net";

const REQUIRED_MODEL_ENV = [
  "CSS_TOKENOGRAPHY_PASSMARK_STEP_EXECUTION_MODEL",
  "CSS_TOKENOGRAPHY_PASSMARK_ASSERTION_PRIMARY_MODEL",
  "CSS_TOKENOGRAPHY_PASSMARK_ASSERTION_SECONDARY_MODEL",
  "CSS_TOKENOGRAPHY_PASSMARK_UTILITY_MODEL",
];

function preflightError(message) {
  return new Error(`Passmark live preflight failed: ${message}`);
}

function isEnabled(value) {
  return value === "1";
}

function requireEnv(env, name) {
  if (typeof env[name] !== "string" || env[name].trim() === "") {
    throw preflightError(`${name} must be set`);
  }
  return env[name];
}

function requireGatewayCredentials(env, gateway) {
  if (gateway === "none") {
    requireEnv(env, "ANTHROPIC_API_KEY");
    requireEnv(env, "GOOGLE_GENERATIVE_AI_API_KEY");
  } else if (gateway === "vercel") {
    requireEnv(env, "AI_GATEWAY_API_KEY");
  } else if (gateway === "openrouter") {
    requireEnv(env, "OPENROUTER_API_KEY");
  } else if (gateway === "cloudflare") {
    requireEnv(env, "CLOUDFLARE_ACCOUNT_ID");
    requireEnv(env, "CLOUDFLARE_AI_GATEWAY");
    requireEnv(env, "ANTHROPIC_API_KEY");
    requireEnv(env, "GOOGLE_GENERATIVE_AI_API_KEY");
  } else {
    throw preflightError("CSS_TOKENOGRAPHY_PASSMARK_GATEWAY must be none, vercel, openrouter, or cloudflare");
  }
}

export function buildLivePassmarkConfig(env = process.env) {
  if (!isEnabled(env.CSS_TOKENOGRAPHY_PASSMARK_LIVE)) {
    throw preflightError("CSS_TOKENOGRAPHY_PASSMARK_LIVE=1 is required");
  }

  const redisUrl = requireEnv(env, "CSS_TOKENOGRAPHY_PASSMARK_REDIS_URL");
  const gateway = requireEnv(env, "CSS_TOKENOGRAPHY_PASSMARK_GATEWAY");
  const baseUrl = requireEnv(env, "CSS_TOKENOGRAPHY_PASSMARK_BASE_URL");
  for (const name of REQUIRED_MODEL_ENV) requireEnv(env, name);
  requireGatewayCredentials(env, gateway);

  const cua = isEnabled(env.CSS_TOKENOGRAPHY_PASSMARK_ENABLE_CUA);
  const video = isEnabled(env.CSS_TOKENOGRAPHY_PASSMARK_ENABLE_VIDEO);
  const telemetry = isEnabled(env.CSS_TOKENOGRAPHY_PASSMARK_ENABLE_TELEMETRY);
  if (!telemetry && (env.AXIOM_TOKEN || env.AXIOM_DATASET)) {
    throw preflightError("telemetry is disabled by default; remove Axiom variables or set CSS_TOKENOGRAPHY_PASSMARK_ENABLE_TELEMETRY=1");
  }
  if (cua) {
    requireEnv(env, "OPENAI_API_KEY");
    if (gateway !== "none") {
      throw preflightError("CUA requires CSS_TOKENOGRAPHY_PASSMARK_GATEWAY=none");
    }
  }
  if (video) requireEnv(env, "GOOGLE_GENERATIVE_AI_API_KEY");

  let redis;
  try {
    redis = new URL(redisUrl);
  } catch {
    throw preflightError("CSS_TOKENOGRAPHY_PASSMARK_REDIS_URL must be a valid redis URL");
  }
  if (!new Set(["redis:", "rediss:"]).has(redis.protocol) || !redis.hostname) {
    throw preflightError("CSS_TOKENOGRAPHY_PASSMARK_REDIS_URL must use redis:// or rediss://");
  }
  let base;
  try {
    base = new URL(baseUrl);
  } catch {
    throw preflightError("CSS_TOKENOGRAPHY_PASSMARK_BASE_URL must be an absolute URL");
  }
  if (!new Set(["http:", "https:"]).has(base.protocol)) {
    throw preflightError("CSS_TOKENOGRAPHY_PASSMARK_BASE_URL must use http:// or https://");
  }

  return Object.freeze({
    baseUrl: base.toString(),
    redis: { host: redis.hostname, port: Number(redis.port || (redis.protocol === "rediss:" ? 6380 : 6379)), secure: redis.protocol === "rediss:" },
    passmark: {
      ai: {
        gateway: cua ? "none" : gateway,
        ...(cua ? { mode: "cua" } : {}),
        models: {
          stepExecution: env.CSS_TOKENOGRAPHY_PASSMARK_STEP_EXECUTION_MODEL,
          assertionPrimary: env.CSS_TOKENOGRAPHY_PASSMARK_ASSERTION_PRIMARY_MODEL,
          assertionSecondary: env.CSS_TOKENOGRAPHY_PASSMARK_ASSERTION_SECONDARY_MODEL,
          utility: env.CSS_TOKENOGRAPHY_PASSMARK_UTILITY_MODEL,
        },
      },
      redis: { url: redisUrl },
      assertions: { consensusPolicy: "fail-on-disagreement" },
      // Omit telemetry credentials unless a caller deliberately enables them.
      ...(telemetry ? { telemetry: { axiomToken: env.AXIOM_TOKEN, axiomDataset: env.AXIOM_DATASET } } : {}),
    },
    options: Object.freeze({ cua, video, telemetry }),
  });
}

export async function preflightRedis(redis, timeoutMs = 2_000) {
  await new Promise((resolve, reject) => {
    const socket = net.createConnection({ host: redis.host, port: redis.port });
    const timer = setTimeout(() => socket.destroy(preflightError("Redis connection timed out")), timeoutMs);
    socket.once("connect", () => {
      clearTimeout(timer);
      socket.end();
      resolve();
    });
    socket.once("error", () => {
      clearTimeout(timer);
      reject(preflightError("Redis is unavailable"));
    });
  });
}
