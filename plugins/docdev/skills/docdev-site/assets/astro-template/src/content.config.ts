import { resolve } from "node:path";
import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";
import settings from "../docdev.config.mjs";

const docs = defineCollection({
  loader: glob({
    base: resolve(process.cwd(), settings.contentDir),
    pattern: "**/*.{md,mdx}",
  }),
  schema: z.object({
    title: z.string().min(1),
    summary: z.string().min(1),
    type: z.enum(["development", "plan", "architecture", "library"]),
    status: z.enum(["draft", "review", "approved", "deprecated"]),
    slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
    created: z.coerce.date(),
    updated: z.coerce.date(),
    audience: z.array(z.string()).min(1),
    owners: z.array(z.string()),
    tags: z.array(z.string()),
    evidence: z.array(z.string()),
  }),
});

export const collections = { docs };
