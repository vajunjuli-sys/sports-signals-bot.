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

# Direct Telegram Updates Poller with detailed logs
def telegram_poller():
    print("=== TELEGRAM POLLER INITIALIZING ===")
    try:
        del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
        res = requests.get(del_url, timeout=10)
        print("Webhook clear response:", res.text)
    except Exception as e:
        print(f"Error clearing webhook: {e}")

    offset = 0
    print("Direct Telegram poller started successfully, waiting for messages...")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35)
            data = response.json()
            
            # ლოგებში გამოჩნდება რას აბრუნებს ტელეგრამი
            print("API Response:", data)
            
            if data.get("ok"):
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    message = result.get("message")
                    if message and "chat" in message:
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        
                        subscribed_chats.add(chat_id)
                        print(f">>> Received message from {chat_id}: {text}")
                        
                        welcome_text = (
                            "🤖 სპორტული სიგნალების ავტომატური ბოტი\n\n"
                            "✅ წარმატებით დაგიმახსოვრე!\n"
                            "ბოტი ფონურ რეჟიმში აკვირდება ბაზრებს და გამოგიგზავნის კოეფიციენტების ვარდნის სიგნალებს."
                        )
                        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        send_res = requests.post(send_url, json={"chat_id": chat_id, "text": welcome_text})
                        print(f"<<< Send message status: {send_res.status_code}, body: {send_res.text}")
        except Exception as e:
            print(f"!!! Poller error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Start HTTP server for Render port binding
    threading.Thread(target=run_http_server, daemon=True).start()
    
    # Start direct Telegram poller
    telegram_poller()
    
