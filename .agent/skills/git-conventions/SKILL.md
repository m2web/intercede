---
name: git-conventions
description: Apply this project's Git commit message conventions, including the
  required emoji prefix, type, and short imperative description. Use this skill
  whenever generating a commit message or advising on branch naming.
---

# Git Conventions Skill

## When to Apply

Use this skill any time you are:

- Generating or suggesting a Git commit message
- Advising on branch naming
- Reviewing whether a commit message follows project standards

## Commit Message Format

Every commit message **must begin with the actual GitHub emoji character**
(not a `:code:` placeholder) that reflects the nature of the change,
followed by a short imperative subject line.

```text
✨ feat: add prayer card component

- Optional bullet detail
- Optional bullet detail
```

Pick the emoji character from the guide below.

### Emoji Guide

| Emoji code | Character to use | When to use |
| --- | --- | --- |
| `:sparkles:` | `✨` | New feature or initial commit |
| `:bug:` | `🐛` | Bug fix |
| `:memo:` | `📝` | Documentation update |
| `:recycle:` | `♻️` | Refactor (no behavior change) |
| `:art:` | `🎨` | Code style / formatting |
| `:zap:` | `⚡️` | Performance improvement |
| `:wrench:` | `🔧` | Config / tooling change |
| `:lock:` | `🔒` | Security fix |
| `:heavy_plus_sign:` | `➕` | Add a dependency |
| `:heavy_minus_sign:` | `➖` | Remove a dependency |
| `:wastebasket:` | `🗑️` | Remove dead code or files |
| `:rocket:` | `🚀` | Deploy or release |
| `:white_check_mark:` | `✅` | Add or update tests |
| `:twisted_rightwards_arrows:` | `🔀` | Merge branches |

## Branch Naming Strategy

- `main` - stable, production-ready code
- Feature branches: `feature/<short-description>`
- Bug fix branches: `fix/<short-description>`

## Files to Exclude from Commits

Never stage or commit:

- `.env` - secrets
- `__pycache__/`, `*.pyc` - Python bytecode
- `node_modules/` - frontend dependencies
- `dist/` - build output
