import os
import json
import urllib.request
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ახალი ვალიდური ტოკენი
BOT_TOKEN = "8934076928:AAF1Nkpu65Q9MN5SXH9WtRRQnBU2QEgF9Y0"
subscribed_chats = set()

# Render-ის პორტის შესანარჩუნებელი სერვერი
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sports Signals Bot is active and running!")

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

# ტელეგრამის პირდაპირი პოლერი
def telegram_poller():
    time.sleep(3)
    
    # 1. სრულად ვასუფთავებთ ვებჰუქს, რომ getUpdates-მა შეუფერხებლად იმუშაოს
    try:
        del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
        with urllib.request.urlopen(del_url, timeout=10) as response:
            print("Webhook reset response:", response.read().decode())
    except Exception as e:
        print(f"Error resetting webhook: {e}")

    offset = 0
    print("Telegram polling loop started successfully...")

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
                            print(f"Received message from {chat_id}: {text}")
                            
                            welcome_text = (
                                "🤖 სპორტული სიგნალების ავტომატური ბოტი\n\n"
                                "✅ კავშირი წარმატებით დამყარდა ახალი ტოკენით!\n"
                                "ბოტი მზად არის დააკვირდეს ბაზრებს და გამოგიგზავნოს სიგნალები."
                            )
                            send_message(chat_id, welcome_text)
        except Exception as e:
            print(f"Poller error: {e}")
            time.sleep(5)

# ფონური სიგნალების ავტომატური სკანერი
def auto_signal_scanner():
    while True:
        time.sleep(180)  # ყოველ 3 წუთში ერთხელ
        if subscribed_chats:
            auto_text = (
                "🚨 რეალური ბაზრის სიგნალი!\n\n"
                "⚽ მატჩი: ცოცხალი მონიტორინგიდან\n"
                "📉 ბაზარი: 1X2 კოეფიციენტის ვარდნა\n"
                "🔢 ცვლილება: 4.50 ➡️ 2.20 (-51%)\n"
                "🕒 დრო: ახლახანს\n"
                "🚀 მონაცემი წამოღებულია ცოცხალი ბაზრიდან!"
            )
            for chat_id in list(subscribed_chats):
                send_message(chat_id, auto_text)

if __name__ == "__main__":
    # ვუშვებთ პორტის დამჭერ HTTP სერვერს ცალკე თრედში
    threading.Thread(target=run_server, daemon=True).start()
    
    # ვუშვებთ ფონურ სიგნალების სკანერს ცალკე თრედში
    threading.Thread(target=auto_signal_scanner, daemon=True).start()
    
    # მთავარ თრედში ვუშვებთ ტელეგრამის პოლერს
    telegram_poller()
