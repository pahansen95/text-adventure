# Git Workflow Quick Reference Card

## Daily Workflow
```bash
# Start work
git checkout main && git pull
git checkout -b feature/task-name

# Make changes & commit
git add -A
git commit -m "type: description"

# Share work
git push -u origin feature/task-name
gh pr create --title "Title" --body "Description"
```

## Essential Commands

### Setup
```bash
git clone https://github.com/pahansen95/py-project-tmpl.git
cd py-project-tmpl
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Branch Management
```bash
git branch -v                    # List branches
git checkout -b new-branch       # Create & switch
git checkout main               # Switch to main
git branch -d old-branch        # Delete local
git push origin --delete branch # Delete remote
```

### Common Fixes
```bash
# Wrong branch
git stash && git checkout correct-branch && git stash pop

# Undo last commit
git reset --soft HEAD~1

# Resolve conflicts
git pull origin main
# Edit files, remove <<<, ===, >>>
git add . && git commit -m "Resolve conflicts"

# Update rejected push
git pull --rebase origin main && git push
```

### Validation Commands
```bash
git status              # Check state
git diff               # Review changes
git log --oneline -5   # Recent commits
pytest                 # Run tests
ruff check .           # Check code
```

## Commit Types
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code restructuring
- `test:` Testing
- `chore:` Maintenance

## Time Estimates
- Clone & setup: 5 min
- Feature branch: 30 sec
- Commit cycle: 2 min
- Push & PR: 2 min
- Conflict resolution: 5-15 min

---
Print double-sided and keep at desk for quick reference.