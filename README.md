# Cryptocurrency Backtest Dashboard

This project is a Streamlit-based dashboard that displays cryptocurrency backtest results using data stored in a PostgreSQL database. The dashboard shows a leaderboard of various algorithms and their performance metrics and provides detailed monthly returns in chart form.

## Features

- **Leaderboard**: Displays algorithm name, backtest period, return, maximum drawdown (MDD), win rate, and monthly chart links.
- **Monthly Return Chart**: Allows users to view detailed monthly returns for selected backtest IDs.
- **PostgreSQL Integration**: Stores backtest results and monthly performance data in PostgreSQL for efficient querying and analysis.

## Requirements

- Python 3.8+
- PostgreSQL

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/crypto-backtest-dashboard.git
   cd crypto-backtest-dashboard
   ```

2. **Install dependencies**: Install required packages from requirements.txt:

```
bash
pip install -r requirements.txt
```

3. **Set up the database**:
- Create a PostgreSQL database.
- Set up a .env file with your database credentials:
```
makefile
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_db_name
```

4. **Create Tables**: Run the SQL commands below in your PostgreSQL instance to create the required tables:
```sql
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    algorithm_name TEXT NOT NULL,
    backtest_start DATE NOT NULL,
    backtest_end DATE NOT NULL,
    final_return NUMERIC,
    mdd NUMERIC,
    win_rate NUMERIC,
    monthly_chart_url TEXT
);

CREATE TABLE monthly_returns (
    id SERIAL PRIMARY KEY,
    backtest_id INT REFERENCES backtest_results(id) ON DELETE CASCADE,
    year INT,
    month INT,
    monthly_return NUMERIC
);
```
## Usage
1. **Load Backtest Data**: Save backtest data to the PostgreSQL database using the save_backtest_results function in main.py. This function saves the main metrics and calculates monthly returns.

2. **Run the Dashboard**: Start the Streamlit dashboard by running:
```
bash
streamlit run app.py
```

3. **Interact with the Dashboard**:
- **Leaderboard**: View algorithm performance metrics.
- **Monthly Return Chart**: Select an ID to view its detailed monthly returns.

## Example Code
In `main.py`, load your backtest data from an Excel file, calculate metrics like return and MDD, and save it to PostgreSQL. The Streamlit UI in `app.py` then fetches and visualizes this data.
