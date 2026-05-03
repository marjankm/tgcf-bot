@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    text = event.message.text
    if not text:
        return
    
    # Block links and usernames
    blocked_links = [
        "t.me", "telegram.me", "http://", "https://", "@",
        "x.com", "twitter.com"
    ]
    
    # Block promotional keywords
    blocked_words = [
        "follow us", "premium", "subscribe", "join",
        "pip net profit", "winning trades", "losing trades",
        "accuracy", "upgrade your trading", "trade smarter",
        "sm team", "sm co", "srosh", "signals chat",
        "economic news", "analytics channel", "discussion group",
        "best regards", "want the same results",
        "while many traders", "join today"
    ]
    
    text_lower = text.lower()
    
    for word in blocked_links + blocked_words:
        if word.lower() in text_lower:
            return
    
    await client.send_message(DEST, text)
