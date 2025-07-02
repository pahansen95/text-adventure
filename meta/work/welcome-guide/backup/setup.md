# Environment Setup

<div class="progress-tracker">
<span class="completed">[✓] Quick Start</span> → <span class="completed">[✓] Overview</span> → <span class="completed">[✓] Concepts</span> → <span class="current">[●] Setup</span> → <span class="upcoming">[ ] Workflow</span> → <span class="upcoming">[ ] Practice</span> → <span class="upcoming">[ ] Reference</span>
</div>

## Prerequisites Checklist

Before starting setup, verify you have:

- [ ] **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- [ ] **Permissions**: Administrator/sudo access for installing software
- [ ] **Internet**: Stable connection for downloading tools (~500MB)
- [ ] **Storage**: At least 4GB free disk space
- [ ] **Time**: About 15-20 minutes for complete setup

## Quick Setup (Recommended) 🚀

We provide automated setup scripts that handle everything in one command. Choose your operating system:

=== "Windows"
    
    **Option 1: Direct Download and Run**
    ```powershell
    # Run in PowerShell as Administrator
    Set-ExecutionPolicy Bypass -Scope Process -Force
    irm https://raw.githubusercontent.com/pahansen95/py-project-tmpl/main/scripts/setup-welcome.ps1 -OutFile setup.ps1
    .\setup.ps1
    ```
    
    **Option 2: One-Line Install**
    ```powershell
    # Run in PowerShell as Administrator
    irm https://raw.githubusercontent.com/pahansen95/py-project-tmpl/main/scripts/setup-welcome.ps1 | iex
    ```

=== "macOS"
    
    ```bash
    # Run in Terminal
    curl -sSL https://raw.githubusercontent.com/pahansen95/py-project-tmpl/main/scripts/setup-welcome.sh | bash
    ```
    
    **Note**: You may be prompted for your password to install system packages.

=== "Linux"
    
    ```bash
    # Run in Terminal
    curl -sSL https://raw.githubusercontent.com/pahansen95/py-project-tmpl/main/scripts/setup-welcome.sh | bash
    ```
    
    **Supported distributions**: Ubuntu, Debian, Fedora, RHEL, Arch

### What the Script Does

The setup script automatically:

1. **Installs Required Tools**
   - Git (version control)
   - Python 3.10+ (programming language)
   - UV (fast Python package manager)

2. **Configures Your Environment**
   - Sets up Git with your name and email
   - Creates project directories
   - Configures shell integration

3. **Prepares the Project**
   - Creates Python virtual environment
   - Installs project dependencies
   - Verifies everything works

4. **Validates Installation**
   - Checks all tool versions
   - Confirms configurations
   - Reports any issues

## Manual Setup

If you prefer manual installation or the automated script encounters issues:

### Step 1: Install Git

=== "Windows"
    
    **Using winget (Windows 11/10 with App Installer)**
    ```powershell
    winget install --id Git.Git -e
    ```
    
    **Using Chocolatey**
    ```powershell
    choco install git
    ```
    
    **Direct Download**
    - Visit [git-scm.com](https://git-scm.com/download/win)
    - Download the installer
    - Run with default settings

=== "macOS"
    
    **Using Homebrew (recommended)**
    ```bash
    brew install git
    ```
    
    **Using Xcode Command Line Tools**
    ```bash
    xcode-select --install
    ```

=== "Linux"
    
    **Ubuntu/Debian**
    ```bash
    sudo apt-get update
    sudo apt-get install git
    ```
    
    **Fedora/RHEL**
    ```bash
    sudo dnf install git
    ```
    
    **Arch**
    ```bash
    sudo pacman -S git
    ```

### Step 2: Install Python

=== "Windows"
    
    **Using winget**
    ```powershell
    winget install --id Python.Python.3.12 -e
    ```
    
    **Direct Download**
    1. Visit [python.org](https://python.org/downloads/)
    2. Download Python 3.12 installer
    3. **Important**: Check "Add Python to PATH"
    4. Click "Install Now"

=== "macOS"
    
    **Using Homebrew**
    ```bash
    brew install python@3.12
    ```
    
    **Using pyenv**
    ```bash
    brew install pyenv
    pyenv install 3.12
    pyenv global 3.12
    ```

=== "Linux"
    
    **Ubuntu/Debian**
    ```bash
    sudo apt-get update
    sudo apt-get install python3.12 python3.12-venv python3.12-dev
    ```
    
    **Fedora/RHEL**
    ```bash
    sudo dnf install python3.12 python3.12-devel
    ```
    
    **Arch**
    ```bash
    sudo pacman -S python
    ```

### Step 3: Install UV Package Manager

UV is a fast, modern Python package manager that replaces pip and pip-tools.

=== "Windows"
    
    ```powershell
    # PowerShell (as Administrator)
    irm https://astral.sh/uv/install.ps1 | iex
    ```
    
    After installation, restart your terminal.

=== "macOS/Linux"
    
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
    
    Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):
    ```bash
    export PATH="$HOME/.cargo/bin:$PATH"
    ```

### Step 4: Configure Git

Set up your identity for commits:

```bash
# Your name (as you want it to appear in commits)
git config --global user.name "Your Name"

# Your email (use the same email as your GitHub account)
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Enable colored output
git config --global color.ui auto

# Set line ending handling
# Windows
git config --global core.autocrlf true
# macOS/Linux
git config --global core.autocrlf input
```

### Step 5: Set Up the Project

1. **Clone the repository**
   ```bash
   git clone https://github.com/pahansen95/py-project-tmpl.git
   cd py-project-tmpl
   ```

2. **Create virtual environment**
   ```bash
   uv venv
   ```

3. **Activate the environment**
   === "Windows"
       ```powershell
       .venv\Scripts\activate
       ```
   
   === "macOS/Linux"
       ```bash
       source .venv/bin/activate
       ```

4. **Install dependencies**
   ```bash
   uv pip install -e ".[dev,docs]"
   ```

## Verification ✅

Run these commands to verify your setup is complete:

### Check Tool Versions

```bash
# Git (should be 2.30 or higher)
git --version

# Python (should be 3.10 or higher)
python --version

# UV (should be 0.4 or higher)  
uv --version
```

### Check Git Configuration

```bash
# Should show your name
git config --global user.name

# Should show your email
git config --global user.email
```

### Check Python Environment

```bash
# Should show (.venv) in your prompt
which python
# Expected: /path/to/project/.venv/bin/python (or Scripts on Windows)

# List installed packages
uv pip list
```

### Quick Test

Create and run a simple test:

```bash
# Create test file
echo "print('Hello from Python!')" > test.py

# Run it
python test.py
# Expected output: Hello from Python!

# Clean up
rm test.py
```

## Development Tools (Optional)

These tools enhance your development experience:

=== "VS Code"
    
    1. Download from [code.visualstudio.com](https://code.visualstudio.com/)
    2. Install recommended extensions:
       - Python (ms-python.python)
       - GitLens (eamodio.gitlens)
       - Material Icon Theme
    
    3. Open the project:
       ```bash
       code .
       ```

=== "GitHub Desktop"
    
    1. Download from [desktop.github.com](https://desktop.github.com/)
    2. Sign in with your GitHub account
    3. Clone repositories visually
    4. Manage branches and commits with GUI

=== "PyCharm"
    
    1. Download from [jetbrains.com/pycharm](https://www.jetbrains.com/pycharm/)
    2. Open project folder
    3. Configure interpreter to use `.venv`

## Troubleshooting 🔧

### Common Issues and Solutions

??? error "Command not found"
    
    **Symptom**: `command not found: git` (or python, uv)
    
    **Solutions**:
    
    1. **Restart your terminal** - New installations need a fresh session
    
    2. **Check PATH** - Ensure tools are in your system PATH
       ```bash
       # Windows PowerShell
       $env:Path -split ';' | Select-String git
       
       # macOS/Linux
       echo $PATH | tr ':' '\n' | grep -E 'git|python|cargo'
       ```
    
    3. **Reinstall** - Use the automated setup script

??? error "Permission denied"
    
    **Symptom**: `Permission denied` when installing
    
    **Solutions**:
    
    - **Windows**: Run PowerShell as Administrator
    - **macOS/Linux**: Use `sudo` for system packages
    - **Check file permissions**: `ls -la` to see ownership

??? error "SSL Certificate Error"
    
    **Symptom**: SSL verification failed when downloading
    
    **Solutions**:
    
    1. **Update certificates**:
       ```bash
       # macOS
       brew install ca-certificates
       
       # Linux
       sudo apt-get install ca-certificates
       ```
    
    2. **Corporate proxy**: Configure proxy settings
       ```bash
       export HTTP_PROXY=http://proxy.company.com:8080
       export HTTPS_PROXY=http://proxy.company.com:8080
       ```

??? error "Python version too old"
    
    **Symptom**: Python version is below 3.10
    
    **Solutions**:
    
    1. **Check available Python commands**:
       ```bash
       python3.12 --version
       python3.11 --version
       python3.10 --version
       ```
    
    2. **Use pyenv** to manage versions:
       ```bash
       pyenv install 3.12
       pyenv local 3.12
       ```

??? error "Virtual environment activation fails"
    
    **Symptom**: `.venv\Scripts\activate` not found or doesn't work
    
    **Solutions**:
    
    1. **Windows execution policy**:
       ```powershell
       Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
       ```
    
    2. **Recreate virtual environment**:
       ```bash
       rm -rf .venv
       uv venv
       ```

### Getting Help

If you're still stuck:

1. **Check the logs**
   - Windows: `$env:TEMP\py-project-setup.log`
   - macOS/Linux: `/tmp/py-project-setup.log`

2. **Search existing issues**
   - [GitHub Issues](https://github.com/pahansen95/py-project-tmpl/issues)

3. **Ask for help**
   - Include your OS version
   - Copy error messages
   - Describe what you tried

## Success! 🎉

Once all verification checks pass, you're ready to start developing!

### Next Steps

1. **Learn the workflow**: Continue to [Development Workflow](workflow.md)
2. **Try the practice exercises**: Jump to [Practice](practice.md)
3. **Start coding**: Create your first feature branch

### Quick Commands

Save these for quick reference:

```bash
# Activate environment (run every time you start)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install new packages
uv pip install package-name

# Run tests
pytest

# Start docs server
mkdocs serve
```

---

*Tip: Bookmark this page for future reference when setting up new machines or helping teammates get started.*