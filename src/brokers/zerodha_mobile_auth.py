from kiteconnect import KiteConnect
from getpass import getpass
import pandas as pd
from datetime import datetime

class ZerodhaBroker:
    def __init__(self):
        """Initialize without credentials"""
        self.api_key = None
        self.api_secret = None
        self.access_token = None
        self.kite = None
        
    def interactive_login(self):
        """Complete interactive login - NOTHING saved"""
        print("\n" + "="*60)
        print("🔐 INTERACTIVE ZERODHA LOGIN")
        print("="*60)
        
        # Step 1: Get API credentials
        print("\n📝 Step 1: Enter API Credentials")
        self.api_key = getpass("🔑 API Key: ")
        self.api_secret = getpass("🔐 API Secret: ")
        
        if not self.api_key or not self.api_secret:
            print("❌ Credentials required!")
            return False
        
        # Step 2: Generate login URL
        self.kite = KiteConnect(api_key=self.api_key)
        login_url = self.kite.login_url()
        
        print("\n📱 Step 2: Login via Mobile")
        print("-"*40)
        print(f"Open this link on your phone:")
        print(f"\n{login_url}\n")
        print("After login, copy the ENTIRE URL from browser")
        print("-"*40)
        
        # Step 3: Get request token
        redirect_url = input("\n📎 Paste redirect URL: ").strip()
        
        try:
            request_token = redirect_url.split('request_token=')[1]
            if '&' in request_token:
                request_token = request_token.split('&')[0]
        except:
            print("❌ Invalid URL! Could not find request token")
            return False
        
        # Step 4: Generate session
        try:
            print("\n🔄 Generating session...")
            session = self.kite.generate_session(
                request_token, 
                api_secret=self.api_secret
            )
            
            self.access_token = session['access_token']
            self.kite.set_access_token(self.access_token)
            
            print("\n" + "="*60)
            print("✅ LOGIN SUCCESSFUL!")
            print("="*60)
            print(f"👤 User: {session['user_name']}")
            print(f"📧 Email: {session['email']}")
            print(f"🏢 Broker: {session['broker']}")
            print(f"🆔 User ID: {session['user_id']}")
            print("="*60)
            
            # Show account balance
            self.show_balance()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Login failed: {e}")
            return False
    
    def show_balance(self):
        """Display account balance"""
        try:
            margins = self.kite.margins()
            equity = margins['equity']
            
            print("\n💰 ACCOUNT BALANCE:")
            print(f"   Available: ₹{equity['available']['live_balance']:,.2f}")
            print(f"   Used Margin: ₹{equity['utilised']['debits']:,.2f}")
            print(f"   Opening Balance: ₹{equity['available']['opening_balance']:,.2f}")
            
        except Exception as e:
            print(f"❌ Could not fetch balance: {e}")
    
    def place_order(self, symbol, quantity, transaction_type, product="CNC"):
        """Place order - requires active login"""
        if not self.kite or not self.access_token:
            print("❌ Login first!")
            return None
        
        try:
            # Confirm order
            print(f"\n📋 ORDER CONFIRMATION:")
            print(f"   Symbol: {symbol}")
            print(f"   Action: {transaction_type}")
            print(f"   Quantity: {quantity}")
            print(f"   Product: {product}")
            
            # Get current price
            ltp = self.kite.ltp(f"NSE:{symbol}")
            price = ltp[f"NSE:{symbol}"]['last_price']
            value = price * quantity
            print(f"   Current Price: ₹{price:,.2f}")
            print(f"   Total Value: ₹{value:,.2f}")
            
            # Confirm
            confirm = input("\n⚠️  Confirm order? (yes/no): ").strip().lower()
            
            if confirm != 'yes':
                print("❌ Order cancelled")
                return None
            
            # Place order
            order_id = self.kite.place_order(
                variety="regular",
                exchange="NSE",
                tradingsymbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                product=product,
                order_type="MARKET"
            )
            
            print(f"\n✅ ORDER PLACED!")
            print(f"   Order ID: {order_id}")
            print(f"   {transaction_type} {quantity} {symbol} @ ₹{price:,.2f}")
            
            return order_id
            
        except Exception as e:
            print(f"❌ Order failed: {e}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        try:
            positions = self.kite.positions()
            
            print("\n📊 CURRENT POSITIONS:")
            if positions['net']:
                total_pnl = 0
                for pos in positions['net']:
                    pnl = pos['pnl']
                    total_pnl += pnl
                    emoji = "🟢" if pnl >= 0 else "🔴"
                    print(f"   {emoji} {pos['tradingsymbol']}: {pos['quantity']} shares")
                    print(f"      Avg: ₹{pos['average_price']:,.2f} | P&L: ₹{pnl:,.2f}")
                
                print(f"\n   💰 Total P&L: ₹{total_pnl:,.2f}")
            else:
                print("   No open positions")
            
            return positions
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def logout(self):
        """Clear session and credentials"""
        self.api_key = None
        self.api_secret = None
        self.access_token = None
        self.kite = None
        print("\n🔒 Logged out successfully")
        print("   All credentials cleared from memory")