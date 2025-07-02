# Quick Reference

<div class="progress-tracker">
<span class="completed">[✓] Overview (10 min)</span> → <span class="completed">[✓] Setup (15 min)</span> → <span class="completed">[✓] Workflow (20 min)</span> → <span class="current">[●] Reference</span>
<div class="progress-time">Total: 45 min | Elapsed: 45 min | Remaining: 0 min</div>
</div>

## Navigation
[Commands](#command-tables) | [Troubleshooting](#troubleshooting) | [Configuration](#configuration) | [Emergency](#emergency-commands) | [Glossary](#glossary) | [Printable Card](quick-reference-card.md)

## Command Tables

### Git Operations
| Operation | Command | Output |
|-----------|---------|--------|
| Clone | `git clone [url]` | Local repository created |
| Branch | `git checkout -b [name]` | Switched to new branch |
| Stage | `git add .` | Changes staged |
| Commit | `git commit -m "[msg]"` | Commit created |
| Push | `git push -u origin [branch]` | Branch pushed, PR URL |
| Pull | `git pull origin main` | Local updated |
| Status | `git status` | Working tree status |
| Log | `git log --oneline -10` | Recent commits |
| Diff | `git diff` | Unstaged changes |

### Python/UV Commands
| Task | Command | Purpose |
|------|---------|---------|
| Create venv | `uv venv` | New .venv directory |
| Activate | `source .venv/bin/activate` | Enter virtual environment |
| Install package | `uv pip install [pkg]` | Add dependency |
| Install project | `uv pip install -e ".[dev]"` | Development mode |
| List packages | `uv pip list` | Show installed |
| Run tests | `pytest` | Execute test suite |
| Format code | `ruff format .` | Auto-format Python |
| Check code | `ruff check .` | Find issues |

### Branch Operations
| Task | Command | Result |
|------|---------|--------|
| List local | `git branch -v` | Shows branches with last commit |
| List remote | `git branch -r` | Shows origin branches |
| Switch | `git checkout [name]` | Changes active branch |
| Delete local | `git branch -d [name]` | Removes merged branch |
| Delete remote | `git push origin --delete [name]` | Removes from GitHub |
| Update list | `git fetch --prune` | Syncs branch list |

## Troubleshooting

### Authentication
**SSH Key Setup**
```bash
ssh-keygen -t ed25519 -C "email@example.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub  # Add to GitHub
git remote set-url origin git@github.com:USER/REPO.git
```

**Token Authentication**
```bash
# Create at github.com/settings/tokens
git remote set-url origin https://[TOKEN]@github.com/[USER]/[REPO].git
```

### Merge Conflicts
```bash
git status                    # See conflicted files
# Edit files to resolve
# Remove <<<, ===, >>> markers
git add [resolved-file]
git commit -m "Resolve conflicts"
git push
```

### Common Errors
| Error | Fix | Time |
|-------|-----|------|
| `rejected push` | `git pull origin main` first | 2 min |
| `divergent branches` | `git pull --rebase origin main` | 3 min |
| `detached HEAD` | `git checkout main` | 30 sec |
| `command not found` | Restart terminal | 1 min |
| `permission denied` | Check SSH: `ssh -T git@github.com` | 5 min |

### Wrong Branch Fixes
```bash
# Uncommitted changes on wrong branch
git stash
git checkout correct-branch
git stash pop

# Committed to wrong branch
git branch correct-branch     # Create branch with commits
git reset --hard HEAD~1       # Remove from current
git checkout correct-branch   # Switch to new branch
```

## Configuration

### Git Setup
```bash
git config --global user.name "Your Name"
git config --global user.email "email@example.com"
git config --global init.defaultBranch main
git config --global core.autocrlf true      # Windows
git config --global core.autocrlf input     # Mac/Linux
git config --global pull.rebase false
git config --global push.default current
```

### Useful Aliases
```bash
git config --global alias.st "status -sb"
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm commit
git config --global alias.unstage "reset HEAD --"
git config --global alias.last "log -1 HEAD"
git config --global alias.visual "log --graph --oneline --all"
```

## Emergency Commands

### Undo Operations
```bash
git reset --soft HEAD~1      # Undo commit, keep changes
git reset --hard HEAD~1      # Undo commit, discard changes
git checkout -- .            # Discard all changes
git clean -fd               # Remove untracked files
git rm --cached file.txt    # Untrack file
```

### Recovery
```bash
git reflog                  # Find lost commits
git checkout -b recovery [hash]  # Restore commit
git fsck --lost-found       # Find dangling objects
```

### Reset to Remote
```bash
git fetch origin
git reset --hard origin/main
git clean -fd
```

## Glossary

**Branch** - Independent development line  
**Clone** - Local copy of repository  
**Commit** - Saved snapshot of changes  
**Conflict** - Competing changes requiring resolution  
**Fork** - Personal copy of another's repository  
**HEAD** - Pointer to current commit  
**Merge** - Combine branches  
**Origin** - Default remote name  
**Pull** - Fetch and merge remote changes  
**Push** - Upload commits to remote  
**PR** - Pull Request for code review  
**Rebase** - Reapply commits on new base  
**Remote** - Repository on server  
**Repository** - Project with version history  
**Stage** - Mark changes for commit  
**Stash** - Temporary storage for changes  

---
**Keyboard Shortcuts**: VS Code (`Ctrl+Shift+G` Git panel), Terminal (`Ctrl+R` search history)