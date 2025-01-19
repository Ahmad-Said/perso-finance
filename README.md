# Perso-Finance Repo

## Overview

The Perso-Finance repository is a Python-based project designed to extract, process, and analyze bank statements from various financial institutions. The project supports multiple banks and provides tools for categorizing transactions and generating comprehensive financial reports.

## Features

- **Bank Statement Extraction**: Extracts data from PDF bank statements.
- **Transaction Processing**: Processes and categorizes transactions.
- **Report Generation**: Generates Excel reports summarizing all transactions.
- **Support for Multiple Banks**: Includes extractors for BNP, Hello Bank, Revolut, and Société Générale.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/Ahmad-Said/perso-finance.git
    cd perso-finance
    ```

2. **Create a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Configuration

To Override the default configuration,
Copy const/const_gl_local.py.example to const/const_gl_local.py 
   and fill in the required information inherited from const/const_gl.py

For running different module files in vs code, open folder workspace at root of the project,
then go to setting -> search env -> edit env file in json -> add followings:
```json
{
    "terminal.integrated.env.windows": {
    "PYTHONPATH": "${workspaceFolder}"
    },
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "${workspaceFolder}"
    },
    "terminal.integrated.env.osx": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}
```

### Extracting Bank Statements

To extract and process bank statements, run the `main` function in the `bank_calculator.py` file:

```sh
python bank/bank_calculator.py
```

### Frais Calculator
If code produce missing local on ubuntu you can run in terminal following commands:
```sh
sudo locale-gen fr_FR.UTF-8
sudo dpkg-reconfigure locales
```