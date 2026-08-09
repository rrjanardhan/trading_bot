"""
🤖 trading_bot - Interactive Backtest Runner
👤 rrjanardhan
📊 Enter stock & capital at runtime
"""

from src.utils.data_fetcher import DataFetcher
from src.strategies.sma_crossover import SMACrossover
from src.strategies.rsi_strategy import RSIStrategy
from src.backtest import Backtest
import pandas as pd
from datetime import datetime

def get_user_input():
    """Get stock and capital from user"""
    print("\n" + "="*60)
    print("📊 BACKTEST SETUP")
    print("="*60)
    
    # Get stock symbol
    print("\n📈 Enter Stock Symbol:")
    print("   Examples: AAPL, RELIANCE.NS, INFY.NS, TCS.NS")
    symbol = input("👉 Stock: ").strip().upper()
    if not symbol:
        symbol = "AAPL"
        print(f"   Using default: {symbol}")
    
    # Get capital
    print("\n💰 Enter Capital Amount:")
    capital_input = input("👉 Capital (e.g., 10000): ").strip()
    if capital_input and capital_input.isdigit():
        capital = int(capital_input)
    else:
        capital = 10000
        print(f"   Using default: ₹{capital:,}")
    
    # Get date range
    print("\n📅 Enter Backtest Period (or press Enter for default):")
    start = input("👉 Start Date (YYYY-MM-DD, default: 2022-01-01): ").strip()
    if not start:
        start = "2022-01-01"
    
    end = input("👉 End Date (YYYY-MM-DD, default: today): ").strip()
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")
    
    return symbol, capital, start, end

def choose_strategy():
    """Let user choose strategy"""
    print("\n" + "="*60)
    print("📊 CHOOSE STRATEGY")
    print("="*60)
    print("1. SMA Crossover")
    print("2. RSI Strategy")
    
    choice = input("\n👉 Choice (1-2): ").strip()
    
    if choice == "1":
        print("\n⚙️ SMA Parameters:")
        short = input("   Short SMA (default: 20): ").strip()
        long = input("   Long SMA (default: 50): ").strip()
        
        short = int(short) if short.isdigit() else 20
        long = int(long) if long.isdigit() else 50
        
        return SMACrossover(short, long)
    
    else:
        print("\n⚙️ RSI Parameters:")
        period = input("   RSI Period (default: 14): ").strip()
        ob = input("   Overbought (default: 70): ").strip()
        os = input("   Oversold (default: 30): ").strip()
        
        period = int(period) if period.isdigit() else 14
        ob = int(ob) if ob.isdigit() else 70
        os = int(os) if os.isdigit() else 30
        
        return RSIStrategy(period, ob, os)

def run_single_backtest():
    """Run single strategy backtest with user input"""
    
    # Get user inputs
    symbol, capital, start_date, end_date = get_user_input()
    strategy = choose_strategy()
    
    print("\n" + "="*60)
    print("🔄 RUNNING BACKTEST...")
    print("="*60)
    print(f"Stock: {symbol}")
    print(f"Capital: ₹{capital:,}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Strategy: {strategy.name}")
    print("="*60)
    
    # Fetch data
    print(f"\n📥 Fetching data for {symbol}...")
    data = DataFetcher.get_historical_data(symbol, start_date, end_date)
    
    if data is None or data.empty:
        print(f"❌ Failed to fetch data for {symbol}")
        print("Check if symbol is correct (use .NS for Indian stocks)")
        return
    
    print(f"✅ Loaded {len(data)} days of data")
    
    # Run backtest
    backtest = Backtest(initial_capital=capital)
    metrics = backtest.run(data, strategy)
    
    # Display results
    print("\n" + "="*60)
    print("📊 BACKTEST RESULTS")
    print("="*60)
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    print("="*60)
    
    # Plot results
    print("\n📈 Generating charts...")
    backtest.plot_results(save_path=f'backtest_{symbol}_{datetime.now().strftime("%Y%m%d")}.png')
    
    # Generate report
    backtest.generate_report(f'report_{symbol}_{datetime.now().strftime("%Y%m%d")}.txt')
    
    return metrics

def run_comparison():
    """Compare multiple strategies with user input"""
    
    # Get user inputs
    symbol, capital, start_date, end_date = get_user_input()
    
    print("\n" + "="*60)
    print("🔄 COMPARING STRATEGIES...")
    print("="*60)
    
    # Fetch data
    print(f"\n📥 Fetching data for {symbol}...")
    data = DataFetcher.get_historical_data(symbol, start_date, end_date)
    
    if data is None or data.empty:
        print(f"❌ Failed to fetch data for {symbol}")
        return
    
    print(f"✅ Loaded {len(data)} days of data")
    
    # Define strategies to compare
    strategies = {
        'SMA (20,50)': SMACrossover(20, 50),
        'SMA (10,30)': SMACrossover(10, 30),
        'SMA (50,200)': SMACrossover(50, 200),
        'RSI (14,70,30)': RSIStrategy(14, 70, 30),
        'RSI (21,80,20)': RSIStrategy(21, 80, 20)
    }
    
    # Compare
    backtest = Backtest(initial_capital=capital)
    comparison = backtest.compare_strategies(data, strategies)
    
    # Save
    comparison.to_csv(f'comparison_{symbol}.csv')
    print(f"\n💾 Saved to comparison_{symbol}.csv")
    
    return comparison

def main_menu():
    """Main interactive menu"""
    print("""
╔══════════════════════════════════════╗
║   🤖 trading_bot by rrjanardhan    ║
║   📊 Interactive Backtest          ║
╠══════════════════════════════════════╣
║  1. 🚀 Single Backtest              ║
║  2. 🔄 Compare All Strategies       ║
║  3. ❌ Exit                         ║
╚══════════════════════════════════════╝
    """)
    
    choice = input("👉 Enter choice (1-3): ").strip()
    
    if choice == "1":
        run_single_backtest()
    elif choice == "2":
        run_comparison()
    elif choice == "3":
        print("\n👋 Goodbye!")
        return False
    else:
        print("❌ Invalid choice")
    
    return True

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════╗
║   🤖 trading_bot                   ║
║   👤 rrjanardhan                   ║
║   📊 No default values!            ║
║   📝 Enter everything at runtime   ║
╚══════════════════════════════════════╝
    """)
    
    running = True
    while running:
        running = main_menu()
        if running:
            input("\n📱 Press Enter to continue...")