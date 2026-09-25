# SwiftData persistence reference index

Read only the categories relevant to the task. SwiftData rules below mix platform APIs with an opinionated repository architecture. Use repository and layer rules only when they fit the project; verify API availability before applying a rule.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Data Modeling | CRITICAL | `model-` |
| 2 | Persistence Setup | CRITICAL | `persist-` |
| 3 | Querying & Filtering | HIGH | `query-` |
| 4 | CRUD Operations | HIGH | `crud-` |
| 5 | Sync & Networking | HIGH | `sync-` |
| 6 | Relationships | MEDIUM-HIGH | `rel-` |
| 7 | SwiftUI State Flow | MEDIUM-HIGH | `state-` |
| 8 | Schema & Migration | MEDIUM-HIGH | `schema-` |
| 9 | Sample Data & Previews | MEDIUM | `preview-` |

## Quick Reference

### 1. Data Modeling (CRITICAL)

- [`model-domain-mapping`](model-domain-mapping.md) - Map @Model entities to domain structs across Domain/Data boundaries
- [`model-custom-types`](model-custom-types.md) - Use custom types over parallel arrays
- [`model-class-for-persistence`](model-class-for-persistence.md) - Use classes for SwiftData entity types
- [`model-identifiable`](model-identifiable.md) - Conform entities to Identifiable with UUID
- [`model-initializer`](model-initializer.md) - Provide custom initializers for entity classes
- [`model-computed-properties`](model-computed-properties.md) - Use computed properties for derived data
- [`model-defaults`](model-defaults.md) - Provide sensible default values for entity properties
- [`model-transient`](model-transient.md) - Mark non-persistent properties with @Transient
- [`model-external-storage`](model-external-storage.md) - Use external storage for large binary data

### 2. Persistence Setup (CRITICAL)

- [`persist-repository-wrapper`](persist-repository-wrapper.md) - Wrap SwiftData behind Domain repository protocols
- [`persist-model-macro`](persist-model-macro.md) - Apply @Model macro to all persistent types
- [`persist-container-setup`](persist-container-setup.md) - Configure ModelContainer at the App level
- [`persist-container-error-recovery`](persist-container-error-recovery.md) - Handle ModelContainer creation failure with store recovery
- [`persist-context-environment`](persist-context-environment.md) - Access ModelContext via @Environment (Data layer)
- [`persist-autosave`](persist-autosave.md) - Enable autosave for manually created contexts
- [`persist-enumerate-batch`](persist-enumerate-batch.md) - Use ModelContext.enumerate for large traversals
- [`persist-in-memory-config`](persist-in-memory-config.md) - Use in-memory configuration for tests and previews
- [`persist-app-group`](persist-app-group.md) - Use App Groups for shared data storage
- [`persist-model-actor`](persist-model-actor.md) - Use @ModelActor for background SwiftData work
- [`persist-identifier-transfer`](persist-identifier-transfer.md) - Pass PersistentIdentifier across actors

### 3. Querying & Filtering (HIGH)

- [`query-property-wrapper`](query-property-wrapper.md) - Use @Query for declarative data fetching (Data layer)
- [`query-background-refresh`](query-background-refresh.md) - Force view refresh after background context inserts
- [`query-sort-descriptors`](query-sort-descriptors.md) - Apply sort descriptors to @Query
- [`query-predicates`](query-predicates.md) - Use #Predicate for type-safe filtering
- [`query-dynamic-init`](query-dynamic-init.md) - Use custom view initializers for dynamic queries
- [`query-fetch-descriptor`](query-fetch-descriptor.md) - Use FetchDescriptor outside SwiftUI views
- [`query-fetch-tuning`](query-fetch-tuning.md) - Tune FetchDescriptor paging and pending-change behavior
- [`query-localized-search`](query-localized-search.md) - Use localizedStandardContains for search
- [`query-expression`](query-expression.md) - Use #Expression for reusable predicate components (iOS 18+)

### 4. CRUD Operations (HIGH)

- [`crud-insert-context`](crud-insert-context.md) - Insert models via repository implementations
- [`crud-delete-indexset`](crud-delete-indexset.md) - Delete via repository with IndexSet from onDelete
- [`crud-sheet-creation`](crud-sheet-creation.md) - Use sheets for focused data creation via ViewModel
- [`crud-cancel-delete`](crud-cancel-delete.md) - Avoid orphaned records by persisting only on save
- [`crud-undo-cancel`](crud-undo-cancel.md) - Enable undo and use it to cancel edits
- [`crud-edit-button`](crud-edit-button.md) - Provide EditButton for list management
- [`crud-dismiss-save`](crud-dismiss-save.md) - Dismiss modal after ViewModel save completes
- [`crud-save-error-handling`](crud-save-error-handling.md) - Handle repository save failures with user feedback

### 5. Sync & Networking (HIGH)

- [`sync-fetch-persist`](sync-fetch-persist.md) - Use injected sync services to fetch and persist API data
- [`sync-offline-first`](sync-offline-first.md) - Design offline-first architecture with repository reads and background sync
- [`sync-conflict-resolution`](sync-conflict-resolution.md) - Implement conflict resolution for bidirectional sync

### 6. Relationships (MEDIUM-HIGH)

- [`rel-optional-single`](rel-optional-single.md) - Use optionals for optional relationships
- [`rel-array-many`](rel-array-many.md) - Use arrays for one-to-many relationships
- [`rel-inverse-auto`](rel-inverse-auto.md) - Rely on SwiftData automatic inverse maintenance
- [`rel-delete-rules`](rel-delete-rules.md) - Configure cascade delete rules for owned relationships
- [`rel-explicit-sort`](rel-explicit-sort.md) - Sort relationship arrays explicitly

### 7. SwiftUI State Flow (MEDIUM-HIGH)

- [`state-query-vs-viewmodel`](state-query-vs-viewmodel.md) - Route all data access through @Observable ViewModels
- [`state-business-logic-placement`](state-business-logic-placement.md) - Place business logic in domain value types and repository-backed ViewModels
- [`state-dependency-injection`](state-dependency-injection.md) - Inject repository protocols via @Environment
- [`state-bindable`](state-bindable.md) - Use @Bindable for two-way model binding
- [`state-local-state`](state-local-state.md) - Use @State for view-local transient data
- [`state-wrapper-views`](state-wrapper-views.md) - Extract wrapper views for dynamic query state

### 8. Schema & Migration (MEDIUM-HIGH)

- [`schema-define-all-types`](schema-define-all-types.md) - Define schema with all model types
- [`schema-unique-attributes`](schema-unique-attributes.md) - Use @Attribute(.unique) for natural keys
- [`schema-unique-macro`](schema-unique-macro.md) - Use #Unique for compound uniqueness (iOS 18+)
- [`schema-index`](schema-index.md) - Use #Index for hot predicates and sorts (iOS 18+)
- [`schema-migration-plan`](schema-migration-plan.md) - Plan migrations before changing models
- [`schema-migration-recovery`](schema-migration-recovery.md) - Plan migration recovery for schema changes
- [`schema-configuration`](schema-configuration.md) - Customize storage with ModelConfiguration

### 9. Sample Data & Previews (MEDIUM)

- [`preview-sample-singleton`](preview-sample-singleton.md) - Create a SampleData singleton for previews
- [`preview-in-memory`](preview-in-memory.md) - Use in-memory containers for preview isolation
- [`preview-static-data`](preview-static-data.md) - Define static sample data on model types
- [`preview-main-actor`](preview-main-actor.md) - Annotate SampleData with @MainActor
