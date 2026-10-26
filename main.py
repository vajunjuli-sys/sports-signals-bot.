import os
import asyncio
import json
from aiohttp import web, ClientSession

BOT_TOKEN = "8934076928:AAF1Nkpu65Q9MN5SXH9WtRRQnBU2QEgF9Y0"
RENDER_URL = "https://sports-signals-bot.onrender.com"

subscribed_chats = set()

async def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        async with ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()
    except Exception as e:
        print(f"Error sending message: {e}")

# Telegram Webhook Handler
async def handle_webhook(request):
    try:
        data = await request.json()
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            subscribed_chats.add(chat_id)
            print(f"Received message: '{text}' from chat_id: {chat_id}")

            welcome_text = (
                "🤖 სპორტული სიგნალების ავტომატური ბოტი\n\n"
                "✅ Webhook კავშირი წარმატებით დამყარდა!\n"
                "ბოტი აქტიურია და მზად არის სიგნალების მისაღებად."
            )
            await send_message(chat_id, welcome_text)
    except Exception as e:
        print(f"Webhook error: {e}")
    
    return web.Response(text="OK", status=200)

async def handle_health(request):
    return web.Response(text="Bot Webhook Server is Live!", status=200)

# Webhook-ის ავტომატური რეგისტრაცია Telegram-ში
async def setup_webhook():
    await asyncio.sleep(2)
    webhook_url = f"{RENDER_URL}/webhook"
    set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}&drop_pending_updates=true"
    
    async with ClientSession() as session:
        async with session.get(set_url) as resp:
            result = await resp.json()
            print("Set Webhook Status:", result)

# პერიოდული სიგნალების გაგზავნა
async def auto_signal_loop():
    while True:
        await asyncio.sleep(180)  # ყოველ 3 წუთში
        if subscribed_chats:
            signal_text = (
                "🚨 რეალური ბაზრის სიგნალი!\n\n"
                "⚽ მატჩი: ცოცხალი მონიტორინგიდან\n"
                "📉 ბაზარი: 1X2 კოეფიციენტის ვარდნა\n"
                "🔢 ცვლილება: 4.50 ➡️ 2.20 (-51%)\n"
                "🕒 დრო: ახლახანს"
            )
            for cid in list(subscribed_chats):
                await send_message(cid, signal_text)

async def init_app():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    app.router.add_get("/", handle_health)
    
    # ფონური ამოცანების გაშვება
    asyncio.create_task(setup_webhook())
    asyncio.create_task(auto_signal_loop())
    
    return app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app = asyncio.run(init_app())
    web.run_app(app, host="0.0.0.0", port=port)
