---
title: Windows Setup Guide for Atlan PostgreSQL App
description: Step-by-step instructions for setting up the Atlan PostgreSQL App on Windows
tags:
  - setup
  - windows
  - installation
---

# Windows Setup Guide

This guide will help you set up the Atlan PostgreSQL App on Windows.

## Prerequisites

Before starting, ensure you have:

- PowerShell access (run as Administrator)
- Internet connection
- Windows 10 or higher

## Setup Steps

### 1. Install Python 3.11.10

Download and install Python from the official website:

1. Go to [Python Downloads](https://www.python.org/downloads/release/python-31110/)
2. Download the Windows installer (64-bit)
3. Run the installer with these options:
   - ✅ Add Python to PATH
   - ✅ Install for all users
   - ✅ Customize installation
   - ✅ All optional features
   - ✅ Install to a directory without spaces (e.g., `C:\Python311`)
4. Verify installation by opening PowerShell and running:
   ```powershell
   python --version  # Should show Python 3.11.10
   ```

### 2. Install Poetry 2.1.3

Install Poetry using PowerShell:

```powershell
# Install Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Add Poetry to your PATH
$env:Path += ";$env:APPDATA\Python\Scripts"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::User)

# Install specific version
poetry self update 2.1.3

# Verify installation
poetry --version  # Should show Poetry 2.1.3
```

### 3. Install Temporal CLI

Download and install Temporal:

```powershell
# Create a directory for Temporal CLI
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.temporalio\bin"

# Download Temporal CLI
Invoke-WebRequest -Uri https://temporal.download/cli/archive/latest?platform=windows&arch=amd64 -OutFile "$env:USERPROFILE\.temporalio\temporal.zip"

# Extract and install
Expand-Archive -Path "$env:USERPROFILE\.temporalio\temporal.zip" -DestinationPath "$env:USERPROFILE\.temporalio\bin" -Force

# Add to PATH
$env:Path += ";$env:USERPROFILE\.temporalio\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::User)

# Verify installation
temporal --version
```

### 4. Install DAPR CLI

Install DAPR using PowerShell:

```powershell
# Install DAPR CLI
powershell -Command "$script=iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1; $block=[ScriptBlock]::Create($script); invoke-command -ScriptBlock $block -ArgumentList 1.14.1"

# Initialize DAPR (slim mode)
dapr init --runtime-version 1.13.6 --slim

# Verify installation
dapr --version
```

### 5. Configure Git for Windows

Ensure Git is configured properly:

```powershell
# Install Git if not already installed
# Download from https://git-scm.com/download/win if needed

# Configure Git to use HTTPS instead of SSH
git config --global url."https://github.com/".insteadOf "git@github.com:"
```

### 6. Configure Poetry for the Project

Set up Poetry configuration:

```powershell
poetry config virtualenvs.in-project true
poetry config system-git-client true
```

### 7. Install Project Dependencies

Install dependencies (requires Make for Windows):

```powershell
# Install Chocolatey if Make is not installed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Make
choco install make

# Install project dependencies
make install

# Activate the virtual environment if not already activated
.\.venv\Scripts\activate
```

### 8. Start Platform Services

Start the Temporal server and DAPR system:

```powershell
make start-deps
```

Wait for all services to start successfully. You should see messages indicating that Temporal and DAPR are running.

### 9. Run the Application

Open a new PowerShell session, navigate to the project directory, activate the virtual environment, and launch the Atlan PostgreSQL App:

```powershell
# Activate virtual environment in the new terminal
.\.venv\Scripts\activate

# Run the application
make run
```

## Verify Installation

Your application should now be running. You can access:

- Web UI: http://localhost:8000/
- Workflows dashboard: http://localhost:8050/workflows

## Troubleshooting

### Python Installation Issues

- Ensure PATH is correctly set:
  ```powershell
  $env:Path += ";C:\Python311;C:\Python311\Scripts"
  [Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::User)
  ```

### Poetry Installation Issues

- If Poetry command is not found, manually add it to your PATH:
  ```powershell
  $env:Path += ";$env:APPDATA\Python\Scripts"
  [Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::User)
  ```

### Dependency Installation Errors

- If Git access fails, check that you've configured it to use HTTPS:
  ```powershell
  git config --global url."https://github.com/".insteadOf "git@github.com:"
  ```

### Permissions Issues

- If you encounter permission errors, run PowerShell as Administrator

### Make Command Not Found

- If make is not found, confirm Chocolatey install:
  ```powershell
  choco install make -y
  ```
- Alternative: manually run each step in the Makefile

## Need Help?

If you encounter any issues during setup, please reach out to us on the Slack channel #pod-app-framework or email apps@atlan.com.

## Next Steps

For more information on developing with the Atlan PostgreSQL App, check out the [Development Guide](../DEVELOPMENT.md).
