import asyncio
import os
import aiohttp
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
DEST = -1003803840028
IST = timezone(timedelta(hours=5, minutes=30))

async def post_calendar(client):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nfs.faireconomy.media/ff_calendar_thisweek.json") as resp:
                events = await resp.json()

        now = datetime.now(IST)
        today = now.strftime("%Y-%m-%d")
        high, medium, low = [], [], []

        for event in events:
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
            line = f"⏰ {time_str} - {currency} - {title}"
            if impact == "High":
                high.append(line)
            elif impact == "Medium":
                medium.append(line)
            else:
                low.append(line)

        message = f"📅 ECONOMIC CALENDAR\n{now.strftime('%A, %d %B %Y')}\n\n"
        if high:
            message += "🔴 HIGH IMPACT:\n" + "\n".join(high) + "\n\n"
        if medium:
            message += "🟡 MEDIUM IMPACT:\n" + "\n".join(medium) + "\n\n"
        if low:
            message += "🟢 LOW IMPACT:\n" + "\n".join(low) + "\n\n"
        if not high and not medium and not low:
            message += "No major events today! 🟢\n\n"
        message += f"⏰ {now.strftime('%I:%M %p IST')}\n📢 [Zero Delay News](https://t.me/zerodelaynewslive)"

        await client.send_message(DEST, message, parse_mode='md', link_preview=False)

    except Exception as e:
        print(f"Calendar error: {e}")
