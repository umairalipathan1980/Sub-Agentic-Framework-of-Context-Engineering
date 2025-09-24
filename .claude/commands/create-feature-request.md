Use our **feature-requestor** sub-agent to produce (or overwrite) **.claude/INITIAL.md** for the following requested feature:
    
**$ARGUMENTS**

Requirements:
- Populate **.claude/INITIAL.md** using its existing four-section template with these headings (including trailing colons) and in this order:
  - ## FEATURE:
  - ## EXAMPLES:
  - ## DOCUMENTATION:
  - ## OTHER CONSIDERATIONS:
- No extra sections or pre/post text.
- Reference files from `examples/**` (if present) in **EXAMPLES** and explain their usage.
- In **DOCUMENTATION**, include links from the feature description and optionally use WebSearch/WebFetch to add essential external sources.
- No placeholders or TODOs. Use “Not applicable” only when truly N/A.
- End by echoing the completion checklist.

If delegation to the sub-agent is unavailable, perform the task directly with the same constraints.

