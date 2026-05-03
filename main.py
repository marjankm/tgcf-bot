import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
SOURCE = -1001263412188
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
    text = event.message.text
    if not text:
        return
    blocked = [
        "t.me", "telegram.me", "http://", "https://", "@",
        "x.com", "follow us", "premium", "subscribe", "join",
        "pip net profit", "winning trades", "losing trades",
        "accuracy", "upgrade your trading", "trade smarter",
        "sm team", "sm co", "srosh", "best regards",
        "want the same results", "join today"
    ]
    for word in blocked:
        if word.lower() in text.lower():
            return
    await client.send_message(DEST, text)

with client:
    client.run_until_disconnected()
