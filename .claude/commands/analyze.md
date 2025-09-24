First, check if `.claude/CLAUDE.md` exists.

If `.claude/CLAUDE.md` exists *AND* contains the specific project details:
- Review the existing project context using our minor-analyzer agent
- UPDATE existing sections in .claude/CLAUDE.md rather than overwriting everything

If `.claude/CLAUDE.md` does *not* exist *OR* contains just the template structure without any specific project details:
- Use our **project-analyzer** agent to perform comprehensive project analysis.
- Create new `CLAUDE.md` with full blueprint.

Focus area: `$ARGUMENTS` (if specified, e.g. module name, feature, folder); otherwise full project scope.

**Success =** A `.claude/CLAUDE.md` at project root that satisfies the full blueprint template sections (if project-analyzer used), or updated relevant sections cleanly (if minor-analyzer used). No redundant gaps; recent changes reflected; no TODO/FIXME placeholders.

If delegation to the chosen sub-agent fails (tools missing, permissions, etc.), do the task directly (following project‐analyzer logic if major context, or minor logic if minor) and echo the completion checklist at end.
