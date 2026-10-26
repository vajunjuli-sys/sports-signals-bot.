import os
import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

BOT_TOKEN = "8934076928:AAF1Nkpu65Q9MN5SXH9WtRRQnBU2QEgF9Y0"
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
        # Render-ის პინგებისთვის
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

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
                print(f"Received message: {text} from {chat_id}")
                
                welcome_text = (
                    "🤖 სპორტული სიგნალების ავტომატური ბოტი\n\n"
                    "✅ კავშირი წარმატებით დამყარდა ვებჰუქით!\n"
                    "ბოტი მზად არის გამოგიგზავნოს სიგნალები."
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
    # Render-ის საჯარო ლინკი ვებჰუქისთვის
    render_url = f"https://sports-signals-bot.onrender.com/{BOT_TOKEN}"
    wh_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={render_url}"
    try:
        req = urllib.request.Request(wh_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            print("Webhook set result:", response.read().decode())
    except Exception as e:
        print(f"Error setting webhook: {e}")

if __name__ == "__main__":
    # ვამერთებთ ვებჰუქს ავტომატურად
    threading.Thread(target=set_webhook, daemon=True).start()
    # ვუშვებთ სერვერს
    run_server()
    
