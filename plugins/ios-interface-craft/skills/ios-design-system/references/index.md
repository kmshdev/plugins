# SwiftUI design systems reference index

Read only the categories relevant to the task. Choose rules that fit the task and supported SDK. Some examples assume a modular clinic app; their architecture constraints apply only to projects that adopted that design.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix | Rules |
|----------|----------|--------|--------|-------|
| 1 | Token Architecture | CRITICAL | `token-` | 6 |
| 2 | Color System Engineering | CRITICAL | `color-` | 7 |
| 3 | Component Style Library | CRITICAL | `style-` | 10 |
| 4 | Typography Scale | HIGH | `type-` | 5 |
| 5 | Spacing & Sizing System | HIGH | `space-` | 5 |
| 6 | Consistency & Governance | HIGH | `govern-` | 7 |
| 7 | Asset Management | MEDIUM-HIGH | `asset-` | 5 |
| 8 | Theme & Brand Infrastructure | MEDIUM | `theme-` | 5 |

## Quick Reference

### 1. Token Architecture (CRITICAL)

- [`token-three-layer-hierarchy`](token-three-layer-hierarchy.md) - Use Raw → Semantic → Component token layers
- [`token-enum-over-struct`](token-enum-over-struct.md) - Use caseless enums for token namespaces
- [`token-single-file-per-domain`](token-single-file-per-domain.md) - One token file per design domain
- [`token-shapestyle-extensions`](token-shapestyle-extensions.md) - Extend ShapeStyle for dot-syntax colors
- [`token-asset-catalog-source`](token-asset-catalog-source.md) - Source color tokens from asset catalog
- [`token-avoid-over-abstraction`](token-avoid-over-abstraction.md) - Avoid over-abstracting beyond three layers

### 2. Color System Engineering (CRITICAL)

- [`color-organized-xcassets`](color-organized-xcassets.md) - Organize color assets with folder groups by role
- [`color-complete-pairs`](color-complete-pairs.md) - Define both appearances for every custom color
- [`color-limit-palette`](color-limit-palette.md) - Limit custom colors to under 20 semantic tokens
- [`color-no-hex-in-views`](color-no-hex-in-views.md) - Never use Color literals or hex in view code
- [`color-system-first`](color-system-first.md) - Prefer system colors before custom tokens
- [`color-tint-not-brand-everywhere`](color-tint-not-brand-everywhere.md) - Set brand color as app tint, don't scatter it
- [`color-audit-script`](color-audit-script.md) - Audit for ungoverned colors with a build script

### 3. Component Style Library (CRITICAL)

- [`style-dls-protocol-pattern`](style-dls-protocol-pattern.md) - Define custom style protocols for complex DLS components
- [`style-equatable-views`](style-equatable-views.md) - Apply @Equatable to every design system view
- [`style-accessibility-first`](style-accessibility-first.md) - Build accessibility into style protocols, not individual views
- [`style-protocol-over-wrapper`](style-protocol-over-wrapper.md) - Use Style protocols instead of wrapper views
- [`style-static-member-syntax`](style-static-member-syntax.md) - Provide static member syntax for custom styles
- [`style-environment-awareness`](style-environment-awareness.md) - Make styles responsive to environment values
- [`style-view-for-containers-modifier-for-styling`](style-view-for-containers-modifier-for-styling.md) - Views for containers, modifiers for styling
- [`style-catalog-file`](style-catalog-file.md) - One style catalog file per component type
- [`style-configuration-over-parameters`](style-configuration-over-parameters.md) - Prefer configuration structs over many parameters
- [`style-preview-catalog`](style-preview-catalog.md) - Create a preview catalog for all styles

### 4. Typography Scale (HIGH)

- [`type-scale-enum`](type-scale-enum.md) - Define a type scale enum wrapping system styles
- [`type-system-styles-first`](type-system-styles-first.md) - Use system text styles before custom ones
- [`type-custom-font-registration`](type-custom-font-registration.md) - Register custom fonts with a centralized extension
- [`type-max-styles-per-screen`](type-max-styles-per-screen.md) - Limit typography variations to 3-4 per screen
- [`type-avoid-font-design-mixing`](type-avoid-font-design-mixing.md) - Use one font design per app

### 5. Spacing & Sizing System (HIGH)

- [`space-token-enum`](space-token-enum.md) - Define spacing tokens as a caseless enum
- [`space-radius-tokens`](space-radius-tokens.md) - Define corner radius tokens by component type
- [`space-no-magic-numbers`](space-no-magic-numbers.md) - Zero hardcoded numbers in view layout code
- [`space-insets-pattern`](space-insets-pattern.md) - Use EdgeInsets constants for composite padding
- [`space-size-tokens`](space-size-tokens.md) - Define size tokens for common dimensions

### 6. Consistency & Governance (HIGH)

- [`govern-naming-conventions`](govern-naming-conventions.md) - Enforce consistent naming conventions across all tokens
- [`govern-spm-package-boundary`](govern-spm-package-boundary.md) - Isolate the design system as a local SPM package
- [`govern-single-source-of-truth`](govern-single-source-of-truth.md) - Every visual value has one definition point
- [`govern-lint-for-tokens`](govern-lint-for-tokens.md) - Use SwiftLint rules to enforce token usage
- [`govern-design-system-directory`](govern-design-system-directory.md) - Isolate tokens in a dedicated directory
- [`govern-migration-incremental`](govern-migration-incremental.md) - Migrate to tokens incrementally
- [`govern-prevent-local-tokens`](govern-prevent-local-tokens.md) - Prevent feature modules from defining local tokens

### 7. Asset Management (MEDIUM-HIGH)

- [`asset-separate-catalogs`](asset-separate-catalogs.md) - Separate asset catalogs for colors, images, icons
- [`asset-sf-symbols-first`](asset-sf-symbols-first.md) - Use SF Symbols before custom icons
- [`asset-icon-export-format`](asset-icon-export-format.md) - Use PDF/SVG vectors, never multiple PNGs
- [`asset-image-optimization`](asset-image-optimization.md) - Use compression and on-demand resources
- [`asset-naming-convention`](asset-naming-convention.md) - Consistent naming convention for all assets

### 8. Theme & Brand Infrastructure (MEDIUM)

- [`theme-environment-key`](theme-environment-key.md) - Use EnvironmentKey for theme propagation
- [`theme-dont-over-theme`](theme-dont-over-theme.md) - Avoid building a theme system unless needed
- [`theme-tint-for-brand`](theme-tint-for-brand.md) - Use .tint() as primary brand expression
- [`theme-light-dark-only`](theme-light-dark-only.md) - Use ColorScheme for light/dark, not custom theming
- [`theme-brand-layer-separation`](theme-brand-layer-separation.md) - Separate brand identity from system mechanics
