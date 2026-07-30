import { expect, test } from "@playwright/test";
import { collect } from "../../src/collectors.mjs";
import { verifyAssertions } from "../../src/contract.mjs";
import { FIXTURES } from "../../src/fixtures.mjs";
import { startFixtureServer } from "../../src/fixture-server.mjs";

let server;
test.beforeAll(async () => { server = await startFixtureServer(); });
test.afterAll(async () => { await server.close(); });

for (const fixture of FIXTURES) {
  test(`${fixture.id} retains deterministic observations`, async ({ page }) => {
    await page.route("**/*", (route) => route.request().url().startsWith(server.origin) ? route.continue() : route.abort());
    await page.goto(server.urlFor(fixture.path));
    const observation = await collect(page, fixture.collectors);
    expect(verifyAssertions(observation, fixture.assertions)).toEqual([]);
    await expect(page).toHaveScreenshot(`${fixture.id}.png`, { animations: "disabled", caret: "hide", scale: "css" });
  });
}
