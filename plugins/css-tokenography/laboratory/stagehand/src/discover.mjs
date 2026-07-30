import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";

import { candidateFlowDocument } from "./candidate-flow.mjs";
import { discoverWithStagehand } from "./stagehand-observer.mjs";

function usage() {
  return "Usage: npm run discover -- --input observations.json\n       npm run discover -- --live --fixture <id> --goal <text>\n\nConverts reviewed Stagehand observations into candidate-only deterministic-flow JSON. The --live mode requires an explicit experimental opt-in. Neither mode changes release status, coverage, or browser baselines.";
}

function parseInputPath(argv) {
  const index = argv.indexOf("--input");
  if (index === -1 || !argv[index + 1]) throw new Error("--input is required");
  return argv[index + 1];
}

function requireArgument(argv, name) {
  const index = argv.indexOf(name);
  if (index === -1 || !argv[index + 1]) throw new Error(`${name} is required with --live`);
  return argv[index + 1];
}

export function candidatesFromObservations(observations) {
  if (!Array.isArray(observations)) throw new TypeError("observations must be an array");
  return observations.map((observation, index) => ({
    id: `stagehand-candidate-${index + 1}`,
    fixture: observation.fixture,
    goal: observation.goal,
    steps: observation.actions,
  }));
}

const invokedAsScript = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;

if (invokedAsScript) {
  if (process.argv.includes("--help")) {
    process.stdout.write(`${usage()}\n`);
  } else {
    try {
      const argv = process.argv.slice(2);
      const observations = argv.includes("--live")
        ? await discoverWithStagehand({
          fixture: requireArgument(argv, "--fixture"),
          goal: requireArgument(argv, "--goal"),
        })
        : JSON.parse(await readFile(parseInputPath(argv), "utf8"));
      const document = candidateFlowDocument({
        generatedAt: new Date().toISOString(),
        candidates: candidatesFromObservations(observations),
      });
      process.stdout.write(`${JSON.stringify(document, null, 2)}\n`);
    } catch (error) {
      process.stderr.write(`Stagehand experimental discovery failed: ${error.message}\n`);
      process.exitCode = 2;
    }
  }
}
