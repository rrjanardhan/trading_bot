import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    @staticmethod
    def get_historical_data(symbol, start_date, end_date=None, interval="1d"):
        """Fetch historical data from Yahoo Finance"""
        try:
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for {symbol}")
            
            print(f"Data fetched for {symbol}: {len(df)} rows")
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    @staticmethod
    def get_live_price(symbol):
        """Get current price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            return round(price, 2)
        except Exception as e:
            print(f"Error fetching live price: {e}")
            return None
    
    @staticmethod
    def get_multiple_symbols(symbols, start_date, end_date=None):
        """Fetch data for multiple symbols"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        data_dict = {}
        for symbol in symbols:
            print(f"Fetching {symbol}...")
            df = DataFetcher.get_historical_data(symbol, start_date, end_date)
            if df is not None:
                data_dict[symbol] = df
        return data_dict
    
    @staticmethod
    def get_company_info(symbol):
        """Get company information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'Symbol': symbol,
                'Name': info.get('longName', 'N/A'),
                'Sector': info.get('sector', 'N/A'),
                'Market Cap': info.get('marketCap', 'N/A')
            }
        except:
            return None
    
    @staticmethod
    def save_to_csv(data, filename):
        """Save data to CSV"""
        try:
            data.to_csv(filename)
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False