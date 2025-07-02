# Quick Start 🚀

<div class="progress-tracker">
<span class="current">[●] Quick Start</span> → <span class="upcoming">[ ] Overview</span> → <span class="upcoming">[ ] Concepts</span> → <span class="upcoming">[ ] Setup</span> → <span class="upcoming">[ ] Workflow</span> → <span class="upcoming">[ ] Practice</span> → <span class="upcoming">[ ] Reference</span>
</div>

**Goal**: Go from zero to pull request in 5 minutes. No fluff. Just commands.

## 30 Seconds: Check Prerequisites

```bash
git --version       # Need 2.30+
python --version    # Need 3.10+
```

Missing? Install:
- Git: [git-scm.com](https://git-scm.com/downloads)
- Python: [python.org](https://python.org/downloads/)

## 1 Minute: Setup

```bash
# Clone
git clone https://github.com/pahansen95/py-project-tmpl.git
cd py-project-tmpl

# Configure Git (if needed)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Install UV (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Mac/Linux
# OR
irm https://astral.sh/uv/install.ps1 | iex       # Windows PowerShell

# Setup Python environment
uv venv
source .venv/bin/activate  # Mac/Linux
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e ".[dev]"
```

## 2 Minutes: Make Changes

```bash
# Create branch
git checkout -b fix/typo-in-readme

# Make your change
echo "Fixed typo" >> README.md

# Commit
git add README.md
git commit -m "fix: Correct typo in README"
```

## 1.5 Minutes: Share

```bash
# Push
git push -u origin fix/typo-in-readme

# Create PR
echo "Visit the link above and click 'Create pull request'"
```

**OR** with GitHub CLI:
```bash
gh pr create --title "Fix typo in README" --body "Quick fix"
```

## Done! 🎉

**Total time**: ~5 minutes

**What you did**:
1. ✓ Set up complete dev environment
2. ✓ Made a change
3. ✓ Created a pull request

**Next**:
- Wait for review
- Make bigger changes
- Read the [full guide](index.md) (when you have time)

---

## Even Faster Next Time

Save this for your next contribution:

```bash
# Start fresh
git checkout main && git pull
git checkout -b feature/new-thing

# Work
# ... make changes ...

# Ship it
git add .
git commit -m "feat: Add new thing"
git push -u origin feature/new-thing
```

---

## Common Issues (30-second fixes)

**"Permission denied"**
```bash
# Use SSH instead
git remote set-url origin git@github.com:pahansen95/py-project-tmpl.git
```

**"Command not found: uv"**
```bash
# Restart terminal or add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

**"Virtual environment not activated"**
```bash
# You'll see (.venv) in prompt when active
source .venv/bin/activate  # Try again
```

---

*Want details? See the [complete guide](index.md). Just want to code? You're all set!*