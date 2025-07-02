# Development Workflow

<div class="progress-tracker">
<span class="completed">[✓] Overview (10 min)</span> → <span class="completed">[✓] Setup (15 min)</span> → <span class="current">[●] Workflow (20 min)</span> → <span class="upcoming">[ ] Reference</span>
<div class="progress-time">Total: 45 min | Elapsed: 25 min | Remaining: 20 min</div>
</div>

## On This Page
- [Daily Operations](#daily-operations) - 5 min
- [Branch Management](#branch-management) - 5 min  
- [Collaboration](#collaboration) - 5 min
- [Validation](#validation-checkpoints) - 5 min

## Objectives
- Execute standard Git workflow independently
- Create and manage feature branches
- Submit changes via pull request

## Prerequisites
| Requirement | Verification | Time |
|-------------|--------------|------|
| Environment configured | `.venv` activated | 0 min |
| Repository cloned | `git status` executes | 0 min |
| GitHub access | Repository visible online | 0 min |

## Daily Operations

### Start Work Session
```bash
git checkout main && git pull origin main && git checkout -b feature/task-name
```
**Output**: `Switched to a new branch 'feature/task-name'`  
**Time**: 30 seconds

### Make Changes
```bash
# Edit files with your preferred editor
# Stage changes
git add -A                    # All changes
git add path/to/file.py      # Specific file

# Review staged changes
git diff --staged
```
**Time**: Variable

### Commit Changes
```bash
git commit -m "type: Brief description"
```
**Types**: `feat` | `fix` | `docs` | `refactor` | `test` | `chore`  
**Time**: 1 minute

### Push to Remote
```bash
git push -u origin feature/task-name    # First push
git push                                # Subsequent pushes
```
**Output**: URL for creating pull request  
**Time**: 30 seconds

## Branch Management

### Branch Operations
```bash
# List branches
git branch -v                    # Local branches
git branch -r                    # Remote branches

# Switch branches
git checkout branch-name         # Existing branch
git checkout -b new-branch       # Create and switch

# Delete branches
git branch -d merged-branch      # Safe delete
git branch -D unmerged-branch    # Force delete
git push origin --delete remote-branch
```

### Sync with Main
```bash
git checkout main && git pull
git checkout feature/task-name
git merge main                   # Or rebase: git rebase main
```
**Time**: 2 minutes

## Collaboration

### Create Pull Request

**Command Line (GitHub CLI):**
```bash
gh pr create --title "Brief description" --body "Details"
```

**Manual Process:**
1. Push branch: `git push -u origin feature/task-name`
2. Visit URL in output
3. Click "Create pull request"
4. Fill template

### Address Review Feedback
```bash
# Make requested changes
git add -A
git commit -m "Address review: specific change"
git push
```

### Resolve Conflicts
```bash
# Pull latest main
git pull origin main

# If conflicts occur:
# 1. Open conflicted files
# 2. Look for <<<<<<< markers
# 3. Edit to resolve
# 4. Remove all markers
git add resolved-file.py
git commit -m "Resolve merge conflicts"
git push
```
**Time**: 5-15 minutes

### Post-Merge Cleanup
```bash
git checkout main
git pull origin main
git branch -d feature/task-name
git remote prune origin
```
**Time**: 1 minute

## Validation Checkpoints

### Pre-Commit Checklist
- [ ] Correct branch: `git branch` shows feature branch
- [ ] Changes reviewed: `git diff` examined
- [ ] Tests pass: `pytest` succeeds
- [ ] Code quality: `ruff check .` passes
- [ ] No debug code: No print statements

### Pre-Push Verification
- [ ] Clean status: `git status` shows nothing to commit
- [ ] Commits logical: `git log --oneline -5` reviewed
- [ ] Branch current: `git pull origin main` completed

### PR Readiness
- [ ] Title descriptive: Starts with verb (Add, Fix, Update)
- [ ] Description complete: What/Why/How included
- [ ] Tests included: New tests for new code
- [ ] Documentation updated: If applicable
- [ ] CI passing: All checks green

## Common Errors

| Error | Command | Time |
|-------|---------|------|
| `divergent branches` | `git pull --rebase origin main` | 2 min |
| `nothing to commit` | `git status --porcelain` | 10 sec |
| `rejected push` | `git pull origin main` then push | 2 min |
| `detached HEAD` | `git checkout main` | 30 sec |

## Command Workflows

### Bug Fix Pattern
```bash
git checkout main && git pull
git checkout -b fix/issue-description
# Fix bug
git add -A && git commit -m "fix: Resolve issue"
git push -u origin fix/issue-description
gh pr create --label "bug"
```

### Feature Pattern
```bash
git checkout main && git pull
git checkout -b feature/new-capability
# Implement feature
git add -A && git commit -m "feat: Add capability"
# Additional commits as needed
git push -u origin feature/new-capability
gh pr create --label "enhancement"
```

### Documentation Pattern
```bash
git checkout -b docs/update-section
# Update docs
git add -A && git commit -m "docs: Update section"
git push -u origin docs/update-section
gh pr create --label "documentation"
```

## Workflow Validation Summary

### Before Starting Work
```bash
git fetch --all && git status
```
**Expected**: "Your branch is up to date", no uncommitted changes

### Before Committing
```bash
pytest && ruff check . && git diff
```
**Expected**: All tests pass, no linting errors, changes reviewed

### Before Creating PR
```bash
git log origin/main..HEAD --oneline && git status --porcelain
```
**Expected**: Commits listed, no uncommitted changes

### Health Check Script
```bash
# Save as check-health.sh
#!/bin/bash
echo "=== Git Health Check ==="
git status --porcelain && echo "✓ Clean working directory" || echo "✗ Uncommitted changes"
git rev-parse --abbrev-ref HEAD | grep -v main && echo "✓ On feature branch" || echo "✗ On main branch"
pytest --quiet && echo "✓ Tests pass" || echo "✗ Tests fail"
ruff check . --quiet && echo "✓ Code quality good" || echo "✗ Code issues found"
echo "=== Ready to commit: $([ $? -eq 0 ] && echo "YES" || echo "NO") ==="
```

---
**Next**: [Quick Reference](reference.md) • **Time Investment**: As needed