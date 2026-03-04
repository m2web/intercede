---
name: markdownlint-conventions
description: Apply this project's markdownlint rules when writing or editing any
  Markdown file. Use this skill before creating or modifying .md files to avoid
  linting violations defined in .markdownlint.json.
---

# Markdownlint Conventions Skill

## When to Apply

Use this skill any time you are:

- Creating a new `.md` file in this repo
- Editing existing Markdown content
- Fixing markdownlint errors reported by the linter

## Rules in Effect

### ASCII-only content

No emoji or non-ASCII characters in Markdown prose or tables.
Use `:emoji-code:` text references instead of the emoji character itself.

### Code blocks

- Style: **fenced** (never indented)
- Fence character: **backticks** only (not tildes)
- Language tag is **required** on every fenced block
- Allowed languages: `bash`, `html`, `javascript`, `json`, `markdown`,
  `mermaid`, `python`, `text`

### Headings

- Style: **ATX** (`#` prefix, not underline style)
- Duplicate headings are allowed only if they are not siblings

### Lists

- Unordered lists: **dash** (`-`) only, not `*` or `+`
- Ordered lists: **sequential numbers** (`1.`, `2.`, `3.`), not repeated `1.`

### Emphasis and strong

- Emphasis (`*italic*`): asterisk only, not underscores
- Strong (`**bold**`): asterisks only, not underscores

### Horizontal rules

- Style: `---` only

### Line length

- Soft limit enforced (non-strict mode)
- Line length is **not** checked inside code blocks

## Quick Reference

| Element | Correct | Incorrect |
| --- | --- | --- |
| Code fence | ` ```python ` | ` ~~~python ` or no language |
| Unordered list | `- item` | `* item` or `+ item` |
| Ordered list | `1. 2. 3.` | `1. 1. 1.` |
| Heading | `## Title` | `Title\n------` |
| Emphasis | `*text*` | `_text_` |
| Strong | `**text**` | `__text__` |
| Horizontal rule | `---` | `***` or `___` |
| Emoji | `:sparkles:` | `✨` |
