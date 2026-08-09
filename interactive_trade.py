"""
INTERACTIVE TRADING BOT
No API keys stored - 100% safe to share on GitHub
"""
from src.brokers.zerodha_broker import ZerodhaBroker
from src.strategies.sma_crossover import SMACrossover
from src.strategies.rsi_strategy import RSIStrategy
from src.utils.data_fetcher import DataFetcher
from datetime import datetime
import time
from getpass import getpass

class InteractiveTrader:
    def __init__(self):
        self.broker = ZerodhaBroker()
        self.strategy = None
        self.symbol = None
        self.quantity = 1
        self.is_logged_in = False
        
    def start(self):
        """Main interactive menu"""
        while True:
            print("\n" + "="*60)
            print("🤖 INTERACTIVE TRADING BOT")
            print("="*60)
            print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-"*60)
            
            if not self.is_logged_in:
                print("1. 🔐 Login to Zerodha")
                print("2. ❌ Exit")
            else:
                print("1. 📊 Check Balance & Positions")
                print("2. 💹 Start Trading (Manual)")
                print("3. 🤖 Start Auto Trading")
                print("4. 📝 Paper Trading Test")
                print("5. 🔒 Logout")
                print("6. ❌ Exit")
            
            print("="*60)
            
            choice = input("\n👉 Choose option: ").strip()
            
            if not self.is_logged_in:
                if choice == "1":
                    self.login()
                elif choice == "2":
                    break
            else:
                if choice == "1":
                    self.check_account()
                elif choice == "2":
                    self.manual_trade()
                elif choice == "3":
                    self.auto_trade()
                elif choice == "4":
                    self.paper_trade()
                elif choice == "5":
                    self.logout()
                elif choice == "6":
                    self.logout()
                    break
    
    def login(self):
        """Interactive login"""
        if self.broker.interactive_login():
            self.is_logged_in = True
            
            # Setup strategy
            print("\n📊 Choose Strategy:")
            print("1. SMA Crossover")
            print("2. RSI Strategy")
            
            strat_choice = input("👉 Choice: ").strip()
            
            if strat_choice == "1":
                short = int(input("Short SMA (default 20): ") or 20)
                long = int(input("Long SMA (default 50): ") or 50)
                self.strategy = SMACrossover(short, long)
            else:
                period = int(input("RSI Period (default 14): ") or 14)
                ob = int(input("Overbought (default 70): ") or 70)
                os = int(input("Oversold (default 30): ") or 30)
                self.strategy = RSIStrategy(period, ob, os)
            
            # Choose stock
            self.symbol = input("\n📈 Stock Symbol (e.g., RELIANCE): ").strip().upper()
            self.quantity = int(input("📦 Quantity per trade: ").strip() or 1)
            
            print(f"\n✅ Setup Complete!")
            print(f"   Strategy: {self.strategy.name}")
            print(f"   Symbol: {self.symbol}")
            print(f"   Quantity: {self.quantity}")
    
    def check_account(self):
        """Check account status"""
        self.broker.show_balance()
        self.broker.get_positions()
    
    def manual_trade(self):
        """Manual trading with confirmation"""
        print("\n💹 MANUAL TRADE")
        
        # Get signal
        data = DataFetcher.get_historical_data(
            f"{self.symbol}.NS",
            "2024-01-01",
            datetime.now().strftime("%Y-%m-%d")
        )
        
        if data is not None:
            signal = self.strategy.get_signals(data)
            
            # Get current price
            price = DataFetcher.get_live_price(f"{self.symbol}.NS")
            
            print(f"\n📊 {self.symbol}: ₹{price:,.2f}")
            print(f"🎯 Signal: {'🟢 BUY' if signal==1 else '🔴 SELL' if signal==-1 else '⏸️ HOLD'}")
            
            if signal == 1:
                action = input("\nPlace BUY order? (yes/no): ").strip().lower()
                if action == 'yes':
                    self.broker.place_order(
                        self.symbol,
                        self.quantity,
                        "BUY"
                    )
            
            elif signal == -1:
                # Check if holding
                positions = self.broker.get_positions()
                holding = False
                if positions:
                    for pos in positions.get('net', []):
                        if pos['tradingsymbol'] == self.symbol:
                            holding = True
                            break
                
                if holding:
                    action = input("\nPlace SELL order? (yes/no): ").strip().lower()
                    if action == 'yes':
                        self.broker.place_order(
                            self.symbol,
                            self.quantity,
                            "SELL"
                        )
                else:
                    print("❌ No shares to sell")
    
    def auto_trade(self):
        """Automated trading with confirmation each time"""
        print(f"\n🤖 AUTO TRADING MODE")
        print(f"Symbol: {self.symbol}")
        print(f"Strategy: {self.strategy.name}")
        print(f"Quantity: {self.quantity}")
        print("\n⚠️  Bot will ask confirmation before each trade")
        
        interval = int(input("\n⏱️  Check interval (minutes, default 5): ") or 5)
        print("\n🚀 Starting... Press Ctrl+C to stop")
        
        try:
            while True:
                print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')}")
                
                # Get data and signal
                data = DataFetcher.get_historical_data(
                    f"{self.symbol}.NS",
                    "2024-01-01",
                    datetime.now().strftime("%Y-%m-%d")
                )
                
                if data is not None:
                    signal = self.strategy.get_signals(data)
                    price = DataFetcher.get_live_price(f"{self.symbol}.NS")
                    
                    print(f"📊 {self.symbol}: ₹{price:,.2f}")
                    print(f"🎯 Signal: {signal}")
                    
                    # Auto-execute with confirmation
                    if signal != 0:
                        self.manual_trade()
                    else:
                        print("⏸️  Holding...")
                
                # Countdown
                for i in range(interval * 60, 0, -1):
                    print(f"\r⏳ Next check in {i//60}m {i%60}s...", end='')
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n\n👋 Auto trading stopped")
            self.check_account()
    
    def paper_trade(self):
        """Test with virtual money first"""
        from src.paper_simulator import PaperSimulator
        
        print(f"\n📝 PAPER TRADING (Virtual Money)")
        print(f"Symbol: {self.symbol}")
        print(f"Strategy: {self.strategy.name}")
        
        capital = float(input("Virtual Capital (default 100000): ") or 100000)
        sim = PaperSimulator(capital)
        
        interval = int(input("Check interval (seconds, default 60): ") or 60)
        
        print("\n🚀 Starting paper trading... Press Ctrl+C to stop")
        
        try:
            while True:
                print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')}")
                
                # Get real market data
                data = DataFetcher.get_historical_data(
                    f"{self.symbol}.NS",
                    "2024-01-01",
                    datetime.now().strftime("%Y-%m-%d")
                )
                
                if data is not None:
                    signal = self.strategy.get_signals(data)
                    price = data['Close'].iloc[-1]
                    
                    print(f"📊 {self.symbol}: ₹{price:,.2f}")
                    print(f"🎯 Signal: {'🟢 BUY' if signal==1 else '🔴 SELL' if signal==-1 else '⏸️ HOLD'}")
                    
                    # Simulate trades
                    if signal == 1 and self.symbol not in sim.positions:
                        shares = int((sim.cash * 0.95) / price)
                        if shares > 0:
                            sim.buy(self.symbol, shares, price)
                    
                    elif signal == -1 and self.symbol in sim.positions:
                        shares = sim.positions[self.symbol]['shares']
                        sim.sell(self.symbol, shares, price)
                    
                    sim.get_performance({self.symbol: price})
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n📊 Final Results:")
            sim.get_performance({self.symbol: price})
            sim.save_session()
    
    def logout(self):
        """Secure logout"""
        confirm = input("\n⚠️  Logout and clear all credentials? (yes/no): ")
        if confirm.lower() == 'yes':
            self.broker.logout()
            self.is_logged_in = False
            self.strategy = None

# Start the bot
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════╗
    ║   🔐 SECURE TRADING BOT            ║
    ║   No API keys stored anywhere      ║
    ║   100% Interactive & Safe          ║
    ╚══════════════════════════════════════╝
    """)
    
    trader = InteractiveTrader()
    
    try:
        trader.start()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    finally:
        # Ensure credentials are cleared
        if trader.is_logged_in:
            trader.broker.logout()
    
    print("\n🔒 All credentials cleared")
    print("✅ Safe to close")