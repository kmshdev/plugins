# Publishing contract

Local generation and publication are separate authorities. A request to scaffold or
preview does not authorize a commit, push, Pages change, or production deployment.

Before publication:

1. Enumerate the exact output and branch/deployment payload.
2. Allowlist publishable content and assets. Exclude private evidence, absolute paths,
   internal repository metadata, owner-only prose, PII, credentials, and unapproved
   licensed material.
3. Run semantic content review plus secret and license checks; secret scanning alone
   cannot detect proprietary architectural claims.
4. Validate the configured base path and direct navigation to every generated route.
5. Inspect representative mobile and desktop viewports, keyboard traversal, reduced
   motion, console errors, and a production static build.
6. Verify the authenticated repository, target branch, and hosting configuration before
   mutating external state. Never force push.

Report the commit, target, live URL, validation commands, and residual limitations.
