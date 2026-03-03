# Git Conventions

## Commit Message Format

Every commit message **must begin with a GitHub emoji** that reflects the
nature of the change, followed by a short imperative subject line.

```text
:emoji: type: short description

- Optional bullet detail
- Optional bullet detail
```

### Emoji Guide

| Emoji | Code | When to use |
| --- | --- | --- |
| ✨ | `:sparkles:` | New feature or initial commit |
| 🐛 | `:bug:` | Bug fix |
| 📝 | `:memo:` | Documentation update |
| ♻️ | `:recycle:` | Refactor (no behavior change) |
| 🎨 | `:art:` | Code style / formatting |
| ⚡️ | `:zap:` | Performance improvement |
| 🔧 | `:wrench:` | Config / tooling change |
| 🔒 | `:lock:` | Security fix |
| ➕ | `:heavy_plus_sign:` | Add a dependency |
| ➖ | `:heavy_minus_sign:` | Remove a dependency |
| 🗑️ | `:wastebasket:` | Remove dead code or files |
| 🚀 | `:rocket:` | Deploy or release |
| ✅ | `:white_check_mark:` | Add or update tests |
| 🔀 | `:twisted_rightwards_arrows:` | Merge branches |

## Branch Strategy

- `main` — stable, production-ready code
- Feature branches: `feature/<short-description>`
- Bug fix branches: `fix/<short-description>`

## Files to Exclude from Commits

- `.env` — never commit secrets
- `__pycache__/`, `*.pyc` — Python bytecode
- `node_modules/` — frontend dependencies
- `dist/` — build output
