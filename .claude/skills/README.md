# Skills

Reusable, filesystem-based instructions Claude Code (and Claude Desktop) load
on demand. Each skill is its own directory with a strict layout:

```
.claude/skills/<skill-name>/
├── SKILL.md          ← required. The instructions Claude reads.
├── scripts/          ← optional. Helper scripts the skill invokes.
├── references/       ← optional. Long-form docs, examples, schemas.
└── assets/           ← optional. Images, templates, fixtures.
```

### `SKILL.md` frontmatter (minimum)

```markdown
---
name: skill-name              # kebab-case, matches the folder
description: One sentence about when to trigger this skill.
---

# When to use
…

# What to do
…
```

### Conventions in this repo

- `description:` must read like a tool description — Claude uses it to decide whether to load the skill. Be specific about triggers.
- Keep `SKILL.md` short. Push detail into `references/`; load on demand.
- Scripts go in `scripts/` and are invoked by the skill instructions (not loaded into context). Prefer Python or shell.
- One skill per directory. Don't nest skills.

### Status

⬜ No skills yet. **World 8** unlocks the first skill — a `mcp-server-author`
skill that codifies the conventions taught across worlds 1–7.
