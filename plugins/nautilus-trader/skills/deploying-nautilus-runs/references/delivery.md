# Reusable delivery without implicit deployment

## Scaffold an existing runner

The helper is optional Python standard-library tooling, not a Python trading
runtime. Templates can also be copied manually. It refuses an existing output
directory, so inspect and merge files into an existing project deliberately.

```sh
python3 scripts/scaffold.py init --output ./run-delivery --package my-strategy --binary my-runner
python3 scripts/scaffold.py plan --output ./run-plan.json --mode backtest --image registry.example/runner@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --catalog-uri /data/input --artifact-root /data/output
```

The example digest illustrates syntax, not an existing/published image. Use the
actual built image digest before execution. Planning allocates a fresh run and
attempt UUID and writes no database, bucket or infrastructure. Its JSON must be
mapped by the application as described in [run architecture](guide.md).

The overlay contains an OCI Dockerfile, local PostgreSQL/Redis Compose services,
a reusable GitHub Actions build workflow, and an application run-registry schema.
The binary/manifest/feature choices must match the target package. The workflow
tests and builds; it does **not** push images or deploy. Review any copied workflow
before enabling it in a repository. A Docker build still executes the target
package's build scripts and may fetch dependencies.

The Compose file is a local integration fixture, not a managed-cloud deployment.
It publishes no database ports and isolates storage on a private network. Redis
is unauthenticated only within this disposable private fixture. Use authenticated,
encrypted managed-service connections for a real cloud target. PostgreSQL requires
an explicit secret. Services and volumes are started only on user authorization;
no generated file automatically runs migrations.

## Provider-neutral run contract

Build once and promote the immutable image digest. For every independent run,
allocate one task/container/process with its own node and native instance ID;
set parallelism to one and automatic retry to zero until recovery semantics are
qualified. A scheduler may run multiple isolated backtests, not multiple copies
of the same live account writer. The application consumes the run plan explicitly;
container environment variables alone do not configure Nautilus.

Map the same contract to the user's selected platform, rather than introducing
an orchestrator they do not use:

| Platform | Finite backtest | Long-running live run | Storage |
| --- | --- | --- | --- |
| AWS | Batch job or ECS task | Controlled ECS service/task ownership | PostgreSQL, managed Redis-compatible cache, S3 |
| Azure | Container Apps Job or existing batch runner | Container Apps/VM service with exclusive ownership | PostgreSQL, managed Redis-compatible cache, Blob/ADLS |
| GCP | Cloud Run Job or Batch task | Appropriate continuously running service/VM | Cloud SQL PostgreSQL, managed Redis, GCS |
| Existing Kubernetes | Job with `parallelism: 1`, `completions: 1`, `backoffLimit: 0` | Explicit single-owner rollout/recovery | Existing managed services and object storage |

These are design mappings, not verified provider command recipes. Check current
platform limits, termination behavior, networking and workload-identity support
when the target is selected. Do not put a broker loop into a request handler or
assume a request-serving/serverless timeout is suitable for a persistent node.

## CI/CD boundaries

1. CI: validate application config, exact dependency/features, build and focused
   offline native/storage tests. Retain lockfile and image/source identifiers.
2. Authorized integration: disposable PostgreSQL/Redis and catalog readback,
   including crash/partial-artifact behavior. Never reuse a production database
   for a convenient test. Schema initialization is a separate migration stage.
3. Release: explicit image registry destination and authorization; inject a scoped
   identity at runtime. Keep build permissions separate from deployment permissions.
4. Deploy: require the selected environment/account approval before migrations,
   paid jobs, cloud writes or broker connectivity. Review the actual plan/diff.
5. Accept: match expected inputs, runs and economic outcomes; verify persistence
   and native shutdown. Keep incomplete/failed runs distinguishable and exit the
   loop on unavailable access, unresolved recovery policy or failed validation.

Retain source/lock/config/input digests, run/node IDs, log/artifact pointers and
readback outcomes. Upload only allowlisted non-secret artifacts; do not archive
environment dumps, credentials, complete workspace contents or unrelated data.
