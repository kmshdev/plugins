# Version and native integration

Use this reference for a dependency upgrade, native-versus-custom architecture
decision, or proposed framework workaround. Skip it for unrelated edits.

## Establish the dependency boundary

Record the requested target, resolved Nautilus packages, Rust version, features
and registry/git/path overrides. Check registry metadata when asked for the latest
release. A shared version label does not make a published crate, source checkout
and project fork identical. Preserve the application's lockfile unless changing
dependencies is part of the task.

Use official documentation for intended composition and compiler-visible
declarations, callers and relevant tests for exact behavior. Make conflicts
explicit; do not select whichever source justifies the proposed implementation.

## Check the native path before extending it

Trace the affected path through input, actor/data delivery, Strategy,
risk/execution, state, persistence and lifecycle as applicable. Do not inspect
unrelated subsystems or add an application-owned replacement for a native owner.

Before adding a parallel service, vendored crate or framework patch, check native
configuration, extension points and the requested released version. If a defect
remains, retain a minimal reproducer, separate application policy from framework
behavior, and explain the smallest correction, source identity and removal
condition. A missing setting or incorrectly wired lifecycle is not proof that
the framework needs a patch.

## Complete the requested boundary

For implementation requests, continue from diagnosis through the local change
and meaningful checks. For review or proposal requests, report findings or the
proposal without making unrequested changes. Reuse passing checks for unchanged
code; a new phase alone does not require another broad suite.

Finish when the requested artifact or behavior is delivered and applicable
checks pass. Report unrelated failures and unverified physical boundaries.
If authorization, credentials, entitlement or an unresolved product decision
blocks a required action, name that blocker and the exact input needed. Complete
independent authorized work first. A command, example or plugin never grants
permission for provider purchases, broker sessions, deployment or publication.
