import os
import json
import urllib.request
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8934076928:AAF1Nkpu65Q9MN5SXH9WtRRQnBU2QEgF9Y0"
subscribed_chats = set()

# Render-ისთვის პორტის მოსმენა (Health Check)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
        
    def log_message(self, format, *args):
        return  # ლოგების გასუფთავება

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"HTTP Server listening on port {port}...")
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

# Telegram Poller
def start_polling():
    # 1. გაუქმება Webhook-ის, რომ getUpdates-მა იმუშაოს
    try:
        del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
        with urllib.request.urlopen(del_url, timeout=10) as resp:
            print("Webhook deleted:", resp.read().decode())
    except Exception as e:
        print(f"Delete webhook error: {e}")

    offset = 0
    print("Bot polling started...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("ok"):
                    for result in data.get("result", []):
                        offset = result["update_id"] + 1
                        message = result.get("message")
                        if message and "chat" in message:
                            chat_id = message["chat"]["id"]
                            text = message.get("text", "")
                            subscribed_chats.add(chat_id)
                            
                            reply_text = (
                                "🤖 სპორტული სიგნალების ბოტი\n\n"
                                "✅ წარმატებით დაუკავშირდით ბოტს!\n"
                                "მონიტორინგი ჩართულია და სიგნალები ავტომატურად გამოგეგზავნებათ."
                            )
                            send_message(chat_id, reply_text)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(3)

# ავტომატური სიგნალების გაგზავნა
def auto_signal_scanner():
    while True:
        time.sleep(120)  # ყოველ 2 წუთში
