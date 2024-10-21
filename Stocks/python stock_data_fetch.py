import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

# PostgreSQL connection setup
db_engine = create_engine('postgresql+psycopg2://postgres:83326874@localhost:5432/Stocks')

# Step 1: Scrape All S&P 500 Stock Symbols from Wikipedia
def get_sp500_symbols():
    # URL of the S&P 500 companies list on Wikipedia
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    
    # Read the table from the webpage
    table = pd.read_html(url)[0]
    
    # Get all stock symbols
    sp500_symbols = table['Symbol'].tolist()
    
    return sp500_symbols

# Step 2: Fetch Historical Stock Data
def fetch_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    stock_data.reset_index(inplace=True)
    stock_data['Symbol'] = symbol
    return stock_data

# Step 3: Store Data in PostgreSQL
def store_stock_data(df):
    # Store the dataframe into PostgreSQL database
    df.to_sql('stock_data', db_engine, if_exists='append', index=False)

# Step 4: Fetch and Store Data for All S&P 500 Stocks
def fetch_and_store_sp500_stocks(start_date='2020-01-01', end_date='2023-01-01'):
    # Get the list of S&P 500 stock symbols
    symbols = get_sp500_symbols()
    
    # Fetch and store data for each symbol
    for symbol in symbols:
        try:
            print(f"Fetching data for {symbol}...")
            stock_data = fetch_stock_data(symbol, start_date, end_date)
            
            # Store the data in PostgreSQL
            store_stock_data(stock_data)
            print(f"Data for {symbol} stored successfully.")
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

# Run the script to fetch and store S&P 500 stocks data
fetch_and_store_sp500_stocks()