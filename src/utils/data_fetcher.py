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
            
            print(f"✅ Data fetched for {symbol}: {len(df)} rows")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
    
    @staticmethod
    def get_live_price(symbol):
        """Get current price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            return round(price, 2)
        except Exception as e:
            print(f"❌ Error fetching live price: {e}")
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
                'Industry': info.get('industry', 'N/A'),
                'Market Cap': info.get('marketCap', 'N/A'),
                'P/E Ratio': info.get('trailingPE', 'N/A'),
                '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
                'Dividend Yield': info.get('dividendYield', 'N/A')
            }
        except Exception as e:
            print(f"❌ Error fetching company info: {e}")
            return None
    
    @staticmethod
    def get_realtime_quote(symbol):
        """Get real-time quote data"""
        try:
            ticker = yf.Ticker(symbol)
            quote = ticker.history(period="1d", interval="1m")
            
            if not quote.empty:
                latest = quote.iloc[-1]
                return {
                    'Symbol': symbol,
                    'Price': round(latest['Close'], 2),
                    'Volume': int(latest['Volume']),
                    'High': round(latest['High'], 2),
                    'Low': round(latest['Low'], 2),
                    'Open': round(latest['Open'], 2),
                    'Time': quote.index[-1]
                }
            return None
        except Exception as e:
            print(f"❌ Error fetching quote: {e}")
            return None
    
    @staticmethod
    def get_market_indices():
        """Get major market indices"""
        indices = {
            'S&P 500': '^GSPC',
            'NASDAQ': '^IXIC',
            'Dow Jones': '^DJI',
            'VIX': '^VIX'
        }
        
        market_data = {}
        
        for name, symbol in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d")
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    change = ((price - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100
                    
                    market_data[name] = {
                        'Symbol': symbol,
                        'Price': round(price, 2),
                        'Change %': round(change, 2)
                    }
            except:
                pass
        
        return market_data
    
    @staticmethod
    def get_crypto_data(symbol, start_date, end_date=None):
        """Fetch cryptocurrency data"""
        try:
            # Convert crypto symbol to Yahoo Finance format
            if not symbol.endswith('-USD'):
                symbol = f"{symbol}-USD"
            
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                raise ValueError(f"No data found for {symbol}")
            
            print(f"✅ Crypto data fetched for {symbol}: {len(df)} rows")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching crypto data: {e}")
            return None
    
    @staticmethod
    def save_to_csv(data, filename):
        """Save data to CSV file"""
        try:
            data.to_csv(filename)
            print(f"💾 Data saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False
    
    @staticmethod
    def load_from_csv(filename):
        """Load data from CSV file"""
        try:
            df = pd.read_csv(filename, index_col=0, parse_dates=True)
            print(f"📂 Data loaded from {filename}: {len(df)} rows")
            return df
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Test data fetching
    print("="*50)
    print("TESTING DATA FETCHER")
    print("="*50)
    
    # Get historical data
    print("\n1. Fetching historical data...")
    data = DataFetcher.get_historical_data("AAPL", "2024-01-01", "2024-06-01")
    if data is not None:
        print(f"   Rows: {len(data)}")
        print(f"   Columns: {list(data.columns)}")
    
    # Get live price
    print("\n2. Fetching live price...")
    price = DataFetcher.get_live_price("AAPL")
    print(f"   AAPL Current Price: ${price}")
    
    # Get company info
    print("\n3. Fetching company info...")
    info = DataFetcher.get_company_info("AAPL")
    if info:
        for key, value in info.items():
            print(f"   {key}: {value}")
    
    # Get multiple symbols
    print("\n4. Fetching multiple symbols...")
    symbols = ["AAPL", "GOOGL", "MSFT"]
    multi_data = DataFetcher.get_multiple_symbols(symbols, "2024-06-01")
    for sym, df in multi_data.items():
        print(f"   {sym}: {len(df)} rows")
    
    # Get market indices
    print("\n5. Fetching market indices...")
    indices = DataFetcher.get_market_indices()
    for name, data in indices.items():
        print(f"   {name}: ${data['Price']} ({data['Change %']:.2f}%)")
    
    print("\n✅ Data fetcher test complete!")