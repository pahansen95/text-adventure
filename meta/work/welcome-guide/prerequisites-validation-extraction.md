# Prerequisites and Validation Steps Extraction

## Prerequisites by Page

### System-Level Prerequisites (from all pages)

**Hardware Requirements:**
- Storage: 4GB free disk space minimum
- Internet: Stable connection (~500MB downloads)
- RAM: 4GB minimum (8GB recommended)

**Operating System:**
- Windows 10/11 (64-bit)
- macOS 10.15+ (Catalina or later)
- Linux: Ubuntu 20.04+, Debian 11+, Fedora 34+, RHEL 8+, Arch (current)

**Access Requirements:**
- Administrator/sudo access for tool installation
- GitHub account for collaboration
- Terminal/command line access

### Tool Prerequisites

**Core Tools Required:**
| Tool | Minimum Version | Check Command | Purpose |
|------|----------------|---------------|---------|
| Git | 2.30+ | `git --version` | Version control |
| Python | 3.10+ | `python --version` | Programming language |
| UV | 0.4+ | `uv --version` | Package manager |

**Optional Tools:**
| Tool | Purpose | Check Command |
|------|---------|---------------|
| GitHub CLI | PR management | `gh --version` |
| VS Code | Editor | `code --version` |
| GitHub Desktop | GUI Git client | GUI application |

### Page-Specific Prerequisites

**Setup Page:**
- Time: 15-20 minutes
- Fresh terminal session
- Internet connection for downloads

**Workflow Page:**
- Completed setup (environment configured)
- Repository cloned
- Virtual environment activated
- Basic Git knowledge

**Practice Page:**
- All tools installed and verified
- Git configured with user identity
- Python virtual environment working
- 30-60 minutes available

## Validation Steps by Stage

### Initial System Validation
```bash
# Operating system check
uname -a  # Linux/macOS
systeminfo | findstr /B /C:"OS Name"  # Windows

# Permissions check
sudo echo "Admin access confirmed"  # Linux/macOS
net session >nul 2>&1 && echo Admin || echo Not Admin  # Windows

# Disk space check
df -h .  # Linux/macOS
fsutil volume diskfree C:  # Windows
```

### Post-Installation Validation

**Tool Installation:**
```bash
# Verify all tools installed
git --version && python --version && uv --version
# Expected: All return version numbers

# Check tool locations
which git python uv  # Linux/macOS
where git python uv  # Windows
```

**Git Configuration:**
```bash
# Identity configured
git config --global user.name
git config --global user.email
# Expected: Your name and email

# Core settings
git config --global --list | grep -E "core|init"
# Expected: Shows autocrlf, defaultBranch settings
```

### Environment Setup Validation

**Virtual Environment:**
```bash
# Environment created
test -d .venv && echo "✓ Virtual environment exists" || echo "✗ No .venv found"

# Environment activated
python -c "import sys; print('✓ venv active' if '.venv' in sys.executable else '✗ venv not active')"

# Correct Python version
python -c "import sys; v=sys.version_info; print(f'Python {v.major}.{v.minor}.{v.micro}')"
# Expected: 3.10.0 or higher
```

**Package Installation:**
```bash
# Core packages installed
uv pip list | grep -E "mkdocs|pytest|ruff|mypy"
# Expected: All packages listed

# Import test
python -c "import mkdocs, pytest, ruff; print('✓ Core packages importable')"
```

### Repository Validation

**Clone Success:**
```bash
# Repository files present
test -f README.md && test -f pyproject.toml && echo "✓ Repository files found"

# Git initialized
git rev-parse --git-dir >/dev/null 2>&1 && echo "✓ Git repository valid"

# Remote configured
git remote -v | grep -q "origin" && echo "✓ Remote origin configured"
```

**Branch Status:**
```bash
# Current branch
git branch --show-current
# Expected: main or feature branch name

# Clean working directory
test -z "$(git status --porcelain)" && echo "✓ Working directory clean"

# Up to date with remote
git fetch --dry-run 2>&1 | grep -q "up to date" && echo "✓ Up to date with remote"
```

### Workflow Readiness Validation

**Development Environment:**
```bash
# All systems check
python -c "
import subprocess
import sys

checks = {
    'Python': sys.version_info >= (3, 10),
    'Git': subprocess.run(['git', '--version'], capture_output=True).returncode == 0,
    'UV': subprocess.run(['uv', '--version'], capture_output=True).returncode == 0,
    'Venv': '.venv' in sys.executable,
}

for check, passed in checks.items():
    print(f'{check}: {"✓" if passed else "✗"}')

if all(checks.values()):
    print('\n✓ Environment ready for development')
else:
    print('\n✗ Environment setup incomplete')
"
```

### Practice Exercise Validations

**Exercise 1 Checkpoint:**
```bash
# Tools functioning
git status && python -c "print('Hello')" && uv --version
# Expected: All commands execute successfully

# Test file operations
echo "test" > test.txt && git add test.txt && git status | grep -q "new file"
rm test.txt && git status
# Expected: File operations work with Git
```

**Exercise 2 Checkpoint:**
```bash
# Branch created
git branch | grep -q "feature/" && echo "✓ Feature branch exists"

# Changes committed
git log --oneline -1 | grep -q "feat:" && echo "✓ Commit follows conventions"

# Ready to push
git status --porcelain -b | grep -q "ahead" && echo "✓ Commits ready to push"
```

**Exercise 3 Checkpoint:**
```bash
# Branch pushed
git ls-remote --heads origin | grep -q "feature/" && echo "✓ Branch on remote"

# PR can be created
gh pr view >/dev/null 2>&1 || echo "✓ Ready to create PR"
```

### Quick Validation Commands

**One-liner health check:**
```bash
# Full environment validation
echo "=== Environment Check ===" && \
git --version && python --version && uv --version && \
echo "Git user: $(git config --global user.name)" && \
echo "Python path: $(which python)" && \
echo "Venv active: $(test -n "$VIRTUAL_ENV" && echo Yes || echo No)" && \
echo "======================="
```

**Project readiness:**
```bash
# Ready to work check
test -d .git && \
test -d .venv && \
test -n "$VIRTUAL_ENV" && \
git status >/dev/null 2>&1 && \
echo "✓ Ready to develop" || echo "✗ Setup incomplete"
```

## Time Estimates for Validations

| Validation Type | Commands | Time |
|----------------|----------|------|
| System check | OS, permissions, disk | 30 seconds |
| Tool verification | Version checks | 30 seconds |
| Git configuration | User, settings | 1 minute |
| Environment check | Venv, packages | 2 minutes |
| Repository status | Clone, branch, remote | 1 minute |
| Full validation | All checks | 5 minutes |

## Critical Validation Points

**Must Pass Before Proceeding:**
1. Git version 2.30+ installed
2. Python 3.10+ installed
3. UV package manager installed
4. Git user.name and user.email configured
5. Virtual environment created and activated
6. Core dependencies installed
7. Repository cloned successfully

**Warning Indicators:**
- No (.venv) in terminal prompt → Virtual environment not active
- "command not found" → Tool not in PATH or not installed
- "permission denied" → Need admin/sudo access
- "SSL certificate" errors → Network/proxy issues
- Python < 3.10 → Incompatible version

## Platform-Specific Validations

**Windows:**
```powershell
# PowerShell execution policy
Get-ExecutionPolicy
# Expected: RemoteSigned or Unrestricted

# Path separators
python -c "import os; print(os.sep)"
# Expected: \
```

**macOS:**
```bash
# Xcode tools (for Git)
xcode-select -p
# Expected: /Applications/Xcode.app/Contents/Developer or similar

# Homebrew (if used)
brew --version
# Expected: Homebrew 3.x or 4.x
```

**Linux:**
```bash
# Package manager detection
which apt yum dnf pacman zypper 2>/dev/null | head -1
# Expected: Path to package manager

# Python dev headers (for some packages)
python3-config --includes
# Expected: Include paths
```