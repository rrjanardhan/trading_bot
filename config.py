import os
from getpass import getpass
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Trading Parameters
    SYMBOL = "AAPL"
    INITIAL_CAPITAL = 10000
    POSITION_SIZE = 0.1
    
    # Strategy Parameters
    SMA_SHORT = 20
    SMA_LONG = 50
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
    # Backtest Parameters
    BACKTEST_START = "2020-01-01"
    BACKTEST_END = "2023-12-31"
    
    # Interactive credentials (NEVER stored)
    ZERODHA_API_KEY = None
    ZERODHA_API_SECRET = None
    ZERODHA_ACCESS_TOKEN = None
    
    @staticmethod
    def get_credentials():
        """Get credentials interactively - NEVER saves them"""
        print("\n" + "="*50)
        print("🔐 ZERODHA CREDENTIALS")
        print("="*50)
        print("⚠️  Keys are NOT stored or shared")
        print("="*50)
        
        # Try environment first
        if os.getenv("ZERODHA_API_KEY"):
            Config.ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
            Config.ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")
            print("✅ Using credentials from environment")
            return True
        
        # Interactive input
        print("\n📝 Enter your credentials:")
        Config.ZERODHA_API_KEY = getpass("🔑 API Key: ")
        Config.ZERODHA_API_SECRET = getpass("🔐 API Secret: ")
        
        if not Config.ZERODHA_API_KEY or not Config.ZERODHA_API_SECRET:
            print("❌ Credentials required!")
            return False
        
        print("✅ Credentials loaded (in memory only)")
        return True
    
    @staticmethod
    def clear_credentials():
        """Clear credentials from memory"""
        Config.ZERODHA_API_KEY = None
        Config.ZERODHA_API_SECRET = None
        Config.ZERODHA_ACCESS_TOKEN = None
        print("🔒 Credentials cleared from memory")