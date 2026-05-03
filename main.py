import os
import threading
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
SOURCE = [-1001263412188, -1001553432571, -1003552874886]
DEST = -1003803840028

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot running!")
    def log_message(self, *args):
        pass

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", 10000), Handler).serve_forever(), daemon=True).start()

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    msg = event.message
    text = msg.text
    
    if not text:
        return
    
    blocked = [
        "t.me", "telegram.me", "@",
        "follow us on x",
        "for even faster headlines",
        "follow us", "premium", "subscribe",
        "pip net profit", "winning trades", "losing trades",
        "upgrade your trading", "trade smarter",
        "sm team", "sm co", "srosh",
        "best regards", "want the same results",
        "join today", "financialjuice",
        "walter bloomberg", "join our",
    ]
    
    for word in blocked:
        if word.lower() in text.lower():
            return
    
    clean_lines = []
    for line in text.split("\n"):
        if "x.com" in line.lower():
            continue
        if "https://" in line.lower():
            continue
        if "http://" in line.lower():
            continue
        if "updates from" in line.lower():
            break
        clean_lines.append(line)
    
    clean_text = "\n".join(clean_lines).strip()
    
    if not clean_text:
        return
    
    # Add timestamp and source
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist).strftime("%d %b %Y | %I:%M %p IST")
    final_text = f"{clean_text}\n\n📰 Reuters 0delaynews\n⏰ {now}\n📢 [Zero Delay News](https://t.me/zerodelaynewslive)"
    
    await client.send_message(DEST, final_text, link_preview=False, parse_mode='md')

with client:
    client.run_until_disconnected()
