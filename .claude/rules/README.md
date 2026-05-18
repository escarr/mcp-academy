# House Rules

Longer-form rules that don't fit in `CLAUDE.md` but should be consulted
before specific kinds of changes. Each rule is a single `.md` file with a
clear trigger (when it applies).

Recommended pattern:

```markdown
---
name: rule-name
applies-to: "what file path or topic this gates" (e.g. backend/grader.py, all PRs)
---

# Rule
Short statement of the rule.

# Why
The reason — usually a past incident or invariant.

# How to apply
Concrete examples of compliant and non-compliant code.
```

Reference these from CLAUDE.md or DECISIONS.md when relevant, so future
Claude sessions know when to check them.

### Status

⬜ No rules yet. Candidate first rule once World 2 ships:
`tools-must-have-annotations.md` — every MCP tool we write must set
`readOnlyHint`, `destructiveHint`, or `idempotentHint` annotations so Claude
can make informed auto-run decisions.
