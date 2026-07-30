import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { createServer } from "node:http";
import { dirname, extname, normalize, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../fixtures");
const CONTENT_TYPES = { ".css": "text/css; charset=utf-8", ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8" };

export function safeFixturePath(requestPath) {
  const cleaned = normalize(requestPath.replace(/^\/+/, ""));
  const candidate = resolve(ROOT, cleaned);
  if (candidate !== ROOT && !candidate.startsWith(`${ROOT}${sep}`)) return null;
  return candidate;
}

export async function startFixtureServer({ port = 0 } = {}) {
  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", "http://localhost");
    if (request.method !== "GET" || url.origin !== "http://localhost" || !url.pathname.startsWith("/fixtures/")) {
      response.writeHead(404).end();
      return;
    }
    const filePath = safeFixturePath(url.pathname.slice("/fixtures/".length));
    if (!filePath) {
      response.writeHead(403).end();
      return;
    }
    try {
      if (!(await stat(filePath)).isFile()) throw new Error("not a file");
      response.writeHead(200, { "Cache-Control": "no-store", "Content-Type": CONTENT_TYPES[extname(filePath)] ?? "application/octet-stream" });
      createReadStream(filePath).pipe(response);
    } catch {
      response.writeHead(404).end();
    }
  });
  await new Promise((resolveServer, reject) => {
    server.once("error", reject);
    server.listen(port, "127.0.0.1", resolveServer);
  });
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("fixture server did not receive a TCP address");
  const origin = `http://127.0.0.1:${address.port}`;
  return {
    origin,
    urlFor: (fixturePath) => new URL(fixturePath, origin).toString(),
    close: () => new Promise((resolveServer, reject) => server.close((error) => (error ? reject(error) : resolveServer()))),
  };
}
