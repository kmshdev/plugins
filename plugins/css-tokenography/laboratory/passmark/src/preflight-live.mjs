import { preflightLiveEvaluation } from "./live-runner.mjs";

try {
  await preflightLiveEvaluation();
  process.stdout.write("Passmark live preflight passed. Starting Playwright evaluation.\n");
} catch (error) {
  // Deliberately do not serialize the environment or Redis URL.
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 2;
}
