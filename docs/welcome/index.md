# Python Project Template Documentation

<div class="progress-tracker">
<span class="current">[●] Overview (10 min)</span> → <span class="upcoming">[ ] Setup (15 min)</span> → <span class="upcoming">[ ] Workflow (20 min)</span> → <span class="upcoming">[ ] Reference</span>
<div class="progress-time">Total: 45 min | Elapsed: 0 min | Remaining: 45 min</div>
</div>

## Objectives
- Execute complete development workflow within 45 minutes
- Configure Python development environment
- Submit code changes via pull request

## Prerequisites

| Requirement | Minimum Version | Verification |
|-------------|----------------|--------------|
| Operating System | Windows 10+, macOS 10.15+, Linux | `uname -a` |
| Disk Space | 4GB free | `df -h` |
| Internet | Stable connection | Download ~500MB |
| Access Rights | Administrator/sudo | Required for installation |

## Fast Track (5 minutes)

### Prerequisites Check (30 seconds)
```bash
git --version       # Required: 2.30+
python --version    # Required: 3.10+
```

### Environment Setup (2 minutes)
```bash
# Clone repository
git clone https://github.com/pahansen95/py-project-tmpl.git && cd py-project-tmpl

# Configure Git identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh      # Linux/macOS
irm https://astral.sh/uv/install.ps1 | iex           # Windows PowerShell

# Create Python environment
uv venv && source .venv/bin/activate                 # Linux/macOS
uv venv && .venv\Scripts\activate                    # Windows

# Install dependencies
uv pip install -e ".[dev]"
```

### Submit Changes (2.5 minutes)
```bash
# Create feature branch
git checkout -b feature/your-change

# Make changes
echo "# Your change" >> README.md

# Commit and push
git add README.md
git commit -m "feat: Add your change"
git push -u origin feature/your-change
```

**Output**: URL for creating pull request

## Navigation

| Section | Purpose | Time Investment |
|---------|---------|-----------------|
| [Setup](setup.md) | Detailed environment configuration | 15 minutes |
| [Workflow](workflow.md) | Complete development process | 20 minutes |
| [Reference](reference.md) | Commands and troubleshooting | As needed |

## System Requirements

### Supported Platforms
- **Windows**: 10/11 (64-bit), PowerShell 5.1+
- **macOS**: 10.15+ (Catalina or later)
- **Linux**: Ubuntu 20.04+, Debian 11+, Fedora 34+, RHEL 8+

### Required Tools
| Tool | Purpose | Installation Check |
|------|---------|-------------------|
| Git 2.30+ | Version control | `git --version` |
| Python 3.10+ | Programming language | `python --version` |
| UV 0.4+ | Package manager | `uv --version` |

## Validation Checkpoint

Execute validation sequence:
```bash
git --version && python --version && uv --version
```
**Expected**: All commands return version numbers
**Time**: 30 seconds

## Common Errors

| Error | Solution | Time |
|-------|----------|------|
| `command not found` | Restart terminal or check PATH | 2 min |
| `permission denied` | Use sudo/admin privileges | 1 min |
| `SSL certificate error` | Configure proxy or update certs | 5 min |

---
**Next**: [Environment Setup](setup.md) • **Time Investment**: 15 minutes