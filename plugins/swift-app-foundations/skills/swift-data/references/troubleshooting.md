# SwiftData troubleshooting

Use the symptom to find relevant rules, then check the project’s actual persistence design before changing it.

## Troubleshooting

- Data not persisting -> `persist-model-macro`, `persist-container-setup`, `persist-autosave`, `schema-configuration`
- List not updating after background import -> `query-background-refresh`, `persist-model-actor`
- List not updating (same-context) -> `query-property-wrapper`, `state-wrapper-views`
- Duplicates from API sync -> `schema-unique-attributes`, `sync-conflict-resolution`
- App crashes on launch after model change -> `schema-migration-recovery`, `persist-container-error-recovery`
- Save failures silently losing data -> `crud-save-error-handling`
- Stale data from network -> `sync-offline-first`, `sync-fetch-persist`
- Widget/extension can't see data -> `persist-app-group`, `schema-configuration`
- Choosing architecture pattern for data views -> `state-query-vs-viewmodel`, `persist-repository-wrapper`
