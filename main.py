import os
import json
import urllib.request
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "8934076928:AAejdrV1HvQv6tmhlL_LXUIQQkYbfGck7uw"
subscribed_chats = set()

@app.route("/", methods=["GET"])
def health_check():
    return "Bot is alive and running!", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        subscribed_chats.add(chat_id)
        print(f"Received message from {chat_id}: {text}")
        
        welcome_text = (
            "🤖 სპორტული სიგნალების ავტომატური ბოტი\n\n"
            "✅ წარმატებით დაგიმახსოვრე!\n"
            "ბოტი ფონურ რეჟიმში აკვირდება ბაზრებს და გამოგიგზავნის კოეფიციენტების ვარდნის სიგნალებს."
        )
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": chat_id, "text": welcome_text}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            print(f"Error sending reply: {e}")
            
    return "OK", 200

def set_webhook():
    # შენი Render სერვისის საჯარო მისამართი
    render_url = f"https://sports-signals-bot.onrender.com/{BOT_TOKEN}"
    wh_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={render_url}"
    try:
        res = urllib.request.urlopen(wh_url, timeout=10)
        print("Webhook set response:", res.read().decode())
    except Exception as e:
        print(f"Error setting webhook: {e}")

if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
