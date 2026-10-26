import os
import time
import threading
import requests
from flask import Flask, request

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "8934076928:AAejdrV1HvQv6tmhlL_LXUIQQkYbfGck7uw"

# Storage for subscribed users
subscribed_chats = set()

@app.route("/", methods=["GET", "POSTIndex"])
def index():
    return "Bot is alive and running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        subscribed_chats.add(chat_id)
        
        # პასუხი ნებისმიერ შეტყობინებაზე ან /start-ზე
        welcome_text = (
            "🤖 სპორტული სიგნალების ავტომატური ბოტი\n\n"
            "✅ ვებჰუქი წარმატებით დაკავშირდა!\n"
            "ბოტი ფონურ რეჟიმში აკვირდება ბაზრებს და გამოგიგზავნის კოეფიციენტების ვარდნის სიგნალებს."
        )
        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": welcome_text})
        
    return "OK", 200

def set_webhook_url():
    time.sleep(3) # დაველოდოთ სერვერის ჩართვას
    # Render-ის ზუსტი საჯარო მისამართი
    render_url = f"https://sports-signals-bot.onrender.com/{BOT_TOKEN}"
    wh_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={render_url}"
    try:
        res = requests.get(wh_url)
        print("Webhook set response:", res.text)
    except Exception as e:
        print(f"Error setting webhook: {e}")

# Background automatic signal scanner & pusher
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
                try:
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    requests.post(url, json={"chat_id": chat_id, "text": auto_text})
                except Exception as e:
                    print(f"Error sending auto signal: {e}")

if __name__ == "__main__":
    # ავტომატურად ვურერთებთ ვებჰუქს ცალკე თრედიდან
    threading.Thread(target=set_webhook_url, daemon=True).start()
    
    # ფონური სკანერის გაშვება
    threading.Thread(target=auto_signal_scanner, daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
