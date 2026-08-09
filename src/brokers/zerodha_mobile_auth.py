from kiteconnect import KiteConnect
import json
import webbrowser
from datetime import datetime

class ZerodhaMobileAuth:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.kite = KiteConnect(api_key=api_key)
        self.access_token = None
    
    def login_via_mobile(self):
        """Login using mobile Kite app"""
        print("\n" + "="*60)
        print("📱 ZERODHA MOBILE LOGIN")
        print("="*60)
        
        # Step 1: Generate login URL
        login_url = self.kite.login_url()
        
        print("\n📋 OPTION 1: Direct Login Link")
        print("-"*40)
        print(f"Open this link on your phone:")
        print(f"\n{login_url}\n")
        
        print("\n📋 OPTION 2: QR Code Method")
        print("-"*40)
        print("1. Open Kite app on your phone")
        print("2. Go to Profile → API Connections")
        print("3. Tap 'Connect New App'")
        print("4. Scan QR code or enter API Key manually")
        print(f"\nYour API Key: {self.api_key}")
        
        print("\n" + "="*60)
        print("After logging in:")
        print("1. You'll be redirected to a page")
        print("2. Copy the ENTIRE URL from browser")
        print("3. Paste it below")
        print("="*60)
        
        # Get request token from URL
        full_url = input("\n📎 Paste the full redirect URL: ").strip()
        
        # Extract request_token from URL
        try:
            if 'request_token=' in full_url:
                request_token = full_url.split('request_token=')[1].split('&')[0]
                
                # Add # if needed
                if ' ' in request_token:
                    request_token = request_token.split(' ')[0]
                
                print(f"\n✅ Request token extracted: {request_token[:20]}...")
                
                # Generate session
                return self.generate_session(request_token)
            else:
                print("❌ Could not find request_token in URL")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def generate_session(self, request_token):
        """Generate access token"""
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            
            # Save session
            session_data = {
                'access_token': self.access_token,
                'api_key': self.api_key,
                'user_name': data['user_name'],
                'email': data['email'],
                'user_id': data['user_id'],
                'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open('zerodha_session.json', 'w') as f:
                json.dump(session_data, f, indent=2)
            
            print("\n" + "="*60)
            print("✅ LOGIN SUCCESSFUL!")
            print("="*60)
            print(f"Welcome, {data['user_name']}")
            print(f"Email: {data['email']}")
            print(f"User ID: {data['user_id']}")
            print(f"Access Token: {self.access_token[:20]}...")
            print("\n💾 Session saved to zerodha_session.json")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"❌ Session generation failed: {e}")
            return False
    
    def login_with_saved_session(self):
        """Login using previously saved session"""
        try:
            with open('zerodha_session.json', 'r') as f:
                data = json.load(f)
            
            self.access_token = data['access_token']
            self.kite.set_access_token(self.access_token)
            
            # Verify token is still valid
            try:
                profile = self.kite.profile()
                print(f"\n✅ Auto-login successful!")
                print(f"Welcome back, {profile['user_name']}")
                return True
            except:
                print("\n⚠️  Session expired. Please login again.")
                return False
                
        except FileNotFoundError:
            print("\n⚠️  No saved session found.")
            return False
    
    def show_qr_code(self):
        """Show QR code for mobile app connection"""
        print("\n📱 SCAN THIS QR CODE WITH KITE APP:")
        print("-"*40)
        
        # Generate QR code text
        qr_text = f"kite://connect?api_key={self.api_key}"
        
        try:
            # Try to generate QR code
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            # Print QR in terminal
            qr.print_ascii()
            
        except ImportError:
            print("Install qrcode: pip install qrcode[pil]")
            print(f"\nOr manually enter this API Key in Kite app:")
            print(f"API Key: {self.api_key}")
        
        print("-"*40)


# Simple test
if __name__ == "__main__":
    print("\n" + "="*60)
    print("📱 ZERODHA MOBILE CONNECTION")
    print("="*60)
    
    API_KEY = input("Enter your API Key: ").strip()
    API_SECRET = input("Enter your API Secret: ").strip()
    
    auth = ZerodhaMobileAuth(API_KEY, API_SECRET)
    
    # Try saved session first
    if not auth.login_with_saved_session():
        # New login via mobile
        print("\nChoose login method:")
        print("1. Open link in mobile browser")
        print("2. Use Kite mobile app")
        
        choice = input("Choice (1-2): ").strip()
        
        if choice == "1":
            auth.login_via_mobile()
        elif choice == "2":
            auth.show_qr_code()
            auth.login_via_mobile()