import asyncio
import os
from telethon import TelegramClient, events
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
SOURCE = int(os.environ.get("SOURCE", "-1001263412188"))
DEST = int(os.environ.get("DEST", "-1003803840028"))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot running!")
    def log_message(self, *args):
        pass

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", 10000), Handler).serve_forever(), daemon=True).start()

client = TelegramClient("session", API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    await client.forward_messages(DEST, event.message)

with client:
    client.run_until_disconnected()
