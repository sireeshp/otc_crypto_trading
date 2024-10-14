
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
   │
   ├── src/
   │   ├── services/
   │   ├── db/
   │   ├── execution/
   │   ├── middlewares/
   │   ├── models/
   │   ├── routes/
   │   ├── strategies/
   │   ├── utils/
   │   ├── __init__.py
   │   └── main.py
   ├── static/                  # Static files like CSS, JS, favicon, etc.
   ├── tests/                   # Test files
   ├── .flake8                  # flake8 configuration
   ├── .gitignore               # Files to ignore in Git
   ├── .isort.cfg               # isort configuration
   ├── .pre-commit-config.yaml  # Pre-commit hooks configuration
   ├── Makefile                 # Command automation
   ├── pytest.ini               # Pytest configuration
   ├── pyproject.toml           # Configuration for black, isort, etc.
   ├── README.md                # Project documentation
   └── requirements.txt
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

To expose full-feature crypto trading features through WebSocket, here is a list of **unique required WebSocket endpoints** that are essential for a comprehensive trading platform:

### Core Features for Market Data (Public)
1. **`watch_ticker`**: Real-time price updates for a specific symbol. -Done
2. **`watch_tickers`**: Real-time price updates for all available symbols (or a subset).
3. **`watch_order_book`**: Real-time updates to the order book for a specific symbol.
4. **`watch_bids_asks`**: Real-time updates to top-level bids and asks (spread).
5. **`watch_trades`**: Real-time updates for public trades executed on a specific symbol.
6. **`watch_ohlcv`**: Real-time OHLCV (candlestick data) for specific timeframes.
7. **`watch_liquidations`**: Real-time liquidation data for all symbols.
8. **`watch_funding_rate`**: Real-time funding rate updates for a specific symbol (for perpetual futures).
9. **`watch_funding_rates`**: Real-time funding rate updates for all perpetual futures symbols.

### Extended Features for Market Data (Public)
1. **`watch_ohlcv_for_symbols`**: Real-time OHLCV data for multiple specific symbols.
2. **`watch_trades_for_symbols`**: Real-time trade updates for multiple specific symbols.
3. **`watch_order_book_for_symbols`**: Real-time order book updates for multiple specific symbols.
4. **`watch_funding_rates_for_symbols`**: Real-time funding rate updates for multiple specific symbols.
5. **`watch_liquidations_for_symbols`**: Real-time liquidation data for multiple specific symbols.

### Core Features for Account & Orders (Private)
1. **`watch_orders`**: Real-time updates on all open and filled orders for the account.
2. **`watch_my_trades`**: Real-time updates on all trades executed by the account.
3. **`watch_balance`**: Real-time updates on account balances, including deposits, withdrawals, and positions.
4. **`watch_position`**: Real-time updates on the account’s position for a specific symbol (for futures or margin).
5. **`watch_positions`**: Real-time updates on all open positions for the account.
6. **`watch_funding_rate_for_my_position`**: Updates to the funding rate applied to the user’s specific position.

### Extended Features for Account & Orders (Private)
1. **`watch_orders_for_symbols`**: Real-time updates for the user’s orders across multiple symbols.
2. **`watch_my_trades_for_symbols`**: Real-time updates for the user’s trades across multiple symbols.
3. **`watch_position_for_symbols`**: Real-time updates for the user’s positions across multiple symbols.
4. **`watch_my_liquidations`**: Real-time updates for user account liquidations.
5. **`watch_my_liquidations_for_symbols`**: Real-time updates for user account liquidations across multiple symbols.

### Unique WebSocket Endpoints for Different Types of Data:
- **Account/Wallet**:
  - **`watch_balance`**: Ensures you receive up-to-date account balance information.
- **Positions**:
  - **`watch_positions`**: Updates on all positions (useful for futures/margin trading).
- **Funding**:
  - **`watch_funding_rate`** and **`watch_funding_rates`**: These are essential for perpetual futures trading to monitor funding rates that affect positions.

### Summary of Unique Endpoints
To cover **all essential trading and market data** features, you need to expose the following endpoints:

1. **Market Data (Public)**:
   - `watch_ticker`
   - `watch_tickers`
   - `watch_order_book`
   - `watch_bids_asks`
   - `watch_trades`
   - `watch_ohlcv`
   - `watch_liquidations`
   - `watch_funding_rate`
   - `watch_funding_rates`

2. **Extended Market Data (Public)**:
   - `watch_trades_for_symbols`
   - `watch_order_book_for_symbols`
   - `watch_ohlcv_for_symbols`
   - `watch_funding_rates_for_symbols`
   - `watch_liquidations_for_symbols`

3. **Account & Orders (Private)**:
   - `watch_orders`
   - `watch_my_trades`
   - `watch_balance`
   - `watch_position`
   - `watch_positions`
   - `watch_funding_rate_for_my_position`
   - `watch_my_liquidations`

4. **Extended Account & Orders (Private)**:
   - `watch_orders_for_symbols`
   - `watch_my_trades_for_symbols`
   - `watch_position_for_symbols`
   - `watch_my_liquidations_for_symbols`

This covers both the public and private WebSocket APIs necessary for real-time trading and market data updates.
