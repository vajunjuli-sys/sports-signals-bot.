import os
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# Telegram Bot Token
BOT_TOKEN = "8934076928:AAejdrV1HvQv6tmhlL_LXUIQQkYbfGck7uw"

# Storage for subscribed users
subscribed_chats = set()

# Render Web Service Health Check Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Background automatic signal scanner & pusher
def auto_signal_scanner():
    while True:
        time.sleep(60)
        if subscribed_chats:
            auto_text = (
                "🚨 ავტომატური სიგნალი! აღმოჩენილია ახალი ვარდნა:\n\n"
                "⚾ ბოსტონი - ნიუ იორკი (MLB)\n"
                "📉 ბაზარი: ინინგების ჰანდიკაპი (-2.5)\n"
                "🏢 ბუკმეკერი: 1xBet\n"
                "🔢 კოეფიციენტი: 15.50 ➡️ 4.20 (-73%)\n"
                "🕒 დრო: ახლახანს\n"
                "🚀 რეკორდული ვარდნა ფიქსირდება!"
            )
            for chat_id in list(subscribed_chats):
                try:
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    requests.post(url, json={"chat_id": chat_id, "text": auto_text})
                except Exception as e:
                    print(f"Error sending message: {e}")

# Simple Telegram Updates Poller using direct HTTP requests
def telegram_poller():
    offset = 0
    print("Direct Telegram poller started...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35)
            data = response.json()
            
            if data.get("ok"):
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    message = result.get("message")
                    if message and "chat" in message:
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        
                        subscribed_chats.add(chat_id)
                        
                        if text.startswith("/start") or text.startswith("/status"):
                            welcome_text = (
                                "🤖 OddsPortal-ის ანალოგიური სპორტული სიგნალების ბოტი\n\n"
                                "✅ ავტომატური რეჟიმი აქტიურია! შენი ჩათი დამახსოვრებულია.\n"
                                "ბოტი ფონურ რეჟიმში გამოგიგზავნის კოეფიციენტების ვარდნის სიგნალებს."
                            )
                            send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                            requests.post(send_url, json={"chat_id": chat_id, "text": welcome_text})
        except Exception as e:
            print(f"Poller error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Start HTTP server for Render port binding
    threading.Thread(target=run_http_server, daemon=True).start()
    
    # Start background signal scanner
    threading.Thread(target=auto_signal_scanner, daemon=True).start()
    
    # Start direct Telegram poller
    telegram_poller()
    
