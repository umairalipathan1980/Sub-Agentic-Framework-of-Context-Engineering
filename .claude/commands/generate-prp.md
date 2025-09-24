Use our **prp-generator** sub-agent to generate a comprehensive Product Requirements Prompt (PRP) under `.claude/PRPs/` from:
    
**$ARGUMENTS** (path to `.claude/INITIAL.md` or description that identifies it)

Requirements:
- Read `.claude/INITIAL.md` (or the specified requirements file) completely.
- Research repo patterns and relevant examples; include external docs referenced in `.claude/INITIAL.md` and, if essential, discover more with WebSearch/WebFetch.
- Output `.claude/PRPs/<feature>.md` with: Research Findings → Phased Implementation Plan → Phase Details → Success Criteria → Risk Assessment.
- Include concrete file paths, commands, and per-phase validation gates.
- End by echoing the completion checklist.

If delegation to the sub-agent is unavailable, perform the task directly with the same constraints.
