# iOS interface review reference index

Read only the categories relevant to the task. Choose rules that fit the task and supported SDK. Some examples assume a modular clinic app; their architecture constraints apply only to projects that adopted that design.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Navigation | CRITICAL | `nav-` |
| 2 | Interaction Design | CRITICAL | `inter-` |
| 3 | Accessibility | CRITICAL | `acc-` |
| 4 | User Feedback | HIGH | `feed-` |
| 5 | UX Patterns | HIGH | `ux-` |
| 6 | Visual Design | HIGH | `vis-` |

## Quick Reference

### 1. Navigation (CRITICAL)

- [`nav-tab-bar`](nav-tab-bar.md) - Design tab bars for top-level navigation
- [`nav-navigation-stack`](nav-navigation-stack.md) - Use NavigationStack for hierarchical navigation
- [`nav-toolbar-placement`](nav-toolbar-placement.md) - Place actions in toolbars using standard placements

### 2. Interaction Design (CRITICAL)

- [`inter-touch-targets`](inter-touch-targets.md) - Maintain 44pt minimum touch targets
- [`inter-gesture-patterns`](inter-gesture-patterns.md) - Use standard gesture patterns
- [`inter-haptic-feedback`](inter-haptic-feedback.md) - Add haptic feedback for meaningful events
- [`inter-keyboard-handling`](inter-keyboard-handling.md) - Handle keyboard appearance gracefully
- [`inter-drag-drop`](inter-drag-drop.md) - Support drag and drop for content transfer
- [`inter-pull-to-refresh`](inter-pull-to-refresh.md) - Support pull to refresh for lists
- [`inter-swipe-actions`](inter-swipe-actions.md) - Add swipe actions for contextual operations
- [`inter-list-search`](inter-list-search.md) - Use searchable for built-in search

### 3. Accessibility (CRITICAL)

- [`acc-labels`](acc-labels.md) - Provide meaningful accessibility labels
- [`acc-dynamic-type`](acc-dynamic-type.md) - Support Dynamic Type for all text
- [`acc-color-contrast`](acc-color-contrast.md) - Maintain sufficient color contrast
- [`acc-reduce-motion`](acc-reduce-motion.md) - Respect reduce motion preference
- [`acc-color-independent`](acc-color-independent.md) - Never rely on color alone
- [`acc-focus-management`](acc-focus-management.md) - Manage focus for assistive technologies
- [`acc-scaled-metric`](acc-scaled-metric.md) - Use ScaledMetric for adaptive sizing
- [`acc-view-that-fits`](acc-view-that-fits.md) - Use ViewThatFits for adaptive layouts

### 4. User Feedback (HIGH)

- [`feed-loading-states`](feed-loading-states.md) - Show appropriate loading indicators
- [`feed-error-states`](feed-error-states.md) - Handle errors with clear recovery actions
- [`feed-notifications`](feed-notifications.md) - Use notifications judiciously
- [`feed-success-confirmation`](feed-success-confirmation.md) - Confirm successful actions appropriately
- [`feed-empty-states`](feed-empty-states.md) - Design helpful empty states

### 5. UX Patterns (HIGH)

- [`ux-onboarding`](ux-onboarding.md) - Design minimal onboarding
- [`ux-permissions`](ux-permissions.md) - Request permissions in context
- [`ux-modality`](ux-modality.md) - Use modality appropriately
- [`ux-confirmation-dialog`](ux-confirmation-dialog.md) - Use confirmation dialogs for destructive actions
- [`ux-data-entry`](ux-data-entry.md) - Minimize data entry friction
- [`ux-undo`](ux-undo.md) - Support undo for destructive actions
- [`ux-settings`](ux-settings.md) - Organize settings logically

### 6. Visual Design (HIGH)

- [`vis-dark-mode`](vis-dark-mode.md) - Support dark mode with semantic colors
- [`vis-sf-symbols`](vis-sf-symbols.md) - Use SF Symbols with correct rendering mode and weight
- [`vis-layout-margins`](vis-layout-margins.md) - Use standard layout margins and safe areas
