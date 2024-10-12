
### **Step 1: Set Up Your Project Directory**

1. **Create the Project Folder**:
   Open a terminal or use VS Code’s integrated terminal and create a directory for your project.
   ```bash
   mkdir otc_crypto_trading
   cd otc_crypto_trading
   ```

2. **Open the Folder in VS Code**:
   You can now open this folder in VS Code:
   ```bash
   code .
   ```

### **Step 2: Set Up Python Virtual Environment**

A virtual environment is essential to isolate dependencies for this specific project.

1. **Create a Virtual Environment**:
   Inside the project folder, create a virtual environment. This will create a `.venv` folder in your project directory.
   ```bash
   python3 -m venv .venv
   ```

2. **Activate the Virtual Environment**:
   For MacOS/Linux:
   ```bash
   source .venv/bin/activate
   ```
   For Windows:
   ```bash
   .venv\Scripts\activate
   ```

3. **Configure VS Code to Use Virtual Environment**:
   - In VS Code, press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac).
   - Type and select "Python: Select Interpreter".
   - Choose the interpreter inside the `.venv` folder you just created.

### **Step 3: Install Essential Libraries**

Let’s install the necessary Python libraries. Inside your virtual environment, run:

```bash
pip install ccxt pandas numpy matplotlib talib backtrader scikit-learn tensorflow empyrical python-dotenv
```

You can also create a `requirements.txt` to track the libraries:
```bash
pip freeze > requirements.txt
```

This file can later be used to install dependencies using:
```bash
pip install -r requirements.txt
```

### **Step 4: Set Up Linting and Code Formatting**

To maintain code quality, let’s install linters and formatters like `flake8` and `black`.

1. **Install Linting and Formatting Tools**:
   Install `flake8` for linting, and `black` for formatting code.
   ```bash
   pip install flake8 black isort
   ```

2. **Configure VS Code for Linting and Formatting**:
   - Press `Ctrl+Shift+P`, type "Preferences: Open Settings (JSON)".
   - Add the following settings to your VS Code `settings.json`:
     ```json
     {
         "python.linting.enabled": true,
         "python.linting.flake8Enabled": true,
         "python.formatting.provider": "black",
         "editor.formatOnSave": true,
         "python.linting.flake8Args": ["--max-line-length=88"],
         "python.sortImports.args": ["--profile", "black"]
     }
     ```

3. **Run Linting and Formatting**:
   - To run `flake8`:
     ```bash
     flake8 .
     ```
   - To run `black` (auto-format):
     ```bash
     black .
     ```

4. **Set Up Pre-Commit Hooks** (optional but recommended):
   Pre-commit hooks ensure linting and formatting are applied before committing code.

   - Install `pre-commit`:
     ```bash
     pip install pre-commit
     ```

   - Create a `.pre-commit-config.yaml` in your root folder:
     ```yaml
     repos:
     -   repo: https://github.com/psf/black
         rev: stable
         hooks:
         - id: black
     -   repo: https://github.com/PyCQA/flake8
         rev: 3.9.2
         hooks:
         - id: flake8
     ```

   - Install pre-commit hooks:
     ```bash
     pre-commit install
     ```

   This will automatically check formatting and linting before you commit.

### **Step 5: Create Project Structure**

Let’s create a basic project structure with separate modules for clarity and maintainability.

1. **Basic Structure**:
   - Create a directory structure for the modules:
     ```bash
     mkdir -p src/{data,strategies,execution,models,utils}
     touch src/{data/__init__.py,strategies/__init__.py,execution/__init__.py,models/__init__.py,utils/__init__.py}
     ```

   Your folder structure should look like this:
   ```
   otc_crypto_trading/
   ├── .venv/
   ├── requirements.txt
   ├── .pre-commit-config.yaml
   ├── src/
   │   ├── data/
   │   │   └── __init__.py
   │   ├── strategies/
   │   │   └── __init__.py
   │   ├── execution/
   │   │   └── __init__.py
   │   ├── models/
   │   │   └── __init__.py
   │   └── utils/
   │       └── __init__.py
   └── main.py
   ```

2. **Module Responsibilities**:
   - `data`: Data fetching and processing logic, real-time and historical data.
   - `strategies`: Your trading algorithms and strategies.
   - `execution`: Code to handle live trading, execution via APIs.
   - `models`: Machine learning models for predictions and AI-based strategies.
   - `utils`: Helper functions and utility scripts.

### **Step 6: Configure Logging**

Logging is essential for monitoring the system’s behavior in real-time. Set up logging in `utils`.

1. **Create Logging Utility**:
   In `src/utils/logger.py`, add the following:
   ```python
   import logging

   def setup_logger(name, log_file, level=logging.INFO):
       """Function to setup a logger."""
       handler = logging.FileHandler(log_file)
       formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
       handler.setFormatter(formatter)

       logger = logging.getLogger(name)
       logger.setLevel(level)
       logger.addHandler(handler)

       return logger

   # Example usage
   logger = setup_logger('trading_logger', 'trading.log')
   logger.info('This is an info message')
   ```

2. **Integrate Logging in Your Code**:
   Use logging in various parts of your project to capture trading decisions, errors, and execution details.

### **Step 7: Version Control and Git Setup**

1. **Initialize Git Repository**:
   Initialize a Git repository and create a `.gitignore` file to ignore unnecessary files like the virtual environment and log files.
   ```bash
   git init
   echo ".venv/\n__pycache__/\n*.log\n" > .gitignore
   ```

2. **Commit Your Initial Setup**:
   Stage and commit your files:
   ```bash
   git add .
   git commit -m "Initial project setup"
   ```
