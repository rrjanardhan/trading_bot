import pandas as pd
import numpy as np

class SMACrossover:
    def __init__(self, short_window=20, long_window=50):
        self.short_window = short_window
        self.long_window = long_window
        self.name = "SMA Crossover Strategy"
        
    def generate_signals(self, data):
        """Generate trading signals based on SMA crossover"""
        df = data.copy()
        
        # Calculate Simple Moving Averages
        df['SMA_short'] = df['Close'].rolling(window=self.short_window, min_periods=1).mean()
        df['SMA_long'] = df['Close'].rolling(window=self.long_window, min_periods=1).mean()
        
        # Generate signals
        df['Signal'] = 0
        
        # Buy signal (1) when short SMA crosses above long SMA
        df.loc[df['SMA_short'] > df['SMA_long'], 'Signal'] = 1
        
        # Sell signal (0) when short SMA crosses below long SMA
        df.loc[df['SMA_short'] <= df['SMA_long'], 'Signal'] = 0
        
        # Generate trading orders (Position)
        # 1 = Buy, -1 = Sell, 0 = Hold
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def get_signals(self, data):
        """Return current signal for live trading"""
        df = self.generate_signals(data)
        
        if len(df) < 2:
            return 0
        
        # Check for crossover signals
        # Golden Cross: Short SMA crosses above Long SMA
        if (df['SMA_short'].iloc[-1] > df['SMA_long'].iloc[-1] and 
            df['SMA_short'].iloc[-2] <= df['SMA_long'].iloc[-2]):
            return 1  # Buy signal
        
        # Death Cross: Short SMA crosses below Long SMA
        elif (df['SMA_short'].iloc[-1] < df['SMA_long'].iloc[-1] and 
              df['SMA_short'].iloc[-2] >= df['SMA_long'].iloc[-2]):
            return -1  # Sell signal
        
        return 0  # Hold
    
    def get_signal_strength(self, data):
        """Calculate signal strength based on SMA distance"""
        df = self.generate_signals(data)
        
        if len(df) < 1:
            return 0
        
        # Calculate percentage difference between SMAs
        sma_diff_percent = ((df['SMA_short'].iloc[-1] - df['SMA_long'].iloc[-1]) / 
                           df['SMA_long'].iloc[-1]) * 100
        
        return round(sma_diff_percent, 2)
    
    def get_current_values(self, data):
        """Get current SMA values"""
        df = self.generate_signals(data)
        
        if len(df) < 1:
            return None
        
        return {
            'Current Price': round(df['Close'].iloc[-1], 2),
            f'SMA {self.short_window}': round(df['SMA_short'].iloc[-1], 2),
            f'SMA {self.long_window}': round(df['SMA_long'].iloc[-1], 2),
            'Signal': 'BUY' if df['SMA_short'].iloc[-1] > df['SMA_long'].iloc[-1] else 'SELL',
            'Strength (%)': self.get_signal_strength(data)
        }
    
    def optimize_parameters(self, data, short_range, long_range):
        """Find optimal SMA parameters"""
        best_return = -float('inf')
        best_params = None
        results = []
        
        print("Optimizing SMA parameters...")
        
        for short in short_range:
            for long in long_range:
                if short >= long:
                    continue
                
                # Create temporary strategy with these parameters
                temp_strategy = SMACrossover(short, long)
                
                # Generate signals
                df = temp_strategy.generate_signals(data.copy())
                
                # Simple backtest
                initial_capital = 10000
                capital = initial_capital
                position = 0
                
                for i in range(1, len(df)):
                    price = df['Close'].iloc[i]
                    
                    # Buy
                    if df['Position'].iloc[i] == 1 and position == 0:
                        position = capital / price
                        capital = 0
                    
                    # Sell
                    elif df['Position'].iloc[i] == -1 and position > 0:
                        capital = position * price
                        position = 0
                
                final_value = capital + (position * df['Close'].iloc[-1])
                total_return = ((final_value / initial_capital) - 1) * 100
                
                results.append({
                    'Short Window': short,
                    'Long Window': long,
                    'Return (%)': round(total_return, 2)
                })
                
                if total_return > best_return:
                    best_return = total_return
                    best_params = (short, long)
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        
        print(f"✅ Best parameters found: SMA({best_params[0]}, {best_params[1]})")
        print(f"📈 Best return: {best_return:.2f}%")
        
        return best_params, results_df
    
    def describe(self):
        """Return strategy description"""
        description = f"""
        ╔══════════════════════════════════════╗
        ║   SMA CROSSOVER STRATEGY           ║
        ╠══════════════════════════════════════╣
        ║ Short Window: {self.short_window} days              ║
        ║ Long Window: {self.long_window} days               ║
        ╠══════════════════════════════════════╣
        ║ BUY Signal: Short SMA crosses      ║
        ║            above Long SMA          ║
        ║ SELL Signal: Short SMA crosses     ║
        ║             below Long SMA         ║
        ╚══════════════════════════════════════╝
        """
        return description


# Example usage
if __name__ == "__main__":
    import yfinance as yf
    
    # Get sample data
    print("Testing SMA Crossover Strategy...")
    ticker = yf.Ticker("AAPL")
    data = ticker.history(start="2023-01-01", end="2024-01-01")
    
    # Create strategy
    strategy = SMACrossover(short_window=20, long_window=50)
    
    # Print strategy description
    print(strategy.describe())
    
    # Generate signals
    signals = strategy.generate_signals(data)
    
    # Get current signal
    current_signal = strategy.get_signals(data)
    print(f"Current Signal: {current_signal}")
    print(f"  (1=Buy, -1=Sell, 0=Hold)")
    
    # Get current values
    values = strategy.get_current_values(data)
    print("\nCurrent Values:")
    for key, value in values.items():
        print(f"  {key}: {value}")
    
    # Count signals
    buy_count = len(signals[signals['Position'] == 1])
    sell_count = len(signals[signals['Position'] == -1])
    print(f"\nTotal Buy Signals: {buy_count}")
    print(f"Total Sell Signals: {sell_count}")
    
    # Show last 5 trading days
    print("\nLast 5 days of signals:")
    print(signals[['Close', 'SMA_short', 'SMA_long', 'Signal', 'Position']].tail())