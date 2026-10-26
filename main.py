import os
import json
import urllib.request
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8934076928:AAejdrV1HvQv6tmhlL_LXUIQQkYbfGck7uw"
subscribed_chats = set()

# HTTP სერვერი Render-ის პორტის შესანარჩუნებლად (Health Check)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Error sending message: {e}")

# ტელეგრამის პოლერი (ამოღებს ვებჰუქს და იწყებს შეტყობინებების კითხვას)
def telegram_poller():
    time.sleep(5)  # დაველოდოთ სერვერის სრულ ამუშავებას
    
    # 1. სრულად გავასუფთავოთ ვებჰუქი, რომ getUpdates მუშაობდეს
    try:
        del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
        with urllib.request.urlopen(del_url, timeout=10) as response:
            print("Webhook cleared:", response.read().decode())
    except Exception as e:
        print(f"Error clearing webhook: {e}")

    offset = 0
    print("Polling loop started...")

    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if data.get("ok"):
                    for result in data.get("result", []):
                        offset = result["update_id"] + 1
                        message = result.get("message")
                        if message and "chat" in message:
                            chat_id = message["chat"]["id"]
                            text = message.get("text", "")
                            
                            subscribed_chats.add(chat_id)
                            print(f"Received from {chat_id}: {text}")
                            
                            welcome_text = (
                                "🤖 სპორტული სიგნალების ავტომატური ბოტი\n\n"
                                "✅ წარმატებით გადმოვიდა Polling რეჟიმზე და დაგიმახსოვრა!\n"
                                "ბოტი ფონურ რეჟიმში აკვირდება ბაზრებს და გამოგიგზავნის კოეფიციენტების ვარდნის სიგნალებს."
                            )
                            send_message(chat_id, welcome_text)
        except Exception as e:
            print(f"Poller error: {e}")
            time.sleep(5)

# ფონური სიგნალების სკანერი
def auto_signal
