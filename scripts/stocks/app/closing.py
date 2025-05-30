####################################################################################################################
# File reads the tickers.csv file and for each ticker in the file gets the latest closing price from yfinance
# The closing price is then inserted in daily_stock_data table (while checking if for the date was already inserted in which case it overwrites the value)
# Scripts also logs in var and in an errors.log files the errors (tickers of values not found in the api) and the overwriting cases
#
# Still //TODO
#  - make a connection between daily_stock_data and the stocks table in order to only return the stock ID (checking if this is a faster and efficient method)
# -  decide which errors should be send by email to the admin after the script runs
#####################################################################################################################

import csv
import yfinance as yf
import datetime
import logging
import mysql.connector

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize an empty list to store error messages
error_log = []

# MySQL database connection details
HOST = "localhost"
USER = "danielne_app"
PASSWORD = "Piedone1976!!"
DATABASE = "danielne_stocks"

# Set up logging to a file
file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.ERROR)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger = logging.getLogger()
logger.addHandler(file_handler)


def read_stock_symbols(file_name):
    """Read stock symbols from a CSV file"""
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        return [row[0].replace('.', '-') for row in reader]


def get_latest_closing_price(symbol):
    """Get the latest closing price for a stock symbol"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        if data.empty:
            raise ValueError(f"No data found for {symbol}")
        return data['Close'].iloc[-1]
    except Exception as e:
        # Log the error message to the error_log list
        error_log.append(f"Error for {symbol}: {e}")
        logger.error(f"Error for {symbol}: {e}")
        return None


def get_stock_id(symbol):
    """Get the stock ID based on the symbol"""
    # Return the stock ticker as the stock ID
    return symbol


def process_stock_symbol(symbol):
    """Process a stock symbol"""
    latest_closing_price = get_latest_closing_price(symbol)
    if latest_closing_price is not None:
        data_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )

        # Create a cursor object
        cursor = connection.cursor()

        # Check if the symbol already has a value for the date
        select_query = """
        SELECT * FROM daily_stock_data
        WHERE stock_id = %s AND date = %s
        """
        cursor.execute(select_query, (symbol, data_date))

        # If a row is found, update the existing value
        if cursor.fetchone():
            update_query = """
            UPDATE daily_stock_data
            SET closing_price = %s
            WHERE stock_id = %s AND date = %s
            """
            cursor.execute(
                update_query, (latest_closing_price, symbol, data_date))
            logger.error(f"Overwrote existing value for {
                         symbol} on {data_date}")
        # If no row is found, insert a new value
        else:
            insert_query = """
            INSERT INTO daily_stock_data (stock_id, date, closing_price)
            VALUES (%s, %s, %s)
            """
            cursor.execute(
                insert_query, (symbol, data_date, latest_closing_price))

        # Commit the changes
        connection.commit()

        # Close the connection
        connection.close()
    else:
        logger.error(f"Failed to get data for {symbol}")


def main():
    stock_symbols = read_stock_symbols('tickers.csv')
    total_symbols = len(stock_symbols)

    for index, symbol in enumerate(stock_symbols):
        process_stock_symbol(symbol)
        progress = ((index + 1) / total_symbols) * 100
        print(f"Progress: {progress:.2f}%")

    print("All done!")


if __name__ == "__main__":
    main()
