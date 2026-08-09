from src.utils.data_fetcher import DataFetcher
from src.strategies.sma_crossover import SMACrossover
from src.strategies.rsi_strategy import RSIStrategy
from src.backtest import Backtest
from config import Config
import pandas as pd

def run_single_backtest():
    """Run single strategy backtest"""
    print("\n" + "="*60)
    print("📊 SINGLE STRATEGY BACKTEST")
    print("="*60)
    
    # Choose strategy
    print("\nSelect Strategy:")
    print("1. SMA Crossover")
    print("2. RSI Strategy")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    # Fetch data
    print(f"\n📥 Fetching data for {Config.SYMBOL}...")
    data = DataFetcher.get_historical_data(
        Config.SYMBOL,
        Config.BACKTEST_START,
        Config.BACKTEST_END
    )
    
    if data is None:
        print("❌ Failed to fetch data")
        return
    
    print(f"✅ Data loaded: {len(data)} trading days")
    
    # Select strategy
    if choice == "1":
        strategy = SMACrossover(
            short_window=Config.SMA_SHORT,
            long_window=Config.SMA_LONG
        )
        print(f"\n📈 Testing: {strategy.name}")
    elif choice == "2":
        strategy = RSIStrategy(
            period=Config.RSI_PERIOD,
            overbought=Config.RSI_OVERBOUGHT,
            oversold=Config.RSI_OVERSOLD
        )
        print(f"\n📈 Testing: {strategy.name}")
    else:
        print("❌ Invalid choice")
        return
    
    # Run backtest
    backtest = Backtest(initial_capital=Config.INITIAL_CAPITAL)
    metrics = backtest.run(data, strategy)
    
    # Display results
    print("\n" + "="*60)
    print("📊 BACKTEST RESULTS")
    print("="*60)
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    print("="*60)
    
    # Plot and save
    print("\n📈 Generating charts...")
    backtest.plot_results(save_path='backtest_results.png')
    
    # Generate report
    backtest.generate_report('backtest_report.txt')
    
    return metrics

def run_strategy_comparison():
    """Compare multiple strategies"""
    print("\n" + "="*60)
    print("📊 STRATEGY COMPARISON")
    print("="*60)
    
    # Fetch data
    print(f"\n📥 Fetching data for {Config.SYMBOL}...")
    data = DataFetcher.get_historical_data(
        Config.SYMBOL,
        Config.BACKTEST_START,
        Config.BACKTEST_END
    )
    
    if data is None:
        print("❌ Failed to fetch data")
        return
    
    print(f"✅ Data loaded: {len(data)} trading days")
    
    # Define strategies
    strategies = {
        'SMA Crossover (20,50)': SMACrossover(20, 50),
        'SMA Crossover (10,30)': SMACrossover(10, 30),
        'SMA Crossover (50,200)': SMACrossover(50, 200),
        'RSI Strategy (14,70,30)': RSIStrategy(14, 70, 30),
        'RSI Strategy (21,80,20)': RSIStrategy(21, 80, 20)
    }
    
    # Compare strategies
    backtest = Backtest(initial_capital=Config.INITIAL_CAPITAL)
    comparison = backtest.compare_strategies(data, strategies)
    
    # Save comparison
    comparison.to_csv('strategy_comparison.csv')
    print("\n💾 Comparison saved to strategy_comparison.csv")
    
    # Find best strategy
    best_strategy = comparison['Total Return (%)'].idxmax()
    best_return = comparison['Total Return (%)'].max()
    
    print("\n" + "="*60)
    print("🏆 BEST STRATEGY")
    print("="*60)
    print(f"Strategy: {best_strategy}")
    print(f"Return: {best_return:.2f}%")
    print("="*60)
    
    return comparison

def run_parameter_optimization():
    """Optimize strategy parameters"""
    print("\n" + "="*60)
    print("🔧 PARAMETER OPTIMIZATION")
    print("="*60)
    
    # Fetch data
    print(f"\n📥 Fetching data for {Config.SYMBOL}...")
    data = DataFetcher.get_historical_data(
        Config.SYMBOL,
        Config.BACKTEST_START,
        Config.BACKTEST_END
    )
    
    if data is None:
        print("❌ Failed to fetch data")
        return
    
    # Choose strategy to optimize
    print("\nSelect Strategy to Optimize:")
    print("1. SMA Crossover")
    print("2. RSI Strategy")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == "1":
        print("\n🔄 Optimizing SMA Crossover parameters...")
        strategy = SMACrossover()
        
        # Define parameter ranges
        short_range = range(5, 51, 5)
        long_range = range(20, 201, 10)
        
        best_params, results = strategy.optimize_parameters(data, short_range, long_range)
        
        # Save results
        results.to_csv('sma_optimization_results.csv')
        
    elif choice == "2":
        print("\n🔄 Optimizing RSI Strategy parameters...")
        strategy = RSIStrategy()
        
        # Define parameter ranges
        period_range = range(7, 22, 1)
        ob_range = range(65, 81, 5)
        os_range = range(20, 36, 5)
        
        best_params, results = strategy.optimize_parameters(data, period_range, ob_range, os_range)
        
        # Save results
        results.to_csv('rsi_optimization_results.csv')
    
    else:
        print("❌ Invalid choice")
        return
    
    print("\n✅ Optimization complete!")
    print(f"Best parameters: {best_params}")

def run_custom_backtest():
    """Run backtest with custom parameters"""
    print("\n" + "="*60)
    print("⚙️ CUSTOM BACKTEST")
    print("="*60)
    
    # Get custom parameters
    symbol = input("\nEnter stock symbol (default: AAPL): ").strip() or "AAPL"
    capital = float(input("Enter initial capital (default: 10000): ") or 10000)
    start_date = input("Enter start date (default: 2020-01-01): ").strip() or "2020-01-01"
    end_date = input("Enter end date (default: today): ").strip() or None
    
    # Fetch data
    print(f"\n📥 Fetching data for {symbol}...")
    data = DataFetcher.get_historical_data(symbol, start_date, end_date)
    
    if data is None:
        print("❌ Failed to fetch data")
        return
    
    # Choose strategy
    print("\nSelect Strategy:")
    print("1. SMA Crossover")
    print("2. RSI Strategy")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == "1":
        short = int(input("Short SMA window (default: 20): ") or 20)
        long = int(input("Long SMA window (default: 50): ") or 50)
        strategy = SMACrossover(short, long)
    elif choice == "2":
        period = int(input("RSI period (default: 14): ") or 14)
        ob = int(input("Overbought level (default: 70): ") or 70)
        os = int(input("Oversold level (default: 30): ") or 30)
        strategy = RSIStrategy(period, ob, os)
    else:
        print("❌ Invalid choice")
        return
    
    # Run backtest
    backtest = Backtest(initial_capital=capital)
    metrics = backtest.run(data, strategy)
    
    # Display results
    print("\n" + "="*60)
    print("📊 CUSTOM BACKTEST RESULTS")
    print("="*60)
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    print("="*60)
    
    # Plot results
    backtest.plot_results()

def main_menu():
    """Main menu for backtest runner"""
    while True:
        print("\n" + "="*60)
        print("🤖 TRADING BOT BACKTEST SUITE")
        print("="*60)
        print("1. Run Single Backtest")
        print("2. Compare Multiple Strategies")
        print("3. Optimize Parameters")
        print("4. Custom Backtest")
        print("5. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            run_single_backtest()
        elif choice == "2":
            run_strategy_comparison()
        elif choice == "3":
            run_parameter_optimization()
        elif choice == "4":
            run_custom_backtest()
        elif choice == "5":
            print("\n👋 Thank you for using Trading Bot Backtest Suite!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()