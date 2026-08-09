import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class Backtest:
    def __init__(self, initial_capital=10000, commission=0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.results = None
        
    def run(self, data, strategy):
        """Run backtest with given strategy"""
        df = data.copy()
        
        # Generate signals
        df = strategy.generate_signals(df)
        
        # Initialize portfolio tracking
        df['Holdings'] = 0.0
        df['Cash'] = float(self.initial_capital)
        df['Total'] = float(self.initial_capital)
        df['Returns'] = 0.0
        
        position = 0
        entry_price = 0
        
        for i in range(1, len(df)):
            current_price = df['Close'].iloc[i]
            
            # Buy signal
            if df['Position'].iloc[i] == 1 and position == 0:
                # Calculate number of shares to buy
                cash_available = df['Cash'].iloc[i-1]
                shares_to_buy = (cash_available * 0.95) // current_price
                
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    commission_cost = cost * self.commission
                    
                    df.loc[df.index[i], 'Holdings'] = shares_to_buy * current_price
                    df.loc[df.index[i], 'Cash'] = df['Cash'].iloc[i-1] - cost - commission_cost
                    position = shares_to_buy
                    entry_price = current_price
            
            # Sell signal
            elif df['Position'].iloc[i] == -1 and position > 0:
                revenue = position * current_price
                commission_cost = revenue * self.commission
                
                df.loc[df.index[i], 'Holdings'] = 0
                df.loc[df.index[i], 'Cash'] = df['Cash'].iloc[i-1] + revenue - commission_cost
                position = 0
                entry_price = 0
            
            # Hold position
            else:
                df.loc[df.index[i], 'Holdings'] = position * current_price
                df.loc[df.index[i], 'Cash'] = df['Cash'].iloc[i-1]
            
            # Update total value and returns
            df.loc[df.index[i], 'Total'] = df['Holdings'].iloc[i] + df['Cash'].iloc[i]
            df.loc[df.index[i], 'Returns'] = (df['Total'].iloc[i] / self.initial_capital - 1) * 100
        
        self.results = df
        return self.calculate_metrics()
    
    def calculate_metrics(self):
        """Calculate performance metrics"""
        if self.results is None:
            return {}
        
        df = self.results
        
        # Calculate total return
        total_return = df['Returns'].iloc[-1]
        
        # Calculate daily returns
        df['Daily_Returns'] = df['Total'].pct_change()
        
        # Calculate Sharpe Ratio (assuming risk-free rate of 2%)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        excess_returns = df['Daily_Returns'] - risk_free_rate
        
        if excess_returns.std() != 0 and not np.isnan(excess_returns.std()):
            sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        else:
            sharpe_ratio = 0
        
        # Calculate Maximum Drawdown
        df['Cumulative_Max'] = df['Total'].expanding().max()
        df['Drawdown'] = (df['Total'] - df['Cumulative_Max']) / df['Cumulative_Max'] * 100
        max_drawdown = df['Drawdown'].min()
        
        # Calculate Win Rate
        trades = df[df['Position'] != 0]
        if len(trades) > 0:
            winning_trades = len(trades[trades['Returns'] > 0])
            total_trades = len(trades)
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        else:
            win_rate = 0
            total_trades = 0
            winning_trades = 0
        
        # Count buy and sell signals
        buy_signals = len(df[df['Position'] == 1])
        sell_signals = len(df[df['Position'] == -1])
        
        # Calculate CAGR (Compound Annual Growth Rate)
        days = len(df)
        years = days / 252
        if years > 0:
            cagr = ((df['Total'].iloc[-1] / self.initial_capital) ** (1/years) - 1) * 100
        else:
            cagr = 0
        
        # Calculate volatility
        volatility = df['Daily_Returns'].std() * np.sqrt(252) * 100
        
        metrics = {
            'Initial Capital ($)': round(self.initial_capital, 2),
            'Final Value ($)': round(df['Total'].iloc[-1], 2),
            'Total Return (%)': round(total_return, 2),
            'CAGR (%)': round(cagr, 2),
            'Sharpe Ratio': round(sharpe_ratio, 2),
            'Max Drawdown (%)': round(max_drawdown, 2),
            'Volatility (%)': round(volatility, 2),
            'Win Rate (%)': round(win_rate, 2),
            'Total Trades': total_trades,
            'Winning Trades': winning_trades,
            'Buy Signals': buy_signals,
            'Sell Signals': sell_signals
        }
        
        return metrics
    
    def plot_results(self, save_path='backtest_results.png'):
        """Plot backtest results"""
        if self.results is None:
            print("❌ No results to plot. Run backtest first!")
            return
        
        df = self.results
        fig, axes = plt.subplots(3, 1, figsize=(14, 12))
        
        # Plot 1: Price with Buy/Sell signals
        axes[0].plot(df.index, df['Close'], label='Close Price', color='blue', alpha=0.6, linewidth=1.5)
        
        # Plot SMAs if they exist
        if 'SMA_short' in df.columns:
            axes[0].plot(df.index, df['SMA_short'], label='SMA Short', color='orange', alpha=0.7, linewidth=1)
        if 'SMA_long' in df.columns:
            axes[0].plot(df.index, df['SMA_long'], label='SMA Long', color='red', alpha=0.7, linewidth=1)
        
        # Plot RSI if exists (on secondary axis)
        if 'RSI' in df.columns:
            ax2 = axes[0].twinx()
            ax2.plot(df.index, df['RSI'], label='RSI', color='purple', alpha=0.3, linewidth=0.8)
            ax2.axhline(y=70, color='red', linestyle='--', alpha=0.3)
            ax2.axhline(y=30, color='green', linestyle='--', alpha=0.3)
            ax2.set_ylabel('RSI', color='purple')
            ax2.legend(loc='upper right')
        
        # Mark buy/sell signals
        buy_signals = df[df['Position'] == 1]
        sell_signals = df[df['Position'] == -1]
        
        axes[0].scatter(buy_signals.index, buy_signals['Close'], 
                       color='green', marker='^', s=100, label='Buy Signal', zorder=5)
        axes[0].scatter(sell_signals.index, sell_signals['Close'], 
                       color='red', marker='v', s=100, label='Sell Signal', zorder=5)
        
        axes[0].set_title('Trading Signals', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Price ($)')
        axes[0].legend(loc='upper left')
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Portfolio Value
        axes[1].plot(df.index, df['Total'], label='Portfolio Value', color='darkblue', linewidth=2)
        axes[1].fill_between(df.index, self.initial_capital, df['Total'], 
                             where=(df['Total'] >= self.initial_capital), 
                             color='green', alpha=0.2, label='Profit Zone')
        axes[1].fill_between(df.index, self.initial_capital, df['Total'], 
                             where=(df['Total'] < self.initial_capital), 
                             color='red', alpha=0.2, label='Loss Zone')
        axes[1].axhline(y=self.initial_capital, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
        
        axes[1].set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Portfolio Value ($)')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Drawdown
        axes[2].fill_between(df.index, 0, df['Drawdown'], color='red', alpha=0.3)
        axes[2].plot(df.index, df['Drawdown'], color='darkred', linewidth=1)
        axes[2].axhline(y=0, color='black', linestyle='-', alpha=0.2)
        
        axes[2].set_title('Drawdown (%)', fontsize=14, fontweight='bold')
        axes[2].set_ylabel('Drawdown (%)')
        axes[2].set_xlabel('Date')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Chart saved as {save_path}")
        
        plt.show()
        return fig
    
    def compare_strategies(self, data, strategies_dict):
        """Compare multiple strategies"""
        results = {}
        
        for name, strategy in strategies_dict.items():
            print(f"Testing {name}...")
            self.results = None  # Reset results
            metrics = self.run(data.copy(), strategy)
            results[name] = metrics
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(results).T
        print("\n" + "="*60)
        print("📊 STRATEGY COMPARISON")
        print("="*60)
        print(comparison_df.to_string())
        print("="*60)
        
        return comparison_df
    
    def generate_report(self, filename='backtest_report.txt'):
        """Generate text report of backtest results"""
        if self.results is None:
            print("❌ No results to report. Run backtest first!")
            return
        
        metrics = self.calculate_metrics()
        
        report = []
        report.append("="*60)
        report.append("📊 TRADING BOT BACKTEST REPORT")
        report.append("="*60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("PERFORMANCE METRICS:")
        report.append("-"*40)
        
        for key, value in metrics.items():
            report.append(f"{key}: {value}")
        
        report.append("")
        report.append("-"*40)
        report.append("Note: Past performance does not guarantee future results.")
        report.append("="*60)
        
        # Save to file
        with open(filename, 'w') as f:
            f.write('\n'.join(report))
        
        # Print to console
        print('\n'.join(report))
        print(f"\n📄 Report saved to {filename}")


# Example usage (uncomment to test)
"""
if __name__ == "__main__":
    from strategies.sma_crossover import SMACrossover
    from strategies.rsi_strategy import RSIStrategy
    from utils.data_fetcher import DataFetcher
    
    # Fetch data
    print("Fetching data...")
    data = DataFetcher.get_historical_data("AAPL", "2020-01-01", "2023-12-31")
    
    if data is not None:
        # Test SMA Crossover
        print("\n" + "="*50)
        print("Testing SMA Crossover Strategy")
        print("="*50)
        
        sma_strategy = SMACrossover(short_window=20, long_window=50)
        backtest = Backtest(initial_capital=10000)
        metrics = backtest.run(data, sma_strategy)
        
        for key, value in metrics.items():
            print(f"{key}: {value}")
        
        # Plot results
        backtest.plot_results()
        
        # Generate report
        backtest.generate_report()
        
        # Compare with RSI
        print("\n" + "="*50)
        print("Strategy Comparison")
        print("="*50)
        
        strategies = {
            'SMA Crossover': SMACrossover(20, 50),
            'RSI Strategy': RSIStrategy(14, 70, 30)
        }
        
        comparison = backtest.compare_strategies(data, strategies)
"""