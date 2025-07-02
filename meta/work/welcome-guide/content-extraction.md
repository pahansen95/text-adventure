# Welcome Guide Content Extraction

## Commands Extracted

### Environment Setup Commands

#### System Verification
```bash
# Git version check
git --version  # Expected: 2.30+

# Python version check  
python --version  # Expected: 3.10+

# UV version check
uv --version  # Expected: 0.4+

# Virtual environment check
which python  # Expected: /path/to/project/.venv/bin/python
```

#### Installation Commands

**Windows:**
```powershell
# Automated setup
Set-ExecutionPolicy Bypass -Scope Process -Force
irm https://raw.githubusercontent.com/pahansen95/py-project-tmpl/main/scripts/setup-welcome.ps1 | iex

# Manual Git install
winget install --id Git.Git -e

# Manual Python install  
winget install --id Python.Python.3.12 -e

# UV install
irm https://astral.sh/uv/install.ps1 | iex
```

**macOS/Linux:**
```bash
# Automated setup
curl -sSL https://raw.githubusercontent.com/pahansen95/py-project-tmpl/main/scripts/setup-welcome.sh | bash

# Manual installations
brew install git python@3.12  # macOS
sudo apt-get install git python3.12  # Ubuntu/Debian
sudo dnf install git python3.12  # Fedora

# UV install
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Project Setup
```bash
# Clone repository
git clone https://github.com/pahansen95/py-project-tmpl.git
cd py-project-tmpl

# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e ".[dev,docs]"
```

### Git Configuration Commands
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
git config --global color.ui auto
git config --global core.autocrlf true   # Windows
git config --global core.autocrlf input  # macOS/Linux
```

### Daily Workflow Commands

#### Branch Operations
```bash
# Create and switch to branch
git checkout -b feature/name

# List branches
git branch -v

# Delete branch
git branch -d feature/name

# Switch branch
git checkout branch-name
```

#### Commit Operations
```bash
# Stage all changes
git add -A

# Stage specific file
git add path/to/file

# Commit with message
git commit -m "type: description"

# Amend last commit
git commit --amend -m "new message"

# Add forgotten file to last commit
git add forgotten_file
git commit --amend --no-edit
```

#### Remote Operations
```bash
# Push new branch
git push -u origin feature/name

# Push updates
git push

# Pull latest changes
git pull origin main

# Fetch without merging
git fetch origin

# Delete remote branch
git push origin --delete branch-name
```

#### Collaboration Commands
```bash
# Create pull request (GitHub CLI)
gh pr create --title "Title" --body "Description"

# Merge PR
gh pr merge --squash --delete-branch

# View PR status
gh pr view

# Update branch with main
git checkout main && git pull
git checkout feature/name
git merge main
```

### Recovery Commands
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Discard all local changes
git checkout -- .

# Remove untracked files
git clean -fd

# Find lost commits
git reflog

# Abort merge in progress
git merge --abort

# Fix detached HEAD
git checkout main
```

## Prerequisites Extracted

### System Requirements
- **OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Permissions**: Administrator/sudo access
- **Storage**: 4GB free disk space
- **Internet**: Stable connection

### Tool Requirements
| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Git | 2.30+ | Version control |
| Python | 3.10+ | Programming language |
| UV | 0.4+ | Package manager |

### Time Requirements
- Quick Start: 5 minutes
- Full Setup: 15-20 minutes
- Workflow Learning: 20 minutes
- Practice Exercises: 30 minutes
- **Total**: 45-75 minutes

## Error Messages and Solutions

### Authentication Errors
| Error | Solution | Time |
|-------|----------|------|
| `Remote: Support for password authentication was removed` | Use personal access token or SSH | 5 min |
| `Permission denied (publickey)` | Add SSH key: `ssh-add ~/.ssh/id_ed25519` | 2 min |
| `authentication failed` | Check credentials: `git config credential.helper` | 5 min |

### Git Workflow Errors
| Error | Solution | Time |
|-------|----------|------|
| `Automatic merge failed` | Resolve conflicts manually, then `git add` and `git commit` | 10 min |
| `Updates were rejected` | Pull first: `git pull origin main` | 2 min |
| `Failed to push some refs` | Set upstream: `git push -u origin branch` | 1 min |
| `divergent branches` | Rebase: `git pull --rebase origin main` | 3 min |

### Environment Errors
| Error | Solution | Time |
|-------|----------|------|
| `command not found` | Restart terminal or check PATH | 2 min |
| `No module named 'package'` | Activate venv and reinstall: `uv pip install package` | 2 min |
| `.venv\Scripts\activate not found` | Create venv first: `uv venv` | 1 min |
| `Python version too old` | Install Python 3.10+: see setup commands | 10 min |

### Common Issues
| Issue | Check | Fix |
|-------|-------|-----|
| Wrong branch | `git branch` | `git checkout correct-branch` |
| Uncommitted changes | `git status` | Commit or stash: `git stash` |
| Virtual env not active | No `(.venv)` in prompt | Activate: see setup commands |
| SSL certificate error | Corporate network | Set proxy or update certificates |

## Validation Steps Extracted

### Environment Validation
```bash
# All tools installed
git --version && python --version && uv --version

# Git configured
git config --global user.name
git config --global user.email

# Virtual environment active
which python | grep .venv

# Dependencies installed
uv pip list | grep -E "mkdocs|pytest|ruff"
```

### Workflow Validation
```bash
# Repository status
git status  # Expected: "nothing to commit, working tree clean"

# Branch tracking
git branch -vv  # Shows tracking relationships

# Remote configuration
git remote -v  # Shows fetch/push URLs

# Latest changes
git log --oneline -5  # Shows recent commits
```

### PR Readiness Validation
```bash
# Clean working directory
git status --porcelain  # Expected: empty output

# All tests pass
pytest  # Expected: all green

# Code quality
ruff check .  # Expected: no errors

# Type checking
mypy .  # Expected: no errors
```

## Key Concepts (for glossary)

**Repository**: Complete project history and files
**Clone**: Local copy of remote repository
**Branch**: Isolated development workspace
**Commit**: Saved snapshot of changes
**Stage**: Mark changes for next commit
**Push**: Upload commits to remote
**Pull**: Download and merge remote changes
**PR/Pull Request**: Proposed changes for review
**Merge**: Combine branches
**Conflict**: Competing changes requiring resolution
**Remote**: Server-hosted repository (GitHub)
**Origin**: Default remote repository name
**HEAD**: Current branch/commit pointer
**Upstream**: Original repository (for forks)
**Fast-forward**: Linear history merge
**Rebase**: Rewrite commit history
**Cherry-pick**: Apply specific commits
**Stash**: Temporary storage for changes

## Security Warnings

- Never commit sensitive data (passwords, tokens, keys)
- Use `.gitignore` for private files
- Review changes before committing: `git diff`
- Use SSH keys or tokens, not passwords
- Verify repository URL before cloning

## Critical Notes

- Always pull before starting new work
- Commit frequently with clear messages
- One feature per branch
- Delete branches after merging
- Keep commits focused and atomic
- Test before pushing
- Review PR feedback promptly