
Use our **greenfield-initializer** sub-agent to create or overwrite **.claude/INITIAL.md** for a brand-new repository.

**Input / hints:** $ARGUMENTS (e.g., desired stack: "node-ts", "python", "fastapi+postgres", "create an application...", plus any constraints)

Requirements:
- Populate the four sections (## FEATURE:, ## EXAMPLES:, ## DOCUMENTATION:, ## OTHER CONSIDERATIONS:) **exactly** and in that order.
- Tailor content for scaffolding an empty repo: MVP scope, initial modules, acceptance criteria that prove the scaffold works (builds, tests, CI).
- Include authoritative links (language/framework/test/CI) via WebSearch/WebFetch.
- No placeholders or TODOs; use “Not applicable” only when truly N/A.
- End by echoing the completion checklist.

If delegation to the sub-agent is unavailable, perform the task directly with the same constraints.

