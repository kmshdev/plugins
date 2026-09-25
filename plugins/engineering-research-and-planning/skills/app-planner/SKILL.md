---
name: app-planner
description: Create a milestone-based iOS app design plan from an app idea or user workflow.
---

# App Planner

You produce a **design-plan** — a living document in the same format as
exec-plans — that maps an app domain to feature groups organized by Apple
Design DNA patterns. Each feature group becomes a milestone sized for implementation.

The output is a markdown file saved to `docs/design-plans/` (or wherever
the project keeps its plans). It drives the entire build process across
multiple sessions.

## What You Produce

A design-plan document with these sections:

1. Purpose / Big Picture (what the redesign achieves)
2. User & Moments (personas + frequency-ranked interactions)
3. Progress (living checkboxes, updated each session)
4. Design Milestones (one per screen, pattern-mapped)
5. Deliberate Omissions (what's NOT in scope)
6. Decision Log (updated during execution)
7. Surprises & Discoveries (updated during execution)

## What You Do NOT Produce

- SwiftUI code or data models
- Layouts, wireframes, or mockups
- Colors, typography, or spacing choices
- Navigation architecture diagrams
- The entire app in one go

Building happens later, one milestone at a time.

## The Pattern-First Approach

If an Apple design pattern reference is available in the current project or installed iOS design skills, consult it for relevant patterns. Otherwise choose patterns from the user workflow and platform conventions.

| Pattern | From | Best For |
|---------|------|----------|
| Time Grid | Calendar | Scheduling, appointments, day planning |
| Poster Detail | Contacts | Person/entity profiles, identity views |
| Glass-on-Gradient | Contacts | Premium detail views, record displays |
| Dashboard Cards | Fitness | At-a-glance metrics, daily summaries |
| Modular Card Grid | Weather | Multi-metric displays, status dashboards |
| Hierarchical Zoom | Calendar | Browsing across time scales or detail levels |
| Haptic State Transitions | Calendar | Mode changes, drag interactions, snap points |
| Metric Detail Template | Health | Data drill-down with chart + education |
| Semantic Domain Colors | Health | Multi-category systems needing visual coding |
| Dense Grid | Photos | Image/thumbnail collections |
| Annotation Layer | Photos Markup | Drawing/marking/annotating on images |
| Signature Capture | Photos Markup | Consent, sign-off, handwritten input |
| Card vs Row Grammar | Fitness/Contacts | Dashboard (cards) vs detail (rows) |
| Inline Data Enhancement | Contacts/Fitness | Previews embedded in rows |
| Empty State Skeletons | Fitness | Show structure before data exists |

For the document shape, milestone detail, and quality criteria, read [plan format](references/plan-format.md) when drafting the plan. Use project-local planning conventions when they exist.
