# Feature Specification and Planning

**Version 1.0.0**
Software Engineering
January 2026

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring codebases. Humans may also find it useful,
> but guidance here is optimized for automation and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive feature specification and planning guide for software engineers, product managers, and technical leads. Contains 42 rules across 8 categories, prioritized by impact from critical (scope definition, requirements clarity) to foundational (documentation standards). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct approaches, and specific impact metrics to prevent scope creep and ensure project success.

---

## Table of Contents

1. [Scope Definition](./_sections.md#1-scope-definition) — **CRITICAL**
   - 1.1 [Create Work Breakdown Structure for Complex Features](./scope-work-breakdown.md) — CRITICAL (reduces estimation error by 50%)
   - 1.2 [Define Explicit In-Scope and Out-of-Scope Boundaries](./scope-define-boundaries.md) — CRITICAL (prevents 40% of project failures from scope creep)
   - 1.3 [Define MVP Separately from Full Vision](./scope-define-mvp.md) — CRITICAL (enables faster time-to-value)
   - 1.4 [Document Assumptions and Constraints Early](./scope-document-assumptions.md) — CRITICAL (prevents mid-project surprises and rework)
   - 1.5 [Obtain Stakeholder Sign-off on Scope](./scope-stakeholder-signoff.md) — CRITICAL (prevents scope disputes and rejected deliverables)
2. [Requirements Clarity](./_sections.md#2-requirements-clarity) — **CRITICAL**
   - 2.1 [Maintain Requirements Traceability](./req-traceability.md) — CRITICAL (catches 95% of missing requirements before launch)
   - 2.2 [Separate Functional and Non-Functional Requirements](./req-functional-nonfunctional.md) — CRITICAL (prevents 75% of late-stage NFR surprises)
   - 2.3 [State Requirements Without Prescribing Solutions](./req-avoid-solution-language.md) — CRITICAL (enables optimal technical solutions)
   - 2.4 [Use Consistent Terminology with a Glossary](./req-consistent-terminology.md) — CRITICAL (eliminates cross-team miscommunication)
   - 2.5 [Use User Story Format for Feature Requirements](./req-user-stories.md) — CRITICAL (reduces feature misalignment by 60%)
   - 2.6 [Write Specific and Measurable Requirements](./req-specific-measurable.md) — CRITICAL (reduces interpretation disputes by 80%)
3. [Prioritization](./_sections.md#3-prioritization) — **HIGH**
   - 3.1 [Identify and Prioritize Dependencies](./prio-dependencies-first.md) — HIGH (prevents blocked work and idle teams)
   - 3.2 [Map Features by Value vs Effort](./prio-value-vs-effort.md) — HIGH (focuses 80% of effort on high-value work)
   - 3.3 [Use Kano Model for Customer Satisfaction Prioritization](./prio-kano-model.md) — HIGH (avoids over-investing in features users expect)
   - 3.4 [Use MoSCoW Method for Scope Prioritization](./prio-moscow-method.md) — HIGH (reduces scope disputes by 70%)
   - 3.5 [Use RICE Scoring for Data-Driven Prioritization](./prio-rice-scoring.md) — HIGH (reduces priority disputes by 65%)
4. [Acceptance Criteria](./_sections.md#4-acceptance-criteria) — **HIGH**
   - 4.1 [Avoid Over-Specifying Acceptance Criteria](./accept-avoid-over-specification.md) — HIGH (preserves developer flexibility)
   - 4.2 [Ensure All Criteria Are Testable](./accept-testable-criteria.md) — HIGH (enables objective verification of completion)
   - 4.3 [Establish Definition of Done Beyond Code](./accept-definition-of-done.md) — HIGH (reduces post-launch issues by 60%)
   - 4.4 [Include Edge Cases in Acceptance Criteria](./accept-edge-cases.md) — HIGH (prevents production bugs from untested scenarios)
   - 4.5 [Use Given-When-Then Format for Acceptance Criteria](./accept-given-when-then.md) — HIGH (reduces acceptance ambiguity by 80%)
5. [Stakeholder Alignment](./_sections.md#5-stakeholder-alignment) — **MEDIUM-HIGH**
   - 5.1 [Align on Success Metrics Before Building](./stake-success-metrics.md) — MEDIUM-HIGH (eliminates 90% of post-launch success disputes)
   - 5.2 [Establish Stakeholder Communication Cadence](./stake-communication-plan.md) — MEDIUM-HIGH (reduces stakeholder surprises by 80%)
   - 5.3 [Gather Stakeholder Feedback Early and Often](./stake-early-feedback.md) — MEDIUM-HIGH (reduces late-stage direction changes)
   - 5.4 [Identify All Stakeholders Early](./stake-identify-stakeholders.md) — MEDIUM-HIGH (prevents late-stage surprises from overlooked parties)
   - 5.5 [Resolve Stakeholder Conflicts Explicitly](./stake-conflict-resolution.md) — MEDIUM-HIGH (prevents passive-aggressive scope battles)
6. [Technical Specification](./_sections.md#6-technical-specification) — **MEDIUM**
   - 6.1 [Define API Contracts Before Implementation](./tech-api-contracts.md) — MEDIUM (prevents 70% of integration rework)
   - 6.2 [Document Security Considerations](./tech-security-considerations.md) — MEDIUM (prevents 90% of security review surprises)
   - 6.3 [Document System Context and Dependencies](./tech-system-context.md) — MEDIUM (reduces integration surprises by 60%)
   - 6.4 [Plan Error Handling and Recovery](./tech-error-handling.md) — MEDIUM (reduces production incidents by 50%)
   - 6.5 [Specify Data Models and Schema Changes](./tech-data-model.md) — MEDIUM (reduces database migration failures by 80%)
   - 6.6 [Specify Performance Requirements Upfront](./tech-performance-requirements.md) — MEDIUM (avoids 40% of late-stage performance rewrites)
7. [Change Management](./_sections.md#7-change-management) — **MEDIUM**
   - 7.1 [Assess Full Impact Before Approving Changes](./change-impact-assessment.md) — MEDIUM (prevents 80% of timeline surprises from scope changes)
   - 7.2 [Implement Scope Freeze Periods](./change-scope-freeze.md) — MEDIUM (reduces late-stage changes by 85%)
   - 7.3 [Maintain a Deferred Items Log](./change-defer-log.md) — MEDIUM (captures 100% of good ideas for future consideration)
   - 7.4 [Use Formal Change Request Process](./change-formal-process.md) — MEDIUM (reduces uncontrolled scope growth by 70%)
   - 7.5 [Version All Specification Documents](./change-version-tracking.md) — MEDIUM (eliminates 95% of "which version is current" confusion)
8. [Documentation Standards](./_sections.md#8-documentation-standards) — **LOW**
   - 8.1 [Define Project Terminology in a Glossary](./doc-glossary-terms.md) — LOW (eliminates term confusion across team)
   - 8.2 [Document Key Decisions with Context](./doc-decision-records.md) — LOW (preserves decision rationale for future reference)
   - 8.3 [Keep Documentation Accessible and Searchable](./doc-accessible-format.md) — LOW (reduces information retrieval time by 70%)
   - 8.4 [Maintain Single Source of Truth](./doc-single-source.md) — LOW (eliminates version confusion across team)
   - 8.5 [Use Consistent Document Templates](./doc-consistent-templates.md) — LOW (reduces document creation time by 50%)

---

## References

1. [https://www.wrike.com/project-management-guide/faq/what-is-scope-creep-in-project-management/](https://www.wrike.com/project-management-guide/faq/what-is-scope-creep-in-project-management/)
2. [https://www.atlassian.com/agile/product-management/requirements](https://www.atlassian.com/agile/product-management/requirements)
3. [https://www.scaledagileframework.com/user-stories/](https://www.scaledagileframework.com/user-stories/)
4. [https://www.productplan.com/glossary/rice-scoring-model/](https://www.productplan.com/glossary/rice-scoring-model/)
5. [https://www.karlwiegers.com/requirements-traceability/](https://www.karlwiegers.com/requirements-traceability/)
6. [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/)
7. [https://adr.github.io/](https://adr.github.io/)
8. [https://sre.google/sre-book/service-level-objectives/](https://sre.google/sre-book/service-level-objectives/)

---

## Source Files

This document was compiled from individual reference files. For detailed editing or extension:

| File | Description |
|------|-------------|
| [references/_sections.md](./_sections.md) | Category definitions and impact ordering |
| [assets/templates/_template.md](../assets/templates/_template.md) | Template for creating new rules |
| [SKILL.md](../SKILL.md) | Quick reference entry point |
