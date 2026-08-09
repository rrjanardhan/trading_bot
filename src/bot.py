import pandas as pd
import numpy as np
from datetime import datetime
import schedule
import time
import json

class TradingBot:
    def __init__(self, strategy, symbol, initial_capital=10000):
        self.strategy = strategy
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position = 0
        self.entry_price = 0
        self.trades = []
        
    def execute_trade(self, signal, current_price):
        """Execute trade based on signal"""
        timestamp = datetime.now()
        
        # Buy signal
        if signal == 1 and self.position == 0:
            shares_to_buy = (self.cash * 0.95) // current_price
            if shares_to_buy > 0:
                cost = shares_to_buy * current_price
                self.cash -= cost
                self.position = shares_to_buy
                self.entry_price = current_price
                
                trade = {
                    'timestamp': timestamp,
                    'type': 'BUY',
                    'price': current_price,
                    'shares': shares_to_buy,
                    'cost': cost,
                    'cash_remaining': self.cash
                }
                self.trades.append(trade)
                print(f"✅ BUY: {shares_to_buy} shares at ${current_price:.2f}")
                return trade
        
        # Sell signal
        elif signal == -1 and self.position > 0:
            revenue = self.position * current_price
            self.cash += revenue
            profit = revenue - (self.position * self.entry_price)
            
            trade = {
                'timestamp': timestamp,
                'type': 'SELL',
                'price': current_price,
                'shares': self.position,
                'revenue': revenue,
                'profit': profit,
                'profit_percent': (profit / (self.position * self.entry_price)) * 100,
                'cash_remaining': self.cash
            }
            self.trades.append(trade)
            
            print(f"❌ SELL: {self.position} shares at ${current_price:.2f}")
            print(f"💰 Profit: ${profit:.2f} ({trade['profit_percent']:.2f}%)")
            
            self.position = 0
            self.entry_price = 0
            return trade
        
        return None
    
    def get_portfolio_value(self, current_price):
        """Calculate current portfolio value"""
        holdings_value = self.position * current_price
        return self.cash + holdings_value
    
    def get_stats(self, current_price):
        """Get current trading statistics"""
        total_value = self.get_portfolio_value(current_price)
        total_return = ((total_value / self.initial_capital) - 1) * 100
        
        return {
            'Symbol': self.symbol,
            'Cash': f"${self.cash:.2f}",
            'Position': f"{self.position} shares",
            'Current Price': f"${current_price:.2f}",
            'Portfolio Value': f"${total_value:.2f}",
            'Total Return': f"{total_return:.2f}%",
            'Total Trades': len(self.trades)
        }
    
    def print_stats(self, current_price):
        """Display current statistics"""
        stats = self.get_stats(current_price)
        print("\n" + "="*50)
        print("📊 PORTFOLIO STATUS")
        print("="*50)
        for key, value in stats.items():
            print(f"{key}: {value}")
        print("="*50)
    
    def save_trades(self, filename='trades.json'):
        """Save trade history to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.trades, f, default=str, indent=2)
        print(f"💾 Trade history saved to {filename}")
    
    def get_trade_summary(self):
        """Get summary of all trades"""
        if not self.trades:
            return "No trades executed yet."
        
        summary = {
            'Total Trades': len(self.trades),
            'Buy Trades': len([t for t in self.trades if t['type'] == 'BUY']),
            'Sell Trades': len([t for t in self.trades if t['type'] == 'SELL']),
        }
        
        # Calculate profits
        profits = [t['profit'] for t in self.trades if t['type'] == 'SELL']
        if profits:
            summary['Total Profit'] = f"${sum(profits):.2f}"
            summary['Average Profit'] = f"${np.mean(profits):.2f}"
            summary['Winning Trades'] = len([p for p in profits if p > 0])
            summary['Losing Trades'] = len([p for p in profits if p < 0])
            if summary['Winning Trades'] + summary['Losing Trades'] > 0:
                summary['Win Rate'] = f"{(summary['Winning Trades'] / (summary['Winning Trades'] + summary['Losing Trades'])) * 100:.2f}%"
        
        return summary
    
    def print_trade_summary(self):
        """Display trade summary"""
        summary = self.get_trade_summary()
        print("\n" + "="*50)
        print("📈 TRADE SUMMARY")
        print("="*50)
        if isinstance(summary, str):
            print(summary)
        else:
            for key, value in summary.items():
                print(f"{key}: {value}")
        print("="*50)
    
    def reset(self):
        """Reset bot to initial state"""
        self.cash = self.initial_capital
        self.position = 0
        self.entry_price = 0
        self.trades = []
        print("🔄 Bot reset to initial state")

# Example usage (uncomment to test)
"""
if __name__ == "__main__":
    from strategies.sma_crossover import SMACrossover
    from utils.data_fetcher import DataFetcher
    
    # Initialize components
    strategy = SMACrossover(short_window=20, long_window=50)
    bot = TradingBot(strategy=strategy, symbol="AAPL", initial_capital=10000)
    
    # Get current price
    data = DataFetcher.get_historical_data("AAPL", "2024-01-01", datetime.now().strftime("%Y-%m-%d"))
    current_price = DataFetcher.get_live_price("AAPL")
    
    # Get trading signal
    signal = strategy.get_signals(data)
    print(f"Signal: {signal}")
    
    # Execute trade
    bot.execute_trade(signal, current_price)
    
    # Show stats
    bot.print_stats(current_price)
    bot.print_trade_summary()
"""