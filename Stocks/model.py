import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import statsmodels.api as sm
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
import plotly.graph_objs as go
import warnings
import os

# Create directories for saving results
os.makedirs('analysis', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)
os.makedirs('forecasts', exist_ok=True)

# Establish database connection
engine = create_engine('postgresql+psycopg2://postgres:83326874@localhost:5432/Stocks')

# Fetch all distinct stock symbols from the stock_data table
def get_stock_symbols():
    query = "SELECT DISTINCT stock_symbol FROM stock_data;"
    try:
        symbols_df = pd.read_sql(query, engine)
        stock_symbols = symbols_df['stock_symbol'].tolist()  # Convert DataFrame column to list
        return stock_symbols
    except Exception as e:
        print(f"Error fetching stock symbols: {e}")
        return []

# Define a function to fetch stock data for a given symbol
def fetch_stock_data(symbol):
    query = f"""
    SELECT "Date", "Close" 
    FROM stock_data 
    WHERE stock_symbol = '{symbol}' 
    ORDER BY "Date" ASC;
    """
    try:
        df = pd.read_sql(query, engine)
        if df.empty:
            print(f"No data found for symbol: {symbol}")
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

# ARIMA model
def arima_model(stock_data, symbol):
    try:
        model = ARIMA(stock_data['Close'], order=(5, 1, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=30)
        forecast_df = pd.DataFrame({'Date': pd.date_range(start=stock_data['Date'].iloc[-1] + pd.Timedelta(days=1), periods=30), 
                                    'ARIMA_Forecast': forecast})
        forecast_df.to_csv(f'forecasts/arima_forecast_{symbol}.csv', index=False)
        return forecast_df
    except Exception as e:
        print(f"Error in ARIMA model for {symbol}: {e}")
        return pd.DataFrame()

# SARIMA model
def sarima_model(stock_data, symbol):
    try:
        model = sm.tsa.SARIMAX(stock_data['Close'], 
                               order=(1, 1, 1), 
                               seasonal_order=(1, 1, 1, 12), 
                               enforce_stationarity=False, 
                               enforce_invertibility=False)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model_fit = model.fit(maxiter=5000, disp=False)
        forecast = model_fit.forecast(steps=30)
        forecast_df = pd.DataFrame({'Date': pd.date_range(start=stock_data['Date'].iloc[-1] + pd.Timedelta(days=1), periods=30), 
                                    'SARIMA_Forecast': forecast})
        forecast_df.to_csv(f'forecasts/sarima_forecast_{symbol}.csv', index=False)
        return forecast_df
    except Exception as e:
        print(f"Error in SARIMA model for {symbol}: {e}")
        return pd.DataFrame()

# Prophet model
def prophet_model(stock_data, symbol):
    try:
        df = stock_data.rename(columns={'Date': 'ds', 'Close': 'y'})
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        forecast_df = forecast[['ds', 'yhat']].tail(30).rename(columns={'ds': 'Date', 'yhat': 'Prophet_Forecast'})
        forecast_df.to_csv(f'forecasts/prophet_forecast_{symbol}.csv', index=False)
        return forecast_df
    except Exception as e:
        print(f"Error in Prophet model for {symbol}: {e}")
        return pd.DataFrame()

# Visualization function
def visualize_results(stock_data, arima_forecast, sarima_forecast, prophet_forecast, symbol):
    fig = go.Figure()
    
    # Actual data
    fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Close'], mode='lines', name='Actual'))
    
    # Forecasts
    fig.add_trace(go.Scatter(x=arima_forecast['Date'], y=arima_forecast['ARIMA_Forecast'], mode='lines', name='ARIMA Forecast'))
    fig.add_trace(go.Scatter(x=sarima_forecast['Date'], y=sarima_forecast['SARIMA_Forecast'], mode='lines', name='SARIMA Forecast'))
    fig.add_trace(go.Scatter(x=prophet_forecast['Date'], y=prophet_forecast['Prophet_Forecast'], mode='lines', name='Prophet Forecast'))

    fig.update_layout(title=f'Stock Price Forecasting for {symbol}', xaxis_title='Date', yaxis_title='Price')
    fig.write_html(f'visualizations/visualization_{symbol}.html')
    print(f"Visualization saved for {symbol} to 'visualizations/visualization_{symbol}.html'")

# Main function to fetch data, apply models, and save output for each symbol
def main():
    stock_symbols = get_stock_symbols()

    if stock_symbols:
        for symbol in stock_symbols:
            print(f"Processing symbol: {symbol}")
            stock_data = fetch_stock_data(symbol)

            if stock_data is not None and not stock_data.empty:
                # Run ARIMA model
                arima_forecast = arima_model(stock_data, symbol)

                # Run SARIMA model
                sarima_forecast = sarima_model(stock_data, symbol)

                # Run Prophet model
                prophet_forecast = prophet_model(stock_data, symbol)

                # Save visualizations
                visualize_results(stock_data, arima_forecast, sarima_forecast, prophet_forecast, symbol)

                print(f"Completed processing for {symbol}.")
            else:
                print(f"No data found for symbol: {symbol}")

if __name__ == "__main__":
    main()