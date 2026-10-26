import os
import json
import urllib.request
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8934076928:AAF1Nkpu65Q9MN5SXH9WtRRQnBU2QEgF9Y0"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Send error: {e}")

# 1. ფონური პოლერი (Telegram Polling) - მუშაობს გამავალი მოთხოვნებით, ვებჰუქების გარეშე
def start_telegram_poller():
    time.sleep(5)
    # ვასუფთავებთ ნებისმიერ ძველ ვებჰუქს, რომ getUpdates-მა თავისუფლად იმუშაოს
    try:
        del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
        urllib.request.urlopen(del_url, timeout=10)
        print("Webhook cleared successfully.")
    except Exception:
        pass

    offset = 0
    print("Background polling started...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=25"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("ok"):
                    for result in data.get("result", []):
                        offset = result["update_id"] + 1
                        message = result.get("message")
                        if message and "chat" in message:
                            chat_id = message["chat"]["id"]
                            text = message.get("text", "")
                            print(f"Received message: {text} from {chat_id}")
                            
                            if text.startswith("/start"):
                                reply_text = (
                                    "🤖 სპორტული სიგნალების ბოტი\n\n"
                                    "✅ კავშირი წარმატებით დამყარდა!\n"
                                    "ბოტი მზად არის დააკვირდეს ბაზრებს და გამოგიგზავნოს სიგნალები."
                                )
                                send_message(chat_id, reply_text)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(3)

# 2. HTTP სერვერი Render-ისა და UptimeRobot-ისთვის (ინარჩუნებს სერვერს გაღვიძებულს)
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot server is active!")
    def log_message(self, format, *args):
        pass

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Web server running on port {port}...")
    server.serve_forever()

if __name__ == "__main__":
    # ფონურ თრედში ვუშვებთ ტელეგრამის პოლერს
    threading.Thread(target=start_telegram_poller, daemon=True).start()
    # მთავარ თრედში ვუშვებთ ვებ სერვერს პორტის დასაჭერად
    run_web_server()
    
