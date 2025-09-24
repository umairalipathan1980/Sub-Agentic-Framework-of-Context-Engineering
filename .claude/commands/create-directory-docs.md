Use our **directory-documentor** sub-agent to create or update **README.md** files for important subdirectories.

**Focus:** $ARGUMENTS (directory names or glob patterns). If omitted, analyze the repo and document major directories automatically.

Requirements:
- Incremental-first: update existing READMEs; otherwise create new ones.
- Use Glob/Grep/Read for discovery; use Bash only for safe, read-only context (e.g., git log for the directory).
- Each README should be a **blueprint** for re-creating the directory’s functionality:
  - Role in the System; Structure & Entrypoints
  - Public Interfaces (APIs/Exports/Events) with signatures/tables
  - Libraries & Frameworks (versions + **links to official docs**)
  - Configuration (env vars/flags/keys)
  - Typical Workflows and a short text sequence diagram
  - Minimal Runnable Snippets (plus commands to run them)
  - Testing & Quality (paths, commands, gates)
  - Operational Notes (logging/metrics/alerts), Security & Performance
  - Dependencies & Integrations; Dir-scoped Changelog (git)
  - Maintenance & Ownership; Related Docs & Links (incl. CLAUDE.md)
- Prefer short, accurate, runnable examples; avoid duplication of CLAUDE.md.
- No placeholders or TODOs. End by echoing the completion checklist.

If delegation to the sub-agent is unavailable, perform the task directly with the same constraints.

