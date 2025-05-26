import feedparser
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telegram
import os
import re
import json

# === ENV SETUP ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SHEET_JSON = os.getenv("GOOGLE_CRED_JSON")
SHEET_NAME = os.getenv("SHEET_NAME", "Snipe Data")
SHEET_TAB = os.getenv("SHEET_TAB", "AI Tools")

with open("google_creds.json", "w") as f:
    f.write(SHEET_JSON)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME)
worksheet = sheet.worksheet(SHEET_TAB)

# === FETCH PRODUCT HUNT FEED ===
feed = feedparser.parse("https://www.producthunt.com/feed")
added = 0
latest_clean_summary = ""
latest_title = ""
latest_link = ""

for entry in feed.entries:
    title = entry.title
    summary = entry.summary
    link = entry.link

    if "AI" not in title and "AI" not in summary:
        continue

    short_summary = summary[:500]
    clean_summary = re.sub('<[^<]+?>', '', short_summary).strip()
    clean_summary = re.sub(r'Discussion\s*\|\s*Link', '', clean_summary)
    clean_summary = re.sub(r'\n{2,}', '\n', clean_summary).strip()

    drop_name = title
    reason = clean_summary
    action = "Try it now."
    full_text = f"{drop_name}\n{reason}\n{action}\nLink: {link}"

    worksheet.append_row([
        title, "Product Hunt", link, reason, full_text
    ])
    
    latest_clean_summary = reason
    latest_title = title
    latest_link = link
    added += 1
    break  # only take first relevant drop daily

# === SEND TO TELEGRAM ===
if added > 0:
    message = f"🚀 *Today's AI Drop: {latest_title}*\n\n🧠 {latest_clean_summary}\n\n🔗 [Try it now]({latest_link})"
    bot = telegram.Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
    print("✅ Drop added and sent to Telegram.")
else:
    print("⚠️ No new AI drops found today.")
