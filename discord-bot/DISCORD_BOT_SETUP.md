# Discord Bot Setup Guide

## Step 1: Create Discord Bot

1. Go to: https://discord.com/developers/applications
2. Click "New Application" → Name it "C.A.T.S. Championship"
3. Go to "Bot" section → Click "Add Bot"
4. Under TOKEN, click "Copy" → **Save this somewhere safe**
5. Go to "Intents" → Turn ON: **Message Content Intent**
6. Go to "OAuth2" → URL Generator
   - Scopes: `bot`
   - Permissions: 
     - `Send Messages`
     - `Embed Links`
     - `Read Message History`
7. Copy the generated URL and open it → Select your Discord server → Authorize

---

## Step 2: Update Bot Token

Open `discord_countdown_bot.py` and replace line 16:

```python
TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
```

With your actual token:

```python
TOKEN = "MzA1NTQ3OTIwMzQ3NDA..."  # Your actual token
```

---

## Step 3: Deploy to Replit (Free, Always Running)

### Option A: Deploy to Replit (Easiest - Recommended)

1. Go to: https://replit.com (create free account)
2. Click "Create" → Select "Python"
3. Copy the bot code from `discord_countdown_bot.py`
4. Paste it into Replit
5. Create `requirements.txt`:
```
discord.py
```
6. Click "Run" → Bot runs 24/7!

### Option B: Run Locally

1. Install discord.py:
```powershell
pip install discord.py
```

2. Run:
```powershell
cd "C:\Users\lucam\OneDrive\Bureaublad\mappen\Scripts\blue stacks"
python discord_countdown_bot.py
```

---

## Step 4: Use the Bot in Discord

In your Discord server, use these commands:

**Start countdown:**
```
!set_end_time "03/07/2026 22:00"
```

**Check status:**
```
!countdown_status
```

---

## Workflow:

1. **Run your OCR script** to get the timer:
```powershell
python "C.A.T.S. Championship Timer NotifierV3.py"
```

2. **Copy the end time** from the output (e.g., `03/07/2026 22:00`)

3. **Go to Discord** and type:
```
!set_end_time "03/07/2026 22:00"
```

4. **Bot takes over:**
   - Updates countdown every minute
   - Sends alerts at 60 and 15 minutes
   - Runs 24/7 on Replit (or your PC)

---

## Troubleshooting

**Bot not responding?**
- Check token is correct
- Make sure bot has permission to send messages
- Restart the bot

**No countdown message?**
- Use `!set_end_time` command first
- Make sure bot can see the channel

**Alerts not sending?**
- Wait for 60 or 15 minutes before end time
- Use `!countdown_status` to check remaining time

---

## Notes

- **Replit version:** Bot runs 24/7, never stops (best for always-on countdown)
- **Local version:** Bot runs on your PC only while script is active
- **State saved:** Bot remembers message ID and settings in `bot_settings.json`

**Recommended:** Deploy to Replit for true always-on operation! 🚀
