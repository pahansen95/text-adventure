# Environment Setup

<div class="progress-tracker">
<span class="completed">[✓] Overview (10 min)</span> → <span class="current">[●] Setup (15 min)</span> → <span class="upcoming">[ ] Workflow (20 min)</span> → <span class="upcoming">[ ] Reference</span>
<div class="progress-time">Total: 45 min | Elapsed: 10 min | Remaining: 35 min</div>
</div>

## Objectives
- Install Git, Python, and UV package manager
- Configure development environment
- Verify all tools function correctly

## Prerequisites
| Component | Requirement | Verification |
|-----------|-------------|--------------|
| OS | Windows 10+, macOS 10.15+, Linux | `uname -a` |
| Access | Administrator/sudo | Required |
| Storage | 4GB free | `df -h` |
| Internet | Stable connection | 500MB download |

## Automated Setup (5 minutes)

### Windows
```powershell
# PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
irm https://raw.githubusercontent.com/pahansen95/py-project-tmpl/main/scripts/setup-welcome.ps1 | iex
```

### macOS/Linux
```bash
curl -sSL https://raw.githubusercontent.com/pahansen95/py-project-tmpl/main/scripts/setup-welcome.sh | bash
```

**Script Actions**: Installs Git/Python/UV, configures environment, creates virtual environment, installs dependencies.

## Manual Setup (15 minutes)

### Install Required Tools

| Tool | Windows | macOS | Linux |
|------|---------|-------|-------|
| Git | `winget install Git.Git` | `brew install git` | `apt install git` |
| Python | `winget install Python.Python.3.12` | `brew install python@3.12` | `apt install python3.12` |
| UV | `irm https://astral.sh/uv/install.ps1 \| iex` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Same as macOS |

### Configure Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
git config --global core.autocrlf true    # Windows
git config --global core.autocrlf input   # macOS/Linux
```

### Project Setup
```bash
# Clone and enter project
git clone https://github.com/pahansen95/py-project-tmpl.git
cd py-project-tmpl

# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows

# Install dependencies
uv pip install -e ".[dev,docs]"
```

## Validation Checkpoint

Execute validation sequence (2 minutes):

### System Validation
```bash
# Check all tools (30 seconds)
echo "=== Tool Versions ===" && \
git --version && \
python --version && \
uv --version && \
echo "✓ All tools installed"
```

### Configuration Validation
```bash
# Check Git config (30 seconds)
echo "=== Git Configuration ===" && \
echo "Name: $(git config --global user.name)" && \
echo "Email: $(git config --global user.email)" && \
echo "Branch: $(git config --global init.defaultBranch)" && \
echo "✓ Git configured"
```

### Environment Validation
```bash
# Check Python environment (30 seconds)
echo "=== Python Environment ===" && \
python -c "import sys; print(f'Python: {sys.executable}')" && \
python -c "import sys; print('✓ Venv active' if '.venv' in sys.executable else '✗ Venv NOT active')" && \
uv pip list | grep -q pytest && echo "✓ Dependencies installed"
```

### Project Validation
```bash
# Final check (30 seconds)
test -f pyproject.toml && echo "✓ Project files found" && \
test -d .git && echo "✓ Git repository initialized" && \
git remote -v | grep -q origin && echo "✓ Remote configured"
```

**Expected**: All validations show ✓ checkmarks

## Common Issues

| Issue | Solution | Time |
|-------|----------|------|
| `command not found` | Restart terminal or add to PATH | 2 min |
| `permission denied` | Run as Administrator/sudo | 1 min |
| `SSL certificate error` | Set proxy or update certificates | 5 min |
| `venv activation fails` | Windows: `Set-ExecutionPolicy RemoteSigned` | 2 min |

---
**Next**: [Development Workflow](workflow.md) • **Time Investment**: 20 minutes