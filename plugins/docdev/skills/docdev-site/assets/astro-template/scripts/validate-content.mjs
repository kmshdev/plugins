import { readdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";
import settings from "../docdev.config.mjs";

const root = resolve(process.cwd(), settings.contentDir);

async function collect(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map((entry) => {
    const path = resolve(directory, entry.name);
    if (entry.isDirectory()) return collect(path);
    return entry.isFile() && entry.name.endsWith(".mdx") ? [path] : [];
  }));
  return nested.flat().sort();
}

function frontmatter(text, path) {
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  if (!match) throw new Error(`${path}: missing leading MDX frontmatter`);
  return Object.fromEntries(match[1].split(/\r?\n/).flatMap((line) => {
    const field = line.match(/^([a-z][a-z0-9_-]*):\s*(.*)$/);
    if (!field) return [];
    return [[field[1], field[2].replace(/^"|"$/g, "")]];
  }));
}

const files = await collect(root);
if (files.length === 0) throw new Error(`No MDX files found under ${root}`);

const owners = new Map();
for (const path of files) {
  const data = frontmatter(await readFile(path, "utf8"), path);
  if (!data.slug) throw new Error(`${path}: missing slug`);
  if (owners.has(data.slug)) {
    throw new Error(`Duplicate docdev slug "${data.slug}": ${owners.get(data.slug)} and ${path}`);
  }
  owners.set(data.slug, path);
}

console.log(`validated ${files.length} unique MDX route(s)`);
