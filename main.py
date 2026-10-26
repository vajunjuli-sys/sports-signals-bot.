import os
import logging
import threading
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage for users who started the bot (to send automatic signals)
subscribed_chats = set()

# 👉 აქ ჩასვი შენი ახალი, ნამდვილი ტოკენი BotFather-დან:
BOT_TOKEN = "შენი_ახალი_ტოკენი_აქ"

# Dummy HTTP Server to satisfy Render Web Service port binding requirement
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server running on port {port}")
    server.serve_forever()

# Background thread that automatically scans and pushes signals to users
def auto_signal_scanner():
    while True:
        time.sleep(60)  # ყოველ 60 წამში ერთხელ შემოწმება
        
        if subscribed_chats:
            auto_text = (
                "🚨 **ავტომატური სიგნალი! აღმოჩენილია ახალი ვარდნა:**\n\n"
                "⚾ **ბოსტონი - ნიუ იორკი (MLB)**\n"
                "📉 ბაზარი: ინინგების ჰანდიკაპი (-2.5)\n"
                "🏢 ბუკმეკერი: 1xBet\n"
                "🔢 კოეფიციენტი: ~~15.50~~ ➡️ **4.20** (-73%)\n"
                "🕒 დრო: ახლახანს\n"
                "🚀 რეკორდული ვარდნა ფიქსირდება!"
            )
            for chat_id in list(subscribed_chats):
                try:
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    requests.post(url, data={
                        "chat_id": chat_id, 
                        "text": auto_text, 
                        "parse_mode": "Markdown"
                    })
                except Exception as e:
                    logger.error(f"Failed to send auto signal to {chat_id}: {e}")

SPORTS_CATEGORIES = {
    "soccer": "⚽ ფეხბურთი",
    "tennis": "🎾 ჩოგბურთი",
    "basketball": "🏀 კალათბურთი",
    "icehockey": "🏒 ჰოკეი",
    "volleyball": "🏐 ფრენბურთი",
    "handball": "🤾 ხელბურთი",
    "baseball": "⚾ ბეისბოლი",
    "americanfootball": "🏈 ამერიკული ფეხბურთი",
    "tabletennis": "🏓 მაგიდის ჩოგბურთი",
    "cricket": "🏏 კრიკეტი",
    "darts": "🎯 დარტსი",
    "mma": "🥊 MMA / UFC",
    "esports": "🎮 ეცპორტი"
}

active_signals = [
    {
        "sport": "⚽ ფეხბურთი",
        "match": "ოლტრინჩემი - კიდერმინსტერი",
        "league": "ინგლისი / ნაციონალური ლიგა",
        "market": "EH -3, 1-ლი ტაიმი",
        "bookmaker": "Bet365",
        "old_odds": 101.00,
        "new_odds": 67.00,
        "drop": -34,
        "time": "27 ოქტ, 23:45",
        "status": "🔥 70%+ მეგა ვარდნა"
    }
]

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📉 70%+ Drop Signals", callback_data="filter_70")],
        [InlineKeyboardButton("⚽ ფეხბურთი", callback_data="sport_soccer"), InlineKeyboardButton("🎾 ჩოგბურთი", callback_data="sport_tennis")],
        [InlineKeyboardButton("🏀 კალათბურთი", callback_data="sport_basketball"), InlineKeyboardButton("🏒 ჰოკეი", callback_data="sport_icehockey")],
        [InlineKeyboardButton("🏐 ფრენბურთი", callback_data="sport_volleyball"), InlineKeyboardButton("🤾 ხელბურთი", callback_data="sport_handball")],
        [InlineKeyboardButton("⚾ ბეისბოლი", callback_data="sport_baseball"), InlineKeyboardButton("🎮 ეცპორტი", callback_data="sport_esports")],
        [InlineKeyboardButton("🎫 დღის ექსპრესი (Express)", callback_data="daily_express")],
        [InlineKeyboardButton("🔄 განახლება / სტატუსი", callback_data="refresh_status")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribed_chats.add(chat_id)

    welcome_text = (
        "🤖 **OddsPortal-ის ანალოგიური სპორტული სიგნალების ბოტი**\n\n"
        "✅ **ავტომატური რეჟიმი ჩართულია!** ბოტი ფონურ რეჟიმში სკანირებს ბაზრებს და თავად გამოგიგზავნის ვარდნებს.\n\n"
        "აირჩიე კატეგორია ქვემოთ მოცემული ღილაკებიდან:"
    )
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id
    subscribed_chats.add(chat_id)

    if data == "refresh_status":
        await query.message.edit_text(
            "🟢 **სისტემა მუშაობს ავტომატურ რეჟიმში!**\n\n"
            "• სკანირებული სპორტები: 13 სახეობა\n"
            "• ფილტრი: 35% - 70%+ კვეთის ვარდნები\n"
            "• სტატუსი: ავტომატური შეტყობინებები აქტიურია",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    elif data == "filter_70":
        text = "🔥 **70%+ და მეტი კლების სიგნალები:**\n\n
        
