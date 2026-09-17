# Reviewable run-delivery overlay

Generated for Cargo package `@@PACKAGE@@`, binary `@@BINARY@@`. This is an overlay
for an existing Rust application, not a complete trading strategy or deployment.

- Merge `Dockerfile` and `.dockerignore` into the package/workspace build context.
  The image builds the existing locked binary. Qualify extra OS libraries and
  runtime assets required by its adapters; the generic image does not invent them.
  Pass `--build-arg CARGO_FEATURES="your-feature-list"` with the same features
  used by the reusable CI workflow. Empty means no additional package features.
- Review `nautilus-ci.yml` before copying it into `.github/workflows/`. It is a
  reusable `workflow_call` build/test job, with no image push or deployment.
- `compose.yaml` is a local PostgreSQL/Redis fixture with no published database
  ports. Set an explicit `POSTGRES_PASSWORD` without committing it. Do not use
  the unauthenticated private Redis fixture as a public/cloud configuration.
- `run-schema.sql` is an application run-registry migration, not Nautilus's native
  SQL schema. Applying either migration requires an authorized database target.
- Generate `run-plan.json` inside this overlay, supply the effective application
  configuration SHA-256 via `--config-digest`, map it in the runner, and inject runtime
  database/storage credentials explicitly. `RUN_PLAN_PATH` is an application
  convention, not an automatic Nautilus setting. The default image tag is only
  for local builds; use the approved immutable image digest for a real run.

Choose artifact paths visible inside the container (the local volume is `/data`)
or a qualified writable object-store URI. Preserve them after the container exits.
The `run` profile is opt-in; do not start it until the binary's config mapping,
streaming features, migrations, run ownership and shutdown behavior are verified.
No file here starts services, runs migrations, publishes an image or launches a job.
