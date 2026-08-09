"""
Quick script to connect your bot to Mobile Kite
Run this from your phone or computer
"""
from kiteconnect import KiteConnect
import json

def connect_mobile_kite():
    print("""
    ╔══════════════════════════════════════╗
    ║   📱 MOBILE KITE CONNECTION        ║
    ╠══════════════════════════════════════╣
    ║ Connect your trading bot to         ║
    ║ Zerodha Kite mobile app            ║
    ╚══════════════════════════════════════╝
    """)
    
    # Your API credentials
    API_KEY = input("🔑 Enter API Key: ").strip()
    API_SECRET = input("🔐 Enter API Secret: ").strip()
    
    kite = KiteConnect(api_key=API_KEY)
    
    print("\n" + "="*60)
    print("📱 STEPS TO CONNECT:")
    print("="*60)
    print("\n1️⃣  Open this link on your PHONE:")
    print(f"   {kite.login_url()}")
    
    print("\n2️⃣  Login to your Zerodha account")
    
    print("\n3️⃣  After login, you'll see a blank page")
    print("    Copy the ENTIRE URL from address bar")
    print("    It looks like: https://127.0.0.1/?request_token=xxx...")
    
    print("\n4️⃣  Paste that URL here")
    print("="*60)
    
    # Get the redirect URL
    redirect_url = input("\n📎 Paste redirect URL: ").strip()
    
    # Extract request token
    try:
        if 'request_token=' in redirect_url:
            request_token = redirect_url.split('request_token=')[1]
            if '&' in request_token:
                request_token = request_token.split('&')[0]
            
            # Clean token
            request_token = request_token.strip()
            
            print(f"\n✅ Token extracted: {request_token[:20]}...")
            
            # Generate session
            data = kite.generate_session(request_token, api_secret=API_SECRET)
            
            # Save session
            session = {
                'access_token': data['access_token'],
                'user_name': data['user_name'],
                'api_key': API_KEY
            }
            
            with open('kite_session.json', 'w') as f:
                json.dump(session, f)
            
            print("\n" + "="*60)
            print("✅ SUCCESSFULLY CONNECTED!")
            print("="*60)
            print(f"User: {data['user_name']}")
            print(f"Access Token: {data['access_token'][:30]}...")
            print(f"\n💾 Session saved to kite_session.json")
            print(f"\n🔗 Your bot can now trade using this session!")
            print("="*60)
            
            # Test connection
            kite.set_access_token(data['access_token'])
            profile = kite.profile()
            print(f"\n📊 Account Verified: {profile['user_name']}")
            print(f"Broker: {profile['broker']}")
            
            return data['access_token']
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you:")
        print("1. Copied the FULL URL")
        print("2. Used correct API Secret")
        print("3. Completed login on phone")
        return None

def test_session():
    """Test if saved session works"""
    try:
        with open('kite_session.json', 'r') as f:
            session = json.load(f)
        
        kite = KiteConnect(api_key=session['api_key'])
        kite.set_access_token(session['access_token'])
        
        # Test
        profile = kite.profile()
        print(f"\n✅ Session active!")
        print(f"User: {profile['user_name']}")
        
        # Get positions
        positions = kite.positions()
        print(f"\n📊 Current Positions:")
        for pos in positions['net']:
            print(f"  {pos['tradingsymbol']}: {pos['quantity']} @ ₹{pos['average_price']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Session expired: {e}")
        return False

if __name__ == "__main__":
    print("\n📱 ZERODHA MOBILE KITE CONNECTOR")
    print("="*60)
    print("1. Connect new session")
    print("2. Test existing session")
    
    choice = input("\nChoice (1-2): ").strip()
    
    if choice == "1":
        token = connect_mobile_kite()
        if token:
            print("\n✅ Ready to trade!")
    elif choice == "2":
        test_session()