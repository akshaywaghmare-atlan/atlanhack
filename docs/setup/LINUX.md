---
title: Linux Setup Guide for Atlan PostgreSQL App
description: Step-by-step instructions for setting up the Atlan PostgreSQL App on Linux
tags:
  - setup
  - linux
  - installation
---

# Linux Setup Guide

This guide will help you set up the Atlan PostgreSQL App on Linux (Ubuntu/Debian based systems).

## Prerequisites

Before starting, ensure you have:
- Terminal access
- Sudo privileges (for installing software)
- Internet connection

## Setup Steps

### 1. Install System Dependencies

First, install essential build dependencies:

```bash
sudo apt-get update
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
liblzma-dev
```

### 2. Install Python 3.11 with pyenv

We'll use pyenv to manage Python versions:

```bash
# Install pyenv
curl https://pyenv.run | bash

# Add pyenv to your path
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

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

Temporal is used for workflow orchestration:

```bash
curl -sSf https://temporal.download/cli.sh | sh
export PATH="$HOME/.temporalio/bin:$PATH"
echo 'export PATH="$HOME/.temporalio/bin:$PATH"' >> ~/.bashrc
```

### 5. Install DAPR CLI

Install DAPR using the following commands:

```bash
# Install DAPR CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash -s 1.14.1

# Initialize DAPR (slim mode)
dapr init --runtime-version 1.13.6 --slim

# Verify installation
dapr --version
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
- If pyenv fails to install Python, make sure you have all the required dependencies:
  ```bash
  sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
  xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
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
  sudo netstat -tunlp | grep 8000  # Check if port 8000 is in use
  sudo netstat -tunlp | grep 8050  # Check if port 8050 is in use
  ```

## Need Help?

If you encounter any issues during setup, please reach out to us on the Slack channel #pod-app-framework or email apps@atlan.com.

## Next Steps

For more information on developing with the Atlan PostgreSQL App, check out the [Development Guide](../DEVELOPMENT.md).