import os
import json
import urllib.request
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8934076928:AAF1Nkpu65Q9MN5SXH9WtRRQnBU2QEgF9Y0"
RENDER_URL = "https://sports-signals-bot.onrender.com"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Send error: {e}")

# ავტომატურად აყენებს ვებჰუქს გაშვებისას
def auto_set_webhook():
    time.sleep(3)
    wh_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={RENDER_URL}"
    try:
        with urllib.request.urlopen(wh_url, timeout=10) as resp:
            print("Webhook auto-registered:", resp.read().decode())
    except Exception as e:
        print(f"Webhook registration error: {e}")

class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # UptimeRobot-ის პინგებისთვის
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sports Signals Bot is active!")

    def do_POST(self):
        # ტელეგრამიდან შემომავალი შეტყობინებების დამუშავება
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            if "message" in data:
                message = data["message"]
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
            print(f"Error processing update: {e}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass

def run():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"Server running on port {port}...")
    server.serve_forever()

if __name__ == "__main__":
    # ფონურ რეჟიმში ავტომატურად ვარეგისტრირებთ ვებჰუქს
    threading.Thread(target=auto_set_webhook, daemon=True).start()
    # ვუშვებთ მთავარ სერვერს
    run()
    
