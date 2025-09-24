

Use our **greenfield-initializer** sub-agent to create or overwrite **.claude/INITIAL.md** for a brand-new repository.

**Input / hints:** $ARGUMENTS (e.g., desired stack: "node-ts", "python", "fastapi+postgres", "create an application...", plus any constraints)

Requirements:
- Populate the four sections (## FEATURE:, ## EXAMPLES:, ## DOCUMENTATION:, ## OTHER CONSIDERATIONS:) **exactly** and in that order.
- No extra sections or pre/post text.
- Include links, if mentioned, via WebSearch/WebFetch.
- Reference documentations, if mentioned. 
- Reference files from `examples/**` (if present and mentioned in the specification) in **EXAMPLES** and explain their usage.
- No placeholders or TODOs; use “Not applicable” only when truly N/A.
- End by echoing the completion checklist.

If delegation to the sub-agent is unavailable, perform the task directly with the same constraints.

