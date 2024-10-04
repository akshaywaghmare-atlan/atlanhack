# Mac Setup Guide

This guide will help you set up your Mac for developing this project, starting from scratch.

## Setting up the environment

### 1. Install Homebrew

Homebrew is a package manager for macOS that simplifies the installation of software. Execute the following command in your Terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

This script downloads and installs Homebrew on your system.

[Learn more about Homebrew](https://brew.sh/)

### 2. Install Python

Install Python 3.11 or higher:

i. Install `pyenv`. `pyenv` is a tool for managing multiple Python versions.
```
brew install pyenv
```
ii. Add the following to your `~/.zshrc` (or `~/.bash_profile` for Bash):
```
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```
iii. Reload your shell configuration `~/.zshrc` (or `~/.bash_profile` for Bash)
```
source ~/.zshrc
```
iv. Install and use Python 3.11 (or any version):
```
pyenv install 3.11.0
pyenv global 3.11.0
```
v. Verify the active Python version:
```
python --version
```


This will install and set up Python 3.11, which is required for running the project.

[Python documentation](https://docs.python.org/3.11/)

### 3. Install poetry

Poetry is a tool for dependency management and packaging in Python. Install it with:

```bash
curl -sSL https://install.python-poetry.org | python -
```
This command downloads and runs the Poetry installer script.

[Poetry documentation](https://python-poetry.org/docs/)

### 4. Install Temporal CLI

We use Temporal as a orchestration platform. Install the Temporal CLI with:

```bash
brew install temporal
```

This allows you to interact with Temporal from the command line.

[Temporal documentation](https://docs.temporal.io/develop/python)


### 5. Install DAPR CLI

Dapr (Distributed Application Runtime) simplifies microservice development. Install it with:

```
brew install dapr/tap/dapr-cli
dapr init --slim
```
These commands install the Dapr CLI and initialize it in slim mode.

[Dapr documentation](https://docs.dapr.io/)


### 6. Install Node.js

Node.js is a JavaScript runtime, which is required for building the frontend. Install it using Homebrew:
```bash
brew install node
```

This installs Node.js, which is needed for frontend development.

[Node.js documentation](https://nodejs.org/en/docs/)

## Setting up the project

### 0. Repository Access

Ensure you have access to the following SDK repositories:
- [Python Application SDK](https://github.com/atlanhq/application-sdk): The SDK is used to develop applications on the Atlan platform.
- [UI SDK](https://github.com/atlanhq/application-sdk): The SDK is used to develop the frontend of the application.

If you don't have access, please reach out to the IT team.

### 1. Clone the repository

Make sure to clone this repository including the submodule, use the following command:
```bash
git clone --recurse-submodules https://github.com/atlanhq/phoenix-postgres-app.git
```

### 2. Install python project dependencies

Install the python dependencies using the command:
```bash
make install
```
This sets up a project-specific virtual environment and installs the required Python packages.

### 3. Install frontend dependencies and build

Install the frontend dependencies and build the frontend using the command:
```bash
npm install
npm run generate
```
These commands install node dependencies and generate necessary frontend static files.

### 4. Start the platform

Open a new terminal window and start the platform by running:
```bash
make start-all
```

This will start the Temporal server and the DAPR system.

### 5. Run the application

Finally, open a new terminal window and start the application by running:
```bash
make run
```

This command launches your application, making it ready for development and testing.

Open http://localhost:8000/ on your browser to access the application :rocket:

> [!TIP]
> Head over to the [development guide](./DEVELOPMENT.md) to learn more about local development.
