import { startFixtureServer } from "./fixture-server.mjs";

const port = Number(process.env.CSS_TOKENOGRAPHY_FIXTURE_PORT ?? "4173");
if (!Number.isInteger(port) || port < 1 || port > 65_535) {
  process.stderr.write("CSS_TOKENOGRAPHY_FIXTURE_PORT must be an integer from 1 to 65535\n");
  process.exitCode = 2;
} else {
  const server = await startFixtureServer({ port });
  process.stdout.write(`${server.origin}\n`);

  const close = async () => {
    await server.close();
    process.exit(0);
  };
  process.once("SIGINT", close);
  process.once("SIGTERM", close);
}
