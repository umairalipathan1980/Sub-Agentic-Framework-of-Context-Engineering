Use our **prp-executor** sub-agent to execute the specified Product Requirements Prompt (PRP) and implement the feature.
    
**$ARGUMENTS** (path to PRP, e.g., `.claude/PRPs/feature-name.md`)

Requirements:
- Read the PRP completely and execute implementation **phase-by-phase**.
- For each phase: implement changes, then run validation gates/commands and tests.
- Use repo examples and any linked docs; optionally use WebSearch/WebFetch to resolve uncertainties.
- Provide progress output and end by echoing the completion checklist.

If delegation to the sub-agent is unavailable, perform the task directly with the same constraints.
