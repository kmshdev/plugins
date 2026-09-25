# iOS feature trigger prompt

Use this prompt to request the full feature workflow. Replace the bracketed fields with concrete details; omit optional fields that the app itself can answer.

> Use `$ios-feature-workflow` to implement **[feature]** in **[app or repository]** so **[user]** can **[observable outcome]**. Follow the app’s existing architecture and visual language. Build and run the affected flow, verify its behavior and rendered states, then run applicable formal review gates on the completed change. **[Optional constraints or acceptance criteria.]**

Example:

> Use `$ios-feature-workflow` to add saved searches in the Journal app so readers can rerun a search from the Library tab. Preserve the current SwiftData model boundary and tab navigation. Build and run the flow, verify save, rename, and delete behavior, then review the completed change.
