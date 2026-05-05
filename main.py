import os
import asyncio
import aiohttp
import threading
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
SOURCE = [-1001263412188, -1001553432571, -1003552874886]
DEST = -1003803840028
IST = timezone(timedelta(hours=5, minutes=30))

# --- HEALTH CHECK SERVER (For Render/Railway) ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"News + Calendar Bot Running!")
    def log_message(self, *args):
        pass

def run_health_server():
    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# --- NEWS FORWARDING LOGIC ---
def is_spanish(text):
    spanish_words = ["que", "con", "para", "por", "una", "los", "las", "del", "sus", "como"]
    text_lower = text.lower()
    count = sum(1 for word in spanish_words if f" {word} " in f" {text_lower} ")
    return count >= 3

async def news_handler(event):
    msg = event.message
    text = msg.raw_text
    if not text or is_spanish(text):
        return

    blocked = ["t.me", "telegram.me", "@srosh", "premium", "subscribe", "pip net", "winning trades"]
    if any(word.lower() in text.lower() for word in blocked):
        return

    clean_lines = []
    for line in text.split("\n"):
        if any(x in line.lower() for x in ["x.com", "http", "follow sm", "boost us", "srosh"]):
            continue
        clean_lines.append(line)

    clean_text = "\n".join(clean_lines).strip()
    if not clean_text:
        return

    now = datetime.now(IST).strftime("%d %b %Y | %I:%M %p IST")
    final_text = f"{clean_text}\n\n⏰ {now}\n📢 [Zero Delay News](https://t.me/zerodelaynewslive)"
    await event.client.send_message(DEST, final_text, link_preview=False, parse_mode='md')

# --- ECONOMIC CALENDAR LOGIC ---
async def post_calendar(client):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nfs.faireconomy.media/ff_calendar_thisweek.json") as resp:
                events_list = await resp.json()

        now = datetime.now(IST)
        today = now.strftime("%Y-%m-%d")
        high, medium, low = [], [], []

        for event in events_list:
            if event.get("date", "")[:10] != today:
                continue
            title, currency, impact = event.get("title"), event.get("country"), event.get("impact")
            try:
                e_time = datetime.fromisoformat(event.get("date")).astimezone(IST).strftime("%I:%M %p")
            except:
                e_time = "All Day"
            
            line = f"• {e_time} | {currency} | {title}"
            if impact == "High": high.append(line)
            elif impact == "Medium": medium.append(line)
            else: low.append(line)

        message = f"📅 **ECONOMIC CALENDAR**\n**{now.strftime('%A, %d %B %Y')}**\n\n"
        if high: message += "🔴 **HIGH IMPACT:**\n" + "\n".join(high) + "\n\n"
        if medium: message += "🟡 **MEDIUM IMPACT:**\n" + "\n".join(medium) + "\n\n"
        if not high and not medium and not low: message += "_No major events today!_ 🟢\n\n"
        message += f"⏰ _{now.strftime('%I:%M %p IST')}_\n📢 [Zero Delay News](https://t.me/zerodelaynewslive)"

        sent_msg = await client.send_message(DEST, message, parse_mode='md', link_preview=False)
        await client.pin_message(DEST, sent_msg.id)
    except Exception as e:
        print(f"Calendar error: {e}")

async def calendar_scheduler(client):
    # Initial test post on startup
    await post_calendar(client)
    
    while True:
        now = datetime.now(IST)
        target = now.replace(hour=7, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        
        wait_seconds = (target - now).total_seconds()
        print(f"Calendar scheduler: waiting {wait_seconds/3600:.1f} hours.")
        await asyncio.sleep(wait_seconds)
        await post_calendar(client)

# --- START THE BOT ---
async def start_bot():
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
    
    # Register news handler
    client.add_event_handler(news_handler, events.NewMessage(chats=SOURCE))
    
    await client.start()
    print("Bot started: News Forwarder active and Calendar scheduled.")
    
    # Run calendar scheduler as a background task
    asyncio.create_task(calendar_scheduler(client))
    
    # Keep the client running for news forwarding
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start_bot())
