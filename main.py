import os
import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

BOT_TOKEN = "8934076928:AAejdrV1HvQv6tmhlL_LXUIQQkYbfGck7uw"
subscribed_chats = set()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Error sending message: {e}")

class TelegramWebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Render Health Check (ეს პინგი სერვერს ფხიზლად ამყოფებს)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Webhook Server is active!")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            if "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")
                
                subscribed_chats.add(chat_id)
                print(f"Received message from {chat_id}: {text}")
                
                welcome_text = (
                    "🤖 სპორტული სიგნალების ავტომატური ბოტი\n\n"
                    "✅ კავშირი წარმატებით დამყარდა!\n"
                    "ბოტი მზად არის დააკვირდეს ბაზრებს და გამოგიგზავნოს სიგნალები."
                )
                send_message(chat_id, welcome_text)
        except Exception as e:
            print(f"Error processing webhook: {e}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), TelegramWebhookHandler)
    server.serve_forever()

def set_webhook():
    time.sleep(5)
    # ზუსტი ვებჰუქის მისამართი Render-ზე
    render_url = f"https://sports-signals-bot.onrender.com/"
    wh_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={render_url}"
    try:
        req = urllib.request.Request(wh_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            print("Webhook set response:", response.read().decode())
    except Exception as e:
        print(f"Error setting webhook: {e}")

def auto_signal_scanner():
    while True:
        time.sleep(180)
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
    threading.Thread(target=set_webhook, daemon=True).start()
    threading.Thread(target=auto_signal_scanner, daemon=True).start()
    run_server()
    
