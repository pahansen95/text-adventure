# Quick Reference

<div class="progress-tracker">
<span class="completed">[✓] Quick Start</span> → <span class="completed">[✓] Overview</span> → <span class="completed">[✓] Concepts</span> → <span class="completed">[✓] Setup</span> → <span class="completed">[✓] Workflow</span> → <span class="completed">[✓] Practice</span> → <span class="current">[●] Reference</span>
</div>

## Quick Navigation

[🔧 Commands](#command-quick-reference) | [🐛 Troubleshooting](#common-issues--solutions) | [⚙️ Git Config](#git-configurations) | [⌨️ Shortcuts](#keyboard-shortcuts) | [🔗 Links](#quick-links) | [🚨 Emergency](#emergency-commands)

---

## Command Quick Reference

### 📋 Essential Git Operations

| Operation | GitHub Desktop | Command Line | VS Code |
|-----------|---------------|--------------|---------|
| **Clone repository** | File → Clone Repository | `git clone [url]` | Ctrl+Shift+P → Git: Clone |
| **Create branch** | Current Branch → New Branch | `git checkout -b [name]` | Click branch → Create new |
| **Switch branch** | Current Branch → Select | `git checkout [name]` | Click branch name → Select |
| **Update from remote** | Fetch origin → Pull | `git pull` | Sync button (↻) |
| **Stage changes** | ☑️ Check boxes | `git add .` | Click + in Source Control |
| **Stage specific file** | ☑️ Check file box | `git add [file]` | Click + next to file |
| **Unstage changes** | ☐ Uncheck boxes | `git reset` | Click - next to file |
| **Commit** | Type message → Commit | `git commit -m "[msg]"` | Type → Ctrl+Enter |
| **Push** | Push origin | `git push` | Sync button (↻) |
| **View history** | History tab | `git log --oneline` | Timeline view |
| **Discard changes** | Right-click → Discard | `git checkout -- [file]` | Discard button (↶) |

### 🐍 Python/UV Commands

| Task | Command | Description |
|------|---------|-------------|
| **Virtual Environment** |||
| Create venv | `uv venv` | Creates .venv directory |
| Activate (Win) | `.venv\Scripts\activate` | Activates virtual environment |
| Activate (Mac/Linux) | `source .venv/bin/activate` | Activates virtual environment |
| Deactivate | `deactivate` | Exits virtual environment |
| **Package Management** |||
| Install package | `uv pip install [package]` | Installs single package |
| Install from file | `uv pip install -r requirements.txt` | Installs from requirements |
| Install editable | `uv pip install -e .` | Installs project in dev mode |
| List packages | `uv pip list` | Shows installed packages |
| Show package info | `uv pip show [package]` | Details about package |
| Uninstall | `uv pip uninstall [package]` | Removes package |
| **Project Commands** |||
| Run tests | `pytest` | Runs all tests |
| Run specific test | `pytest tests/test_file.py` | Runs single test file |
| Format code | `ruff format .` | Auto-formats Python code |
| Check code | `ruff check .` | Checks for code issues |
| Type check | `mypy .` | Runs type checking |
| Build docs | `mkdocs build` | Builds documentation |
| Serve docs | `mkdocs serve` | Runs local doc server |

### 🌿 Branch Operations

| Task | Command | Description |
|------|---------|-------------|
| **Branch Management** |||
| List branches | `git branch` | Shows local branches |
| List all branches | `git branch -a` | Shows local + remote |
| Create branch | `git branch [name]` | Creates without switching |
| Switch branch | `git checkout [name]` | Changes to branch |
| Create & switch | `git checkout -b [name]` | Creates and switches |
| Delete branch | `git branch -d [name]` | Deletes merged branch |
| Force delete | `git branch -D [name]` | Deletes unmerged branch |
| Rename branch | `git branch -m [new-name]` | Renames current branch |
| **Remote Branches** |||
| Push new branch | `git push -u origin [name]` | First push of branch |
| Push updates | `git push` | Push commits |
| Delete remote | `git push origin --delete [name]` | Removes from GitHub |
| Track remote | `git checkout --track origin/[name]` | Creates local from remote |
| Update branch list | `git fetch --prune` | Syncs branch list |

### 📊 Status & History

| Task | Command | Description |
|------|---------|-------------|
| **Status Commands** |||
| Check status | `git status` | Shows working tree status |
| Short status | `git status -s` | Compact status view |
| Show changes | `git diff` | Unstaged changes |
| Show staged | `git diff --staged` | Staged changes |
| Show branch diff | `git diff main..HEAD` | Branch differences |
| **History Commands** |||
| View history | `git log` | Full commit history |
| Compact history | `git log --oneline` | One line per commit |
| Graph view | `git log --graph --all` | Visual branch history |
| Filter by author | `git log --author="name"` | Specific person's commits |
| Search commits | `git log --grep="text"` | Find in commit messages |
| File history | `git log --follow [file]` | Track file changes |
| Show commit | `git show [hash]` | Details of specific commit |

## Common Issues & Solutions

### 🔐 Authentication Problems

??? error "Remote: Support for password authentication was removed"
    **Problem**: GitHub no longer accepts passwords for Git operations
    
    **Solutions**:
    
    **Option 1: Use Personal Access Token**
    ```bash
    # Generate token at github.com/settings/tokens
    # Use token as password when prompted
    git remote set-url origin https://[TOKEN]@github.com/[USER]/[REPO].git
    ```
    
    **Option 2: Set up SSH (Recommended)**
    ```bash
    # Generate SSH key
    ssh-keygen -t ed25519 -C "your.email@example.com"
    
    # Start SSH agent
    eval "$(ssh-agent -s)"
    
    # Add key to agent
    ssh-add ~/.ssh/id_ed25519
    
    # Copy public key
    cat ~/.ssh/id_ed25519.pub
    # Add to GitHub: Settings → SSH Keys
    
    # Test connection
    ssh -T git@github.com
    
    # Change remote to SSH
    git remote set-url origin git@github.com:USER/REPO.git
    ```

??? error "Permission denied (publickey)"
    **Problem**: SSH key not recognized
    
    **Check SSH agent**:
    ```bash
    # List loaded keys
    ssh-add -l
    
    # Add your key
    ssh-add ~/.ssh/id_ed25519
    
    # Verify GitHub connection
    ssh -T git@github.com
    ```

### 🔀 Merge Conflicts

??? error "Automatic merge failed; fix conflicts and commit"
    **Problem**: Git can't automatically merge changes
    
    **Step-by-step resolution**:
    ```bash
    # 1. See conflicted files
    git status
    
    # 2. Open each conflicted file
    # Look for markers:
    <<<<<<< HEAD
    Your changes
    =======
    Their changes
    >>>>>>> branch-name
    
    # 3. Edit to resolve
    # Remove all <<<, ===, >>> markers
    # Keep the code you want
    
    # 4. Stage resolved files
    git add [resolved-file]
    
    # 5. Complete merge
    git commit -m "Resolve merge conflicts"
    
    # 6. Push changes
    git push
    ```
    
    **Prevention**:
    - Pull before starting work
    - Keep branches short-lived
    - Communicate with team
    - Make small, focused commits

### 🌿 Wrong Branch Issues

??? error "Made changes on wrong branch"
    **Problem**: Started work on main instead of feature branch
    
    **Solution 1: Stash and switch**
    ```bash
    # Save changes temporarily
    git stash
    
    # Create/switch to correct branch
    git checkout -b feature/correct-branch
    
    # Apply saved changes
    git stash pop
    ```
    
    **Solution 2: Create branch from current state**
    ```bash
    # Create branch with current changes
    git checkout -b feature/correct-branch
    
    # Changes are now on new branch
    git add .
    git commit -m "Move work to feature branch"
    
    # Clean up main branch
    git checkout main
    git reset --hard origin/main
    ```

??? error "Committed to wrong branch"
    **Problem**: Committed to main instead of feature branch
    
    **If not pushed**:
    ```bash
    # Create branch from current state
    git branch feature/correct-branch
    
    # Reset main to previous state
    git reset --hard HEAD~1
    
    # Switch to feature branch
    git checkout feature/correct-branch
    ```
    
    **If already pushed** (requires force push):
    ```bash
    # Create branch with the commit
    git branch feature/correct-branch
    
    # Reset main
    git reset --hard HEAD~1
    
    # Force push (coordinate with team!)
    git push --force-with-lease origin main
    
    # Push feature branch
    git checkout feature/correct-branch
    git push -u origin feature/correct-branch
    ```

### 🐍 Virtual Environment Issues

??? error "Command not found: pytest/ruff/mypy"
    **Problem**: Virtual environment not activated
    
    **Check activation**:
    ```bash
    # Should see (.venv) in prompt
    which python
    # Should show: /path/to/project/.venv/bin/python
    ```
    
    **Activate environment**:
    === "Windows"
        ```powershell
        .venv\Scripts\activate
        ```
    === "Mac/Linux"
        ```bash
        source .venv/bin/activate
        ```

??? error "No module named 'package_name'"
    **Problem**: Package not installed in virtual environment
    
    **Solutions**:
    ```bash
    # Ensure venv is activated
    source .venv/bin/activate  # or Windows equivalent
    
    # Install missing package
    uv pip install package_name
    
    # Or reinstall all dependencies
    uv pip install -e ".[dev,docs]"
    ```

### 📤 Push/Pull Problems

??? error "Updates were rejected because the remote contains work"
    **Problem**: Remote has changes you don't have locally
    
    **Solution**:
    ```bash
    # Get remote changes
    git pull origin [branch-name]
    
    # If conflicts, resolve them
    # Then push again
    git push
    ```
    
    **Alternative: Rebase**
    ```bash
    # Rebase your changes on top
    git pull --rebase origin [branch-name]
    
    # Push changes
    git push
    ```

??? error "Failed to push some refs"
    **Problem**: Various push failures
    
    **Check branch tracking**:
    ```bash
    # Set upstream branch
    git push -u origin [branch-name]
    ```
    
    **Check permissions**:
    ```bash
    # Verify you have push access
    git remote -v
    # Should show (push) for origin
    ```

## Git Configurations

### 🌍 Essential Global Settings

```bash
# User Identity (Required)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Default Branch Name
git config --global init.defaultBranch main

# Line Endings
git config --global core.autocrlf true      # Windows
git config --global core.autocrlf input     # Mac/Linux

# Colors
git config --global color.ui auto

# Default Editor
git config --global core.editor "code --wait"    # VS Code
git config --global core.editor "nano"           # Nano
git config --global core.editor "vim"            # Vim

# Merge Strategy
git config --global pull.rebase false

# Push Behavior
git config --global push.default current
```

### 🚀 Productivity Aliases

```bash
# Status & Information
git config --global alias.st "status -sb"
git config --global alias.ll "log --oneline -10"
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"

# Common Operations
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm commit
git config --global alias.cp cherry-pick

# Staging Shortcuts
git config --global alias.a "add ."
git config --global alias.aa "add --all"
git config --global alias.ap "add -p"

# Diff Shortcuts
git config --global alias.d diff
git config --global alias.ds "diff --staged"
git config --global alias.dt "difftool"

# Undo Operations
git config --global alias.undo "reset --soft HEAD~1"
git config --global alias.unstage "reset HEAD --"
git config --global alias.discard "checkout --"

# Branch Operations
git config --global alias.bd "branch -d"
git config --global alias.bD "branch -D"
git config --global alias.branches "branch -a"
git config --global alias.recent "branch --sort=-committerdate"

# Utility Commands
git config --global alias.aliases "config --get-regexp alias"
git config --global alias.whoami "config user.email"
git config --global alias.contributors "shortlog --summary --numbered"
```

### 📁 Project-Specific Settings

```bash
# Override user for specific project
cd /path/to/project
git config user.email "work.email@company.com"

# Project-specific aliases
git config alias.deploy "push production main"
git config alias.staging "push staging develop"

# Ignore file mode changes
git config core.filemode false

# Set merge strategy for specific files
echo "*.generated merge=ours" >> .gitattributes
```

## Keyboard Shortcuts

### ⌨️ VS Code Shortcuts

| Action | Windows/Linux | macOS | Description |
|--------|--------------|-------|-------------|
| **General** ||||
| Command Palette | `Ctrl+Shift+P` | `Cmd+Shift+P` | Access all commands |
| Quick Open | `Ctrl+P` | `Cmd+P` | Open files quickly |
| Terminal | `Ctrl+`` | `Cmd+`` | Toggle terminal |
| Sidebar | `Ctrl+B` | `Cmd+B` | Toggle sidebar |
| **Source Control** ||||
| Source Control View | `Ctrl+Shift+G` | `Cmd+Shift+G` | Open Git panel |
| Stage File | `Ctrl+Enter` | `Cmd+Enter` | Stage current file |
| Commit | `Ctrl+Enter` | `Cmd+Enter` | Commit (in message box) |
| **Editing** ||||
| Multiple Cursors | `Alt+Click` | `Option+Click` | Add cursor |
| Select Next Match | `Ctrl+D` | `Cmd+D` | Select next occurrence |
| Move Line | `Alt+↑/↓` | `Option+↑/↓` | Move line up/down |
| Copy Line | `Alt+Shift+↑/↓` | `Option+Shift+↑/↓` | Duplicate line |
| Comment Line | `Ctrl+/` | `Cmd+/` | Toggle comment |
| **Navigation** ||||
| Go to Definition | `F12` | `F12` | Jump to definition |
| Go Back | `Alt+←` | `Ctrl+-` | Navigate back |
| Go to Line | `Ctrl+G` | `Cmd+G` | Jump to line number |
| Find in Files | `Ctrl+Shift+F` | `Cmd+Shift+F` | Search across files |

### 🖱️ GitHub Desktop Shortcuts

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| **Repository** |||
| Clone Repository | `Ctrl+Shift+O` | `Cmd+Shift+O` |
| Create Branch | `Ctrl+Shift+N` | `Cmd+Shift+N` |
| **Changes** |||
| Commit | `Ctrl+Enter` | `Cmd+Enter` |
| Push | `Ctrl+P` | `Cmd+P` |
| Pull | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| Fetch | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| **View** |||
| Toggle Changes/History | `Ctrl+1/2` | `Cmd+1/2` |
| Repository List | `Ctrl+T` | `Cmd+T` |
| Preferences | `Ctrl+,` | `Cmd+,` |

### 🖥️ Terminal Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| **Navigation** |||
| Previous Command | `↑` | Cycle through history |
| Search History | `Ctrl+R` | Search command history |
| Beginning of Line | `Ctrl+A` | Jump to start |
| End of Line | `Ctrl+E` | Jump to end |
| **Editing** |||
| Clear Screen | `Ctrl+L` | Clear terminal |
| Cancel Command | `Ctrl+C` | Stop running command |
| Delete Word | `Ctrl+W` | Delete word backward |
| **Tab Completion** |||
| Complete | `Tab` | Auto-complete |
| Show Options | `Tab Tab` | Show all options |

## Environment Variables

### 🔧 Development Environment

```bash
# Python Path
export PYTHONPATH="${PYTHONPATH}:/path/to/project"

# Virtual Environment
export VIRTUAL_ENV="/path/to/.venv"
export PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Development Settings
export DEBUG=true
export ENV=development
export LOG_LEVEL=DEBUG

# Project Specific
export PROJECT_NAME="py-project-tmpl"
export PROJECT_ROOT="/path/to/project"
```

### 🌐 Git Environment

```bash
# Git Configuration
export GIT_EDITOR="code --wait"
export GIT_MERGE_AUTOEDIT=no

# GitHub CLI
export GITHUB_TOKEN="your_token_here"
export GH_HOST="github.com"

# Git Performance
export GIT_TRACE_PERFORMANCE=1
export GIT_TRACE_SETUP=1
```

### 🪟 Windows Specific

```powershell
# PowerShell Profile
$env:PYTHONPATH = "C:\path\to\project"
$env:VIRTUAL_ENV = "C:\path\to\.venv"
$env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH"

# Git Bash on Windows
export MSYS=winsymlinks:nativestrict
```

## Quick Links

### 📚 Documentation

| Resource | Description | Link |
|----------|-------------|------|
| **Project** |||
| Project README | Main project documentation | [View](https://github.com/pahansen95/py-project-tmpl) |
| API Documentation | Auto-generated API docs | [View](../api/index.md) |
| Contributing Guide | How to contribute | [View](../../CONTRIBUTING.md) |
| **Python** |||
| Python Docs | Official Python documentation | [python.org](https://docs.python.org) |
| PEP 8 Style Guide | Python code style | [View](https://pep8.org) |
| Type Hints | Python typing guide | [View](https://docs.python.org/3/library/typing.html) |
| **Git** |||
| Pro Git Book | Comprehensive Git guide | [git-scm.com](https://git-scm.com/book) |
| GitHub Docs | GitHub platform guide | [docs.github.com](https://docs.github.com) |
| Git Cheat Sheet | Quick command reference | [View](https://education.github.com/git-cheat-sheet-education.pdf) |

### 🛠️ Tools

| Tool | Purpose | Download |
|------|---------|----------|
| **Development** |||
| Git | Version control | [git-scm.com](https://git-scm.com/downloads) |
| Python | Programming language | [python.org](https://python.org/downloads/) |
| UV | Package manager | [github.com/astral-sh/uv](https://github.com/astral-sh/uv) |
| **Editors** |||
| VS Code | Code editor | [code.visualstudio.com](https://code.visualstudio.com) |
| PyCharm | Python IDE | [jetbrains.com](https://www.jetbrains.com/pycharm/) |
| GitHub Desktop | Git GUI | [desktop.github.com](https://desktop.github.com) |
| **Utilities** |||
| Windows Terminal | Modern terminal | [Microsoft Store](https://aka.ms/terminal) |
| iTerm2 | macOS terminal | [iterm2.com](https://iterm2.com) |
| Postman | API testing | [postman.com](https://www.postman.com) |

### 🆘 Help & Support

| Resource | Description | Link |
|----------|-------------|------|
| **Project Help** |||
| Issues | Report bugs & request features | [GitHub Issues](https://github.com/pahansen95/py-project-tmpl/issues) |
| Discussions | Ask questions & share ideas | [GitHub Discussions](https://github.com/pahansen95/py-project-tmpl/discussions) |
| **Community** |||
| Stack Overflow | Programming Q&A | [Git Tag](https://stackoverflow.com/questions/tagged/git) |
| r/git | Reddit community | [reddit.com/r/git](https://reddit.com/r/git) |
| Dev.to | Developer articles | [dev.to/t/git](https://dev.to/t/git) |

## Emergency Commands

### 🚨 Undo Operations

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Undo commit and push (CAREFUL!)
git reset --hard HEAD~1
git push --force-with-lease

# Restore deleted file
git checkout HEAD~1 -- path/to/file

# Undo git add
git reset

# Undo specific file staging
git reset HEAD path/to/file
```

### 🔥 Fix Mistakes

```bash
# Discard all local changes
git checkout -- .

# Remove untracked files
git clean -fd

# Remove untracked files and directories (dry run)
git clean -fdn

# Fix last commit message
git commit --amend -m "New message"

# Add forgotten file to last commit
git add forgotten_file
git commit --amend --no-edit

# Remove file from Git but keep locally
git rm --cached file_to_keep.txt
```

### 💾 Recovery Operations

```bash
# Find lost commits
git reflog

# Restore lost commit
git checkout -b recovery_branch [commit_hash]

# Show what was in deleted file
git show HEAD~1:path/to/deleted_file.txt

# Find which commit deleted a file
git log --diff-filter=D --summary | grep delete

# Restore entire project state
git checkout [commit_hash] -- .
```

### ⚡ Quick Fixes

```bash
# Switch branches with uncommitted changes
git stash
git checkout other-branch
git stash pop

# Abort merge in progress
git merge --abort

# Abort rebase in progress
git rebase --abort

# Fix "detached HEAD"
git checkout main

# Update branch after force push
git fetch origin
git reset --hard origin/[branch-name]
```

### 🆘 Last Resort

```bash
# Complete reset to remote state
git fetch origin
git reset --hard origin/main
git clean -fd

# Clone fresh if all else fails
cd ..
mv project-dir project-dir-backup
git clone [repository-url]
```

---

## Pro Tips 💡

### Daily Workflow

```bash
# Morning routine
git checkout main
git pull origin main
git checkout -b feature/todays-work

# Before lunch commit
git add .
git commit -m "WIP: Morning progress"

# End of day
git add .
git commit -m "feat: Complete feature implementation"
git push -u origin feature/todays-work
```

### Time Savers

1. **Use aliases** - Set up shortcuts for common commands
2. **Tab completion** - Let terminal complete file/branch names
3. **GUI tools** - Use for complex operations like interactive rebase
4. **Templates** - Create commit message and PR templates
5. **Hooks** - Automate checks with pre-commit hooks

### Best Practices

- 🔄 Pull before push
- 📝 Write clear commit messages
- 🌿 Keep branches focused
- 🧹 Delete merged branches
- 💾 Commit often
- 🔍 Review before committing
- 🏷️ Use conventional commits
- 📊 Check status frequently

---

*Remember: This reference is always here when you need it. Bookmark it for quick access during development!*