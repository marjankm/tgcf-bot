import asyncio
import os
import aiohttp
import threading
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
SOURCE = [-1001263412188, -1001553432571, -1003552874886, -1002006131201, -1001685592361, -1001529423657]
DEST = -1003803840028
IST = timezone(timedelta(hours=5, minutes=30))

# Store recent messages to avoid duplicates
recent_messages = set()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot running!")
    def log_message(self, *args):
        pass

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", 10000), Handler).serve_forever(), daemon=True).start()

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

def is_duplicate(text):
    # Use first 100 characters as fingerprint
    fingerprint = text[:100].lower().strip()
    if fingerprint in recent_messages:
        return True
    recent_messages.add(fingerprint)
    # Keep only last 100 messages
    if len(recent_messages) > 100:
        recent_messages.pop()
    return False

def is_spanish(text):
    spanish_words = [
        "que", "con", "para", "por", "una", "los", "las",
        "del", "sus", "como", "pero", "más", "este", "esta",
        "también", "años", "sobre", "entre", "cuando", "donde",
        "únete", "ahora", "noticias", "análisis", "verdad"
    ]
    text_lower = text.lower()
    count = sum(1 for word in spanish_words if f" {word} " in f" {text_lower} ")
    return count >= 3

def clean_message(text):
    if not text:
        return ""

    blocked = [
        "t.me", "telegram.me",
        "@sroshmayi", "@srosh_support",
        "@sroshmayi_bot", "@marketfeed",
        "@marketnews_feed", "@geopolitics_prime",
        "follow us on x",
        "for even faster headlines",
        "follow us", "premium", "subscribe",
        "pip net profit", "winning trades", "losing trades",
        "upgrade your trading", "trade smarter",
        "sm team", "sm co",
        "best regards", "want the same results",
        "join today", "financialjuice",
        "walter bloomberg", "join our",
        "leave a comment",
        "for our spanish",
        "cryptochillzone",
        "hyperliquid",
        "top trending coins",
        "trading fees",
        "join discussion",
        "view chat",
        "20% off",
        "off on trading",
        "bricsnews",
        "bricsnewschat",
    ]

    for word in blocked:
        if word.lower() in text.lower():
            return None

    clean_lines = []
    for line in text.split("\n"):
        if "follow sm news" in line.lower():
            break
        if "sm news for" in line.lower():
            break
        if "company profit reports" in line.lower():
            break
        if "real-time company" in line.lower():
            break
        if "boost us" in line.lower():
            break
        if "chat |" in line.lower():
            break
        if "geopolitics" in line.lower():
            break
        if "x.com" in line.lower():
            continue
        if "https://" in line.lower():
            continue
        if "http://" in line.lower():
            continue
        if "updates from" in line.lower():
            break
        if "srosh" in line.lower():
            break
        if line.strip().startswith("@"):
            continue
        clean_lines.append(line)

    return "\n".join(clean_lines).strip()

@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    msg = event.message
    now = datetime.now(IST)
    footer = f"\n\n⏰ {now.strftime('%d %b %Y | %I:%M %p IST')}\n📢 [Zero Delay News](https://t.me/zerodelaynewslive)"

    # Handle photo messages
    if msg.photo:
        text = msg.raw_text or ""
        if is_spanish(text):
            return
        clean_text = clean_message(text) if text else ""
        if clean_text is None:
            return
        if clean_text and is_duplicate(clean_text):
            print("Duplicate photo message skipped!")
            return
        caption = f"{clean_text}{footer}" if clean_text else footer.strip()
        await client.send_file(
            DEST,
            msg.photo,
            caption=caption,
            parse_mode='md'
        )
        return

    # Handle text messages
    text = msg.raw_text
    if not text:
        return
    if is_spanish(text):
        return
    clean_text = clean_message(text)
    if clean_text is None:
        return
    if not clean_text:
        return

    # Check duplicate
    if is_duplicate(clean_text):
        print("Duplicate message skipped!")
        return

    final_text = f"{clean_text}{footer}"
    await client.send_message(
        DEST,
        final_text,
        link_preview=False,
        parse_mode='md'
    )

async def post_calendar():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nfs.faireconomy.media/ff_calendar_thisweek.json") as resp:
                events_data = await resp.json()

        now = datetime.now(IST)
        today = now.strftime("%Y-%m-%d")
        high, medium, low = [], [], []

        for event in events_data:
            event_date = event.get("date", "")[:10]
            if event_date != today:
                continue
            title = event.get("title", "")
            currency = event.get("country", "")
            impact = event.get("impact", "")
            time = event.get("date", "")
            try:
                event_time = datetime.fromisoformat(time)
                event_time_ist = event_time.astimezone(IST)
                time_str = event_time_ist.strftime("%I:%M %p")
            except:
                time_str = "All Day"
            line = f"• {time_str} | {currency} | {title}"
            if impact == "High":
                high.append(line)
            elif impact == "Medium":
                medium.append(line)
            else:
                low.append(line)

        message = f"📅 **ECONOMIC CALENDAR**\n**{now.strftime('%A, %d %B %Y')}**\n\n"
        if high:
            message += "🔴 **HIGH IMPACT:**\n" + "\n".join(high) + "\n\n"
        if medium:
            message += "🟡 **MEDIUM IMPACT:**\n" + "\n".join(medium) + "\n\n"
        if low:
            message += "🟢 **LOW IMPACT:**\n" + "\n".join(low) + "\n\n"
        if not high and not medium and not low:
            message += "_No major events today!_ 🟢\n\n"
        message += f"⏰ _{now.strftime('%I:%M %p IST')}_\n📢 [Zero Delay News](https://t.me/zerodelaynewslive)"

        sent_msg = await client.send_message(DEST, message, parse_mode='md', link_preview=False)
        await client.pin_message(DEST, sent_msg.id)
        print("Calendar posted and pinned!")

    except Exception as e:
        print(f"Calendar error: {e}")

async def schedule_calendar():
    # Post immediately for testing
    print("Posting calendar for test...")
    await post_calendar()

    while True:
        now = datetime.now(IST)
        # Schedule at 10:00 AM IST
        target = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if now >= target:
            target = target + timedelta(days=1)
        wait = (target - now).total_seconds()
        print(f"Next calendar post in {wait/3600:.1f} hours")
        await asyncio.sleep(wait)
        await post_calendar()

async def main():
    await client.start()
    print("Bot started!")
    await asyncio.gather(
        client.run_until_disconnected(),
        schedule_calendar()
    )

with client:
    client.loop.run_until_complete(main())
