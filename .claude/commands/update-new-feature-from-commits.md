Use our **commit-documentor** sub-agent to detect and document recently implemented feature(s) **from git commits**,
updating the main `CLAUDE.md` and all relevant subdirectory `README.md` files.

**Focus / Range:** $ARGUMENTS (e.g., a commit SHA, `HEAD~10..HEAD`, or a keyword like "payments").

Requirements:
- Incremental-first: preserve correct content; update only sections impacted by the feature(s).
- Use safe, read-only git queries via Bash to infer scope (e.g., `git log --oneline -10`, `git diff --name-only <range>`, `git show --name-only <sha>`).
- Update `CLAUDE.md` in project blueprint sections (features, architecture, tech stack, APIs/routes, integrations, non-functional, recent changes).
- Update each affected directory’s `README.md` with **blueprint-level** detail (role, interfaces, libraries+links, config, workflows, runnable snippets, testing, security/perf, dependencies/integrations, dir-scoped changelog, links to CLAUDE.md).
- Use Glob/Grep/Read for repo discovery; use WebSearch/WebFetch to include authoritative external docs referenced in commits or code.
- End by returning a summary and echoing the completion checklist.

If delegation to the sub-agent is unavailable, perform the task directly with the same constraints.

