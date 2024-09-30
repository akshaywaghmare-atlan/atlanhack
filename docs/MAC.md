# Mac Setup Guide

This guide will help you set up your Mac for developing this project, starting from scratch.


## Setting up the environment

### 1. Install Homebrew

Homebrew is a package manager for macOS. Open Terminal and run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python

Install Python 3.11 or higher using Homebrew:

```bash
brew install python@3.11
```

### 3. Install poetry

Poetry is used for dependency management:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 4. Install Temporal CLI

```bash
brew install temporal
```

### 5. Install DAPR CLI

```
brew install dapr/tap/dapr-cli
dapr init --slim
```

### 6. Install Node.js

Install Node.js using Homebrew:

```bash
brew install node
```

## Setting up the project

### 0. Repository Access

Make sure you have access to the following SDK repos.
- [Python Application SDK](https://github.com/atlanhq/application-sdk)
- [UI SDK](https://github.com/atlanhq/application-sdk)

If you don't have access, please reach out to the IT team.

### 1. Clone the repository

Make sure to clone this repository including the submodule, use the following command:
```bash
git clone --recurse-submodules https://github.com/atlanhq/phoenix-postgres-app.git
```

### 2. Install python project dependencies

Set poetry config
```
poetry config virtualenvs.in-project true
make install
```

### 3. Install frontend dependencies and build

```bash
npm install
npm run generate
```

### 4. Start the platform

Open a new terminal window and start the platform by running:
```bash
make start-all
```

This will start the Temporal server and the DAPR system.

### 5. Run the application

Open a new terminal window and start the application by running:
```bash
make run
```
