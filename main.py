from src.utils.data_fetcher import DataFetcher
from src.strategies.sma_crossover import SMACrossover
from src.strategies.rsi_strategy import RSIStrategy
from src.bot import TradingBot
from config import Config
import schedule
import time
from datetime import datetime

class TradingApp:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.strategy = SMACrossover(
            short_window=Config.SMA_SHORT,
            long_window=Config.SMA_LONG
        )
        self.bot = TradingBot(
            strategy=self.strategy,
            symbol=Config.SYMBOL,
            initial_capital=Config.INITIAL_CAPITAL
        )
    
    def run_once(self):
        """Execute one trading iteration"""
        print(f"\n{'='*50}")
        print(f"🕐 Trading Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        # Get historical data for signal generation
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - pd.Timedelta(days=100)).strftime("%Y-%m-%d")
        
        data = self.data_fetcher.get_historical_data(
            Config.SYMBOL,
            start_date,
            end_date
        )
        
        if data is None:
            print("❌ Failed to fetch data")
            return
        
        # Get current price
        current_price = self.data_fetcher.get_live_price(Config.SYMBOL)
        if current_price is None:
            print("❌ Failed to fetch current price")
            return
        
        # Generate signal
        signal = self.strategy.get_signals(data)
        
        # Get signal strength
        signal_strength = self.strategy.get_signal_strength(data)
        
        # Display current market status
        print(f"\n📊 Market Status:")
        print(f"   Symbol: {Config.SYMBOL}")
        print(f"   Current Price: ${current_price}")
        print(f"   Signal: {signal} (1=Buy, -1=Sell, 0=Hold)")
        print(f"   Signal Strength: {signal_strength}%")
        
        # Execute trade
        if signal != 0:
            trade = self.bot.execute_trade(signal, current_price)
        else:
            print("   ⏸️  Holding position...")
        
        # Print stats
        self.bot.print_stats(current_price)
        
        # Save trades
        self.bot.save_trades()
    
    def run_backtest_mode(self):
        """Run in backtest mode"""
        print("\n" + "="*50)
        print("📊 BACKTEST MODE")
        print("="*50)
        
        from src.backtest import Backtest
        
        # Fetch historical data
        data = self.data_fetcher.get_historical_data(
            Config.SYMBOL,
            Config.BACKTEST_START,
            Config.BACKTEST_END
        )
        
        if data is None:
            print("❌ Failed to fetch data for backtesting")
            return
        
        # Run backtest
        backtest = Backtest(initial_capital=Config.INITIAL_CAPITAL)
        metrics = backtest.run(data, self.strategy)
        
        # Display results
        print("\n📈 Backtest Results:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        # Plot results
        backtest.plot_results()
        
        # Generate report
        backtest.generate_report()
    
    def switch_strategy(self, strategy_name):
        """Switch between strategies"""
        if strategy_name.lower() == "rsi":
            self.strategy = RSIStrategy(
                period=Config.RSI_PERIOD,
                overbought=Config.RSI_OVERBOUGHT,
                oversold=Config.RSI_OVERSOLD
            )
            print("✅ Switched to RSI Strategy")
        elif strategy_name.lower() == "sma":
            self.strategy = SMACrossover(
                short_window=Config.SMA_SHORT,
                long_window=Config.SMA_LONG
            )
            print("✅ Switched to SMA Crossover Strategy")
        else:
            print("❌ Unknown strategy. Use 'sma' or 'rsi'")
    
    def start_live_trading(self):
        """Start live trading with schedule"""
        print("\n" + "="*50)
        print("🚀 STARTING LIVE TRADING BOT")
        print("="*50)
        print(f"Symbol: {Config.SYMBOL}")
        print(f"Strategy: {self.strategy.name}")
        print(f"Initial Capital: ${Config.INITIAL_CAPITAL}")
        print("="*50)
        
        # Schedule trading checks
        schedule.every().day.at("09:30").do(self.run_once)
        schedule.every().day.at("10:30").do(self.run_once)
        schedule.every().day.at("11:30").do(self.run_once)
        schedule.every().day.at("12:30").do(self.run_once)
        schedule.every().day.at("13:30").do(self.run_once)
        schedule.every().day.at("14:30").do(self.run_once)
        schedule.every().day.at("15:30").do(self.run_once)
        
        print("\n✅ Bot is running. Waiting for scheduled checks...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Bot stopped by user")
            self.bot.print_trade_summary()

import pandas as pd

if __name__ == "__main__":
    app = TradingApp()
    
    # Choose mode
    print("\n" + "="*50)
    print("🤖 TRADING BOT CONTROL PANEL")
    print("="*50)
    print("1. Run single check")
    print("2. Run backtest")
    print("3. Start live trading")
    print("4. Switch to RSI strategy")
    print("5. Exit")
    print("="*50)
    
    choice = input("Enter your choice (1-5): ").strip()
    
    if choice == "1":
        app.run_once()
    elif choice == "2":
        app.run_backtest_mode()
    elif choice == "3":
        app.start_live_trading()
    elif choice == "4":
        app.switch_strategy("rsi")
        app.run_once()
    elif choice == "5":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")