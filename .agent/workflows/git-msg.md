---
description: generate a git commit message for staged changes
---

# git msg — Generate a Commit Message

When the user types `git msg` or `/git-msg`, do the following:

1. Run `git diff --cached` to get the staged diff.
2. If nothing is staged, tell the user to stage files first and stop.
3. Read the git-conventions skill:
   `c:\Users\m2web\source\repos\AI\intercede\.agent\skills\git-conventions\SKILL.md`
4. Produce a single commit message that follows the convention exactly:
   - Start with any emoji character or `:emoji_code:` that fits the change
   - Followed by `type: short imperative description` (≤72 chars total)
   - Optionally add a blank line and bullet-point details if the diff warrants it
5. Print only the commit message — no explanation, no markdown fences.
