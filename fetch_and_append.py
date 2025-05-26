import feedparser
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import os
import json

# === Load Google Sheet creds from env
with open("google_creds.json", "w") as f:
    f.write(os.getenv("GOOGLE_CRED_JSON"))

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(os.getenv("SHEET_NAME", "Snipe Data"))
worksheet = sheet.worksheet(os.getenv("SHEET_TAB", "AI Tools"))

# === Fetch Product Hunt RSS
feed = feedparser.parse("https://www.producthunt.com/feed")
added = 0

for entry in feed.entries:
    title = entry.title
    summary = entry.summary
    link = entry.link

    if "AI" not in title and "AI" not in summary:
        continue

    # Clean summary
    short_summary = summary[:500]
    clean_summary = re.sub('<[^<]+?>', '', short_summary).strip()
    clean_summary = re.sub(r'Discussion\s*\|\s*Link', '', clean_summary)
    clean_summary = re.sub(r'\n{2,}', '\n', clean_summary).strip()

    drop_name = title
    reason = clean_summary
    action = "Try it now."
    full_text = f"{drop_name}\n{reason}\n{action}\nLink: {link}"

    worksheet.append_row([
        title,
        "Product Hunt",
        link,
        reason,
        full_text
    ])

    print(f"✅ Added: {title}")
    added += 1

print(f"\n🚀 {added} drops added.")
