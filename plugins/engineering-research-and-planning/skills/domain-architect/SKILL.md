---
name: domain-architect
description: Map business domains and vertical slices in a Swift codebase to guide restructuring.
---

# Domain Architect

You discover business domains by tracing what users can DO — the
product's capabilities — and mapping each capability to a vertical
slice through the architecture.

You do NOT start from folder names, architecture docs, or file counts.
You start from the product.

## What You Produce

A **domain map** — the single artifact that drives everything else:

```
Domain Map
├── Business Domains (vertical slices the user would recognize)
│   └── Per domain: Types, Config clients, Service reducers, UI views
├── Providers (external SDK bridges)
├── Cross-Cutting Concerns (Infra, Utils)
└── Questions (ambiguous boundaries to discuss with the team)
```

Once the domain map is right, folder structure, SPM targets, enforcement
specs, and migration plans all follow mechanically. Get the domains wrong
and everything downstream is wrong.

## How Domains Work

Read `references/architecture.md` for the full layer spec.
Read `references/architecture.als` for the formally verifiable model.

### A domain is a user capability

**Litmus test**: Can you describe it to a non-engineer in one sentence?

- "Scheduling appointments" — domain (Calendar)
- "Collecting payments" — domain (Payments)
- "Browsing available treatments" — domain (Treatments)
- "Handling HTTP requests" — NOT a domain (infrastructure)
- "Formatting dates" — NOT a domain (utils)

### Each domain owns a vertical slice

```
Types    → pure data definitions for this domain's nouns
Config   → @DependencyClient interfaces (what you can ask for)
Repo     → implementations (how it's done — API, persistence, sync)
Service  → @Reducer state machines (business decisions)
Runtime  → dependency wiring (Config interfaces → Repo implementations)
UI       → SwiftUI views (pixels)
```

Not every domain needs every layer. A thin domain might only have
Config + Service + UI. But Types, Config, and Service are the minimum
for something to be a real domain.

### Domains don't import each other's internals

Cross-domain communication happens through:
- Delegate actions to a parent reducer
- Shared Types (the universal vocabulary)
- Shared Config interfaces (when two domains use the same client)

Never by importing another domain's Service or Repo.

### What's NOT a domain

| Thing | What it is | Where it lives |
|-------|-----------|---------------|
| Error handling | Cross-cutting | Infra |
| Logging/telemetry | Cross-cutting | Infra |
| Formatters, constants | Cross-cutting | Utils |
| Sentry, Stripe SDK, APNS | Provider (SDK bridge) | Providers |
| HTTP transport, persistence engine | Shared infrastructure | Repo |
| Design system tokens | Shared UI | DesignSystem |
| Background task scheduling | Platform integration | Runtime |

---

For the discovery sequence, output format, and depth checks, read [the mapping workflow](references/workflow.md) when producing a domain map.
