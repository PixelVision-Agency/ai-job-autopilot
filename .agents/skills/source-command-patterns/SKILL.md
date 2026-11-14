---
name: source-command-patterns
description: >
  Thin Codex pointer to the slash command /patterns, whose canonical text is .claude/commands/patterns.md.
---

# /patterns (pointer)

Use this skill when the user asks to run `/patterns`. The single source of truth is
`.claude/commands/patterns.md`: read it and follow it exactly. Read `profile/` first; if it is missing,
run `/onboard`. If the command names a Claude-only tool, use the closest available tool and state
any verification gap.
