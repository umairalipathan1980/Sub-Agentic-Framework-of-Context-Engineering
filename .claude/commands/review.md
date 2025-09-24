Conditional review command. Acts on `$ARGUMENTS`:
    
- If argument begins with **current** (optionally followed by a range or N):
  Use our **change-reviewer** sub-agent to review **recent changes only**.
  Examples:
    - `/review current` → last commit (HEAD~1..HEAD)
    - `/review current last5` → last 5 commits (HEAD~5..HEAD)
    - `/review current HEAD~3..HEAD` → explicit range
    - `/review current -- paths src/api/** tests/**` → limit to paths
- If argument is **complete**:
  Use our **project-reviewer** sub-agent for a full audit of the codebase.

The selected sub-agent must:
- Respect git ranges/paths provided in `$ARGUMENTS` (default last commit).
- Produce an actionable review with Critical/Warnings/Suggestions (or priorities), file:line refs, concrete fixes, and authoritative references.
- Remain read-only; use Git via Bash with documented, non-destructive commands.
