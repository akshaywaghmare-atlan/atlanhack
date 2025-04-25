---
title: macOS Setup Guide for Atlan PostgreSQL App
description: Step-by-step instructions for setting up the Atlan PostgreSQL App on macOS
tags:
  - setup
  - macos
  - installation
---

# macOS Setup Guide

This guide will help you set up the Atlan PostgreSQL App on macOS.

## Prerequisites

Before starting, ensure you have:
- Terminal access
- Admin privileges (for installing software)
- Internet connection

## Setup Steps

### 1. Install Homebrew

Homebrew is a package manager for macOS that simplifies software installation:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow any post-installation instructions shown in the terminal.

### 2. Install Python 3.11

We'll use pyenv to manage Python versions:

```bash
# Install pyenv
brew install pyenv

# Set up shell environment
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Install and set Python 3.11.10
pyenv install 3.11.10
pyenv global 3.11.10

# Verify installation
python --version  # Should show Python 3.11.10
```

### 3. Install Poetry 1.8.5

Poetry manages Python dependencies and project environments:

```bash
pip install poetry==1.8.5
```

### 4. Install Temporal CLI

Temporal is the workflow orchestration platform:

```bash
brew install temporal
```

### 5. Install DAPR CLI

DAPR (Distributed Application Runtime) simplifies microservice development:

```bash
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash -s 1.14.1
dapr init --runtime-version 1.13.6 --slim
```

### 6. Configure Poetry for the Project

Set up Poetry to use project-specific virtualization and Git:

```bash
poetry config virtualenvs.in-project true
poetry config experimental.system-git-client true
```

### 7. Install Project Dependencies

Install all required dependencies:

```bash
make install

# Activate the virtual environment if not already activated
source .venv/bin/activate
```

### 8. Start Platform Services

Start the Temporal server and DAPR system:

```bash
make start-deps
```

Wait for all services to start successfully. You should see messages indicating that Temporal and DAPR are running.

### 9. Run the Application

Open a new terminal session, navigate to the project directory, activate the virtual environment, and launch the Atlan PostgreSQL App:

```bash
# Activate virtual environment in the new terminal
source .venv/bin/activate

# Run the application
make run
```

## Verify Installation

Your application should now be running. You can access:

- Web UI: http://localhost:8000/
- Workflows dashboard: http://localhost:8050/workflows

## Troubleshooting

### Python Installation Issues
- If pyenv installation fails, you may need additional dependencies:
  ```bash
  brew install openssl readline sqlite3 xz zlib
  ```

### Poetry Installation Issues
- If Poetry fails to install, try the alternative method:
  ```bash
  curl -sSL https://install.python-poetry.org | python -
  ```

### Dependency Installation Errors
- If `make install` fails, check your Git access:
  ```bash
  # Configure Git to use HTTPS instead of SSH
  git config --global url."https://github.com/".insteadOf "git@github.com:"
  ```

### Port Conflicts
- If you see errors about ports already in use, check for running processes:
  ```bash
  lsof -i :8000  # Check if port 8000 is in use
  lsof -i :8050  # Check if port 8050 is in use
  ```

## Need Help?

If you encounter any issues during setup, please reach out to us on the Slack channel #pod-app-framework or email apps@atlan.com.

## Next Steps

For more information on developing with the Atlan PostgreSQL App, check out the [Development Guide](../DEVELOPMENT.md).