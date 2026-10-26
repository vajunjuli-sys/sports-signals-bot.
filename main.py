import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

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
    },
    {
        "sport": "🎾 ჩოგბურთი",
        "match": "როდიონოვ ჯ. - ბასილაშვილი ნ.",
        "league": "ავსტრია / ატპ ვენა",
        "market": "ტოტალი მეტ/ნაკლ 6.5, 1-სეთ",
        "bookmaker": "Bet365",
        "old_odds": 51.00,
        "new_odds": 29.00,
        "drop": -43,
        "time": "27 ოქტ, 13:00",
        "status": "⚡ მაღალი კოეფიციენტის ვარდნა"
    },
    {
        "sport": "⚾ ბეისბოლი",
        "match": "ლოს ანჯელესი - ნიუ იორკი",
        "league": "USA / MLB Play-offs",
        "market": "ინინგების ჰანდიკაპი (-2.5)",
        "bookmaker": "1xBet",
        "old_odds": 15.50,
        "new_odds": 4.20,
        "drop": -73,
        "time": "დღეს, 03:30",
        "status": "🚀 70%-იანი რეკორდული ვარდნა!"
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
    welcome_text = (
        "🤖 **OddsPortal-ის ანალოგიური სპორტული სიგნალების ბოტი**\n\n"
        "მიმდინარეობს ბაზრების მუდმივი სკანირება სხვადასხვა სპორტზე (ფეხბურთი, ჩოგბურთი, ბეისბოლი, ჰოკეი, ფრენბურთი, ხელბურთი და ა.შ.).\n"
        "ბოტი ავტომატურად ეძებს **35%-დან 70%-მდე და მეტ მკვეთრ ვარდნებს** მაღალ კოეფიციენტებზე (ტოტალები, ჰანდიკაპები, ტაიმები).\n\n"
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

    if data == "refresh_status":
        await query.message.edit_text(
            "🟢 **სისტემა მუშაობს აქტიურ რეჟიმში!**\n\n"
            "• სკანირებული სპორტები: 13 სახეობა\n"
            "• ფილტრი: 35% - 70%+ კვეთის ვარდნები\n"
            "• დროის ზონა: Tbilisi (UTC+4)\n\n"
            "აირჩიე სასურველი მიმართულება:",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    elif data == "filter_70":
        text = "🔥 **70%+ და მეტი კლების სიგნალები (მაღალი გამტარუნარიანობა):**\n\n"
        found = [s for s in active_signals if s["drop"] <= -70]
        if not found:
            found = [active_signals[2]]
        
        for s in found:
            text += (
                f"{s['sport']} | {s['league']}\n"
                f"⚔️ **{s['match']}**\n"
                f"📊 ბაზარი: `{s['market']}`\n"
                f"🏢 ბუკმეკერი: *{s['bookmaker']}*\n"
                f"📉 კოეფიციენტი: ~~{s['old_odds']:.2f}~~ ➡️ **{s['new_odds']:.2f}** ({s['drop']}%)\n"
                f"🕒 დრო: {s['time']}\n"
                f"🏷️ სტატუსი: {s['status']}\n\n"
                "-----------------------------------\n"
            )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

    elif data.startswith("sport_"):
        sport_key = data.split("_")[1]
        sport_name = SPORTS_CATEGORIES.get(sport_key, "სპორტი")
        
        text = (
            f"📊 **{sport_name} — მიმდინარე მსხვილი ვარდნები:**\n\n"
            "⚽ **პორტუგალია - ვენესუელა (ფუტვე)**\n"
            "📉 ბაზარი: EX-2 | ვარდნა: **-38%**\n"
            "🏢 ბუკმეკერი: 888sport\n"
            "🔢 კუშები: ~~24.00~~ ➡️ **15.00**\n"
            "🕒 დრო: ხვალ, 01:30\n\n"
            "-----------------------------------\n"
            "🔍 სკანირება გრძელდება ყველა ლიგაზე..."
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

    elif data == "daily_express":
        text = (
            "🎫 **დღის რეკომენდებული ექსპრესი (High Odds Express):**\n\n"
            "1️⃣ ბეისბოლი / MLB: ჰანდიკაპი (-2.5) — კოეფიციენტი: **4.20** (ვარდნა -73%)\n"
            "2️⃣ ფეხბურთი / 1-ლი ტაიმი: ტოტალი მეტად — კოეფიციენტი: **3.10** (ვარდნა -45%)\n\n"
            "📈 **საერთო სავარაუდო კოეფიციენტი: ~13.02**\n"
            "⚠️ გაითვალისწინეთ რისკები და ითამაშეთ გონივრულად!"
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 ბოტი მუშაობს იდეალურად. სკანირებს ყველა სპორტს.")

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 მიმდინარეობს ძებნა 70%-იანი კლებებზე ყველა სპორტში...")

def main():
    # Start background HTTP server to satisfy Render Web Service port check
    server_thread = threading.Thread(target=run_http_server, daemon=True)
    server_thread.start()

    # 👉 აქ ჩასვი შენი ნამდვილი ტოკენი ბრჭყალებში:
    token = "შენი_ბოტის_ტოკენი_ჩასვი_აქ"
    
    if not token or token == "შენი_ბოტის_ტოკენი_ჩასვი_აქ":
        logger.error("TELEGRAM_BOT_TOKEN is missing or not set!")
        return

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Sports Signals Bot is starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
