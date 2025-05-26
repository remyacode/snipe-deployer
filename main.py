import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telegram
import os
import json

# === ENV VARIABLES ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_JSON = os.getenv("GOOGLE_CRED_JSON")  # Passed as a string
SHEET_NAME = os.getenv("SHEET_NAME", "Snipe Data")
SHEET_TAB = os.getenv("SHEET_TAB", "AI Tools")
CHANNEL_ID = os.getenv("CHANNEL_ID")

with open("google_creds.json", "w") as f:
    f.write(SHEET_JSON)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME)
worksheet = sheet.worksheet(SHEET_TAB)

rows = worksheet.get_all_values()
latest = rows[-1]
title, source, link, reason, full_drop = latest

message = f"🚀 *Today's AI Drop: {title}*\n\n🧠 {reason}\n\n🔗 [Try it now]({link})"

bot = telegram.Bot(token=BOT_TOKEN)
bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

print("✅ Drop sent to Telegram.")
