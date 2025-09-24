Use our **feature-documentor** sub-agent to document a completed feature across the project:
update the main `.claude/CLAUDE.md` **and** all relevant subdirectory `README.md` files.

Provide the feature name and (optionally) hints like ticket ID or keywords:
**$ARGUMENTS**

Requirements:
- Incremental-first: preserve accurate text; only change sections impacted by the feature.
- Update `.claude/CLAUDE.md` in relevant blueprint sections (features, architecture, tech stack, APIs/routes,
  integrations/dependencies, non-functional implications, recent changes). Add authoritative external links.
- Update each affected directory’s `README.md` with **blueprint-level** details:
  Role, Public Interfaces, Libraries & versions (with links), Config keys, Workflows and minimal runnable snippets,
  Testing commands/paths, Security/Performance notes, Dependencies/Integrations, Dir-scoped changelog, links to CLAUDE.md.
- Use `Glob/Grep/Read` for discovery; use `Bash` only for safe, read-only git queries; use `WebSearch/WebFetch`
  to verify and link external docs cited by the feature.
- End by returning a summary and echoing the completion checklist.

If delegation to the sub-agent is unavailable, perform the task directly with the same constraints.
