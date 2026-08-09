import pandas as pd
import numpy as np

class RSIStrategy:
    def __init__(self, period=14, overbought=70, oversold=30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.name = "RSI Strategy"
        
    def calculate_rsi(self, data):
        """Calculate RSI (Relative Strength Index)"""
        df = data.copy()
        
        # Calculate price changes
        delta = df['Close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=self.period, min_periods=1).mean()
        avg_loss = loss.rolling(window=self.period, min_periods=1).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    def generate_signals(self, data):
        """Generate trading signals based on RSI"""
        df = self.calculate_rsi(data)
        
        # Generate signals
        df['Signal'] = 0
        
        # Oversold condition - Buy signal
        df.loc[df['RSI'] < self.oversold, 'Signal'] = 1
        
        # Overbought condition - Sell signal
        df.loc[df['RSI'] > self.overbought, 'Signal'] = -1
        
        # Generate trading orders
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def get_signals(self, data):
        """Return current signal for live trading"""
        df = self.generate_signals(data)
        
        if len(df) < 2:
            return 0
        
        # Check for RSI signals
        # Buy signal: RSI crosses above oversold level
        if (df['RSI'].iloc[-1] > self.oversold and 
            df['RSI'].iloc[-2] <= self.oversold):
            return 1  # Buy signal
        
        # Sell signal: RSI crosses below overbought level
        elif (df['RSI'].iloc[-1] < self.overbought and 
              df['RSI'].iloc[-2] >= self.overbought):
            return -1  # Sell signal
        
        return 0  # Hold
    
    def get_current_rsi(self, data):
        """Get current RSI value"""
        df = self.calculate_rsi(data)
        
        if len(df) < 1:
            return None
        
        return round(df['RSI'].iloc[-1], 2)
    
    def get_rsi_status(self, data):
        """Get RSI status and recommendation"""
        rsi = self.get_current_rsi(data)
        
        if rsi is None:
            return "No data available"
        
        if rsi >= self.overbought:
            status = "OVERBOUGHT"
            recommendation = "SELL"
            color = "🔴"
        elif rsi <= self.oversold:
            status = "OVERSOLD"
            recommendation = "BUY"
            color = "🟢"
        else:
            status = "NEUTRAL"
            recommendation = "HOLD"
            color = "🟡"
        
        return {
            'RSI': rsi,
            'Status': status,
            'Recommendation': recommendation,
            'Signal': color,
            'Overbought Level': self.overbought,
            'Oversold Level': self.oversold
        }
    
    def get_current_values(self, data):
        """Get current trading values"""
        df = self.calculate_rsi(data)
        
        if len(df) < 1:
            return None
        
        status = self.get_rsi_status(data)
        
        return {
            'Current Price': round(df['Close'].iloc[-1], 2),
            'RSI': status['RSI'],
            'Status': status['Status'],
            'Signal': f"{status['Signal']} {status['Recommendation']}",
            'Overbought': self.overbought,
            'Oversold': self.oversold
        }
    
    def get_divergence(self, data, lookback=20):
        """Detect RSI divergence (bullish/bearish)"""
        df = self.calculate_rsi(data)
        
        if len(df) < lookback:
            return "Not enough data"
        
        recent_data = df.tail(lookback)
        
        # Get price and RSI highs/lows
        price_high = recent_data['Close'].max()
        price_low = recent_data['Close'].min()
        rsi_high = recent_data['RSI'].max()
        rsi_low = recent_data['RSI'].min()
        
        # Check for divergences
        # Bearish Divergence: Price makes higher high, RSI makes lower high
        if (recent_data['Close'].iloc[-1] >= price_high * 0.99 and 
            recent_data['RSI'].iloc[-1] < rsi_high * 0.95):
            return "⚠️ Bearish Divergence Detected"
        
        # Bullish Divergence: Price makes lower low, RSI makes higher low
        elif (recent_data['Close'].iloc[-1] <= price_low * 1.01 and 
              recent_data['RSI'].iloc[-1] > rsi_low * 1.05):
            return "💡 Bullish Divergence Detected"
        
        return "No divergence detected"
    
    def optimize_parameters(self, data, period_range, ob_range, os_range):
        """Find optimal RSI parameters"""
        best_return = -float('inf')
        best_params = None
        results = []
        
        print("Optimizing RSI parameters...")
        
        for period in period_range:
            for ob in ob_range:
                for os in os_range:
                    if ob <= os:
                        continue
                    
                    # Create temporary strategy
                    temp_strategy = RSIStrategy(period, ob, os)
                    
                    # Generate signals
                    df = temp_strategy.generate_signals(data.copy())
                    
                    # Simple backtest
                    initial_capital = 10000
                    capital = initial_capital
                    position = 0
                    
                    for i in range(1, len(df)):
                        price = df['Close'].iloc[i]
                        
                        # Buy signal
                        if df['Signal'].iloc[i] == 1 and df['Signal'].iloc[i-1] != 1 and position == 0:
                            position = capital / price
                            capital = 0
                        
                        # Sell signal
                        elif df['Signal'].iloc[i] == -1 and df['Signal'].iloc[i-1] != -1 and position > 0:
                            capital = position * price
                            position = 0
                    
                    final_value = capital + (position * df['Close'].iloc[-1])
                    total_return = ((final_value / initial_capital) - 1) * 100
                    
                    results.append({
                        'Period': period,
                        'Overbought': ob,
                        'Oversold': os,
                        'Return (%)': round(total_return, 2)
                    })
                    
                    if total_return > best_return:
                        best_return = total_return
                        best_params = (period, ob, os)
        
        # Convert to DataFrame
        results_df = pd.DataFrame(results)
        
        print(f"✅ Best parameters: RSI({best_params[0]}, {best_params[1]}, {best_params[2]})")
        print(f"📈 Best return: {best_return:.2f}%")
        
        return best_params, results_df
    
    def describe(self):
        """Return strategy description"""
        description = f"""
        ╔══════════════════════════════════════╗
        ║      RSI TRADING STRATEGY          ║
        ╠══════════════════════════════════════╣
        ║ RSI Period: {self.period} days                  ║
        ║ Overbought Level: {self.overbought}                   ║
        ║ Oversold Level: {self.oversold}                    ║
        ╠══════════════════════════════════════╣
        ║ BUY Signal: RSI crosses above      ║
        ║            oversold level          ║
        ║ SELL Signal: RSI crosses below     ║
        ║             overbought level       ║
        ╠══════════════════════════════════════╣
        ║ RSI > {self.overbought} = Overbought (Sell)       ║
        ║ RSI < {self.oversold} = Oversold (Buy)         ║
        ╚══════════════════════════════════════╝
        """
        return description


# Example usage
if __name__ == "__main__":
    import yfinance as yf
    
    # Get sample data
    print("Testing RSI Strategy...")
    ticker = yf.Ticker("AAPL")
    data = ticker.history(start="2023-01-01", end="2024-01-01")
    
    # Create strategy
    strategy = RSIStrategy(period=14, overbought=70, oversold=30)
    
    # Print description
    print(strategy.describe())
    
    # Generate signals
    signals = strategy.generate_signals(data)
    
    # Get RSI status
    status = strategy.get_rsi_status(data)
    print(f"\nCurrent RSI Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Get divergence
    divergence = strategy.get_divergence(data)
    print(f"\nDivergence Check: {divergence}")
    
    # Count signals
    buy_count = len(signals[signals['Signal'] == 1])
    sell_count = len(signals[signals['Signal'] == -1])
    print(f"\nTotal Buy Signals: {buy_count}")
    print(f"Total Sell Signals: {sell_count}")
    
    # Show last 5 days
    print("\nLast 5 days of RSI signals:")
    print(signals[['Close', 'RSI', 'Signal', 'Position']].tail())