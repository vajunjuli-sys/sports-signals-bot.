import os
import json
import urllib.request
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8934076928:AAF1Nkpu65Q9MN5SXH9WtRRQnBU2QEgF9Y0"
subscribed_chats = set()

# Render-ის პორტის შესანარჩუნებელი სერვერი
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")
    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Send error: {e}")

# Telegram Poller - მუშაობს ყოველგვარი ვებჰუქის გარეშე
def start_poller():
    time.sleep(3)
    # სრულად ვასუფთავებთ ნებისმიერ ძველ ვებჰუქს
    try:
        del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
        urllib.request.urlopen(del_url, timeout=10)
    except Exception:
        pass

    offset = 0
    print("Polling started successfully...")
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
                            subscribed_chats.add(chat_id)
                            
                            reply_text = (
                                "🤖 სპორტული სიგნალების ბოტი\n\n"
                                "✅ წარმატებით დაუკავშირდი ბოტს!\n"
                                "მონიტორინგი აქტიურია."
                            )
                            send_message(chat_id, reply_text)
        except Exception as e:
            print(f"Poller error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    # ვუშვებთ პოლერს ფონურ თრედში
    threading.Thread(target=start_poller, daemon=True).start()
    # მთავარ თრედში ვუშვებთ პორტის დამჭერ სერვერს
    run_server()
    
