import os
import json
import urllib.request
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8934076928:AAF1Nkpu65Q9MN5SXH9WtRRQnBU2QEgF9Y0"
subscribed_chats = set()

# Render-ის პორტის დამჭერი
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")
    def log_message(self, format, *args):
        pass

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"HTTP server started on port {port}")
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

# Telegram Poller
def poll_telegram():
    time.sleep(2)
    # ვასუფთავებთ ძველ ვებჰუქს
    try:
        del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
        urllib.request.urlopen(del_url, timeout=10)
    except Exception:
        pass

    offset = 0
    print("Telegram polling started...")
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
                            send_message(chat_id, "🤖 ბოტი წარმატებით დაკავშირდა და მზად არის!")
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    # ვუშვებთ ტელეგრამის პოლერს ფონურ თრედში
    threading.Thread(target=poll_telegram, daemon=True).start()
    
    # მთავარ თრედში ვუშვებთ ვებ სერვერს, რომ Render-მა პორტი დაინახოს და არ გათიშოს
    run_web_server()
    
