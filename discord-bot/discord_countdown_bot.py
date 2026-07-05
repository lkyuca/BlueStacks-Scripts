"""
C.A.T.S. Championship Countdown Discord Bot
Runs on Replit or any server, updates countdown live
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import os

# Bot configuration
TOKEN = "Your own bot token"  # Get this from Discord Developer Portal
CHANNEL_ID = None  # Will be set via command
MESSAGE_ID = None  # Will be updated when countdown posts

# Store settings in file
SETTINGS_FILE = "bot_settings.json"

def load_settings():
    global CHANNEL_ID, MESSAGE_ID
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            CHANNEL_ID = data.get("channel_id")
            MESSAGE_ID = data.get("message_id")

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump({
            "channel_id": CHANNEL_ID,
            "message_id": MESSAGE_ID
        }, f)

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Store end time
end_time = None
alerted_thresholds = []

@bot.event
async def on_ready():
    print(f"✓ Bot logged in as {bot.user}")
    print(f"✓ Status: Ready for countdown")
    load_settings()
    if CHANNEL_ID:
        print(f"✓ Channel set to: {CHANNEL_ID}")
    countdown_loop.start()

@bot.command(name="set_end_time")
async def set_end_time(ctx, end_time_str: str):
    """
    Set championship end time
    Usage: !set_end_time "03/07/2026 22:00"
    """
    global end_time, alerted_thresholds, CHANNEL_ID, MESSAGE_ID
    
    try:
        end_time = datetime.strptime(end_time_str, "%d/%m/%Y %H:%M")
        alerted_thresholds = []
        CHANNEL_ID = ctx.channel.id
        save_settings()
        
        await ctx.send(f"✓ Championship end time set to: **{end_time.strftime('%d/%m/%Y %H:%M')}**\n"
                       f"Countdown will start now!")
        print(f"✓ End time set: {end_time}")
        
    except ValueError:
        await ctx.send("❌ Invalid format! Use: `!set_end_time \"DD/MM/YYYY HH:MM\"`\n"
                       "Example: `!set_end_time \"03/07/2026 22:00\"`")

@bot.command(name="countdown_status")
async def countdown_status(ctx):
    """Check countdown status"""
    if end_time is None:
        await ctx.send("❌ No countdown active. Use `!set_end_time` to start.")
        return
    
    remaining = end_time - datetime.now()
    if remaining.total_seconds() <= 0:
        await ctx.send("⏰ Championship has ended!")
        return
    
    total_seconds = int(remaining.total_seconds())
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    
    await ctx.send(f"⏳ Time remaining: **{hours}h {minutes}m {seconds}s**\n"
                   f"End time: **{end_time.strftime('%d/%m/%Y %H:%M')}**")

def format_remaining(td):
    """Format timedelta as readable string"""
    if td.total_seconds() <= 0:
        return "0m 0s"
    total_seconds = max(0, int(td.total_seconds()))
    h, rem = divmod(total_seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"

async def send_alert(channel, remaining, threshold):
    """Send an alert message"""
    total_minutes = int(remaining.total_seconds() // 60)
    embed = discord.Embed(
        title=f"⏰ C.A.T.S. Championship Alert!",
        description=f"The championship ends in **{total_minutes} minutes**!",
        color=discord.Color.red()
    )
    embed.add_field(
        name="Expected End Time",
        value=f"**{end_time.strftime('%d/%m/%Y %H:%M')}**",
        inline=False
    )
    embed.add_field(
        name="Remaining Time",
        value=f"**{format_remaining(remaining)}**",
        inline=False
    )
    await channel.send(f"@here", embed=embed)

@tasks.loop(minutes=1)
async def countdown_loop():
    """Update countdown every minute"""
    global end_time, MESSAGE_ID, alerted_thresholds, CHANNEL_ID
    
    if end_time is None or CHANNEL_ID is None:
        return
    
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print("❌ Channel not found")
            return
        
        remaining = end_time - datetime.now()
        total_seconds = remaining.total_seconds()
        
        # Championship ended
        if total_seconds <= 0:
            embed = discord.Embed(
                title="🏆 Championship Ended!",
                description="The C.A.T.S. championship is now over.",
                color=discord.Color.gold()
            )
            await channel.send(embed=embed)
            end_time = None
            return
        
        # Prepare countdown message
        total_minutes = int(total_seconds // 60)
        embed = discord.Embed(
            title="⏳ C.A.T.S. Championship Countdown",
            description=f"**{format_remaining(remaining)}**",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="End Time",
            value=f"**{end_time.strftime('%d/%m/%Y %H:%M')}**",
            inline=False
        )
        embed.set_footer(text="Updates every minute")
        
        # Update or post countdown message
        if MESSAGE_ID:
            try:
                msg = await channel.fetch_message(MESSAGE_ID)
                await msg.edit(embed=embed)
            except discord.NotFound:
                msg = await channel.send(embed=embed)
                MESSAGE_ID = msg.id
                save_settings()
        else:
            msg = await channel.send(embed=embed)
            MESSAGE_ID = msg.id
            save_settings()
        
        # Send alerts at thresholds
        thresholds = [60, 15]
        for threshold in thresholds:
            if total_minutes <= threshold and threshold not in alerted_thresholds:
                await send_alert(channel, remaining, threshold)
                alerted_thresholds.append(threshold)
                print(f"✓ Alert sent for {threshold} minute threshold")
    
    except Exception as e:
        print(f"❌ Error in countdown loop: {e}")

# Run the bot
if __name__ == "__main__":
    print("🤖 C.A.T.S. Championship Discord Bot")
    print("="*50)
    print("\n⚠️  SETUP REQUIRED:")
    print("\n1. Go to: https://discord.com/developers/applications")
    print("2. Create a new application")
    print("3. Go to 'Bot' section and create a bot")
    print("4. Copy the TOKEN and paste it above (line 16)")
    print("5. Set INTENTS to: Message Content Intent (ON)")
    print("6. Under OAuth2 > URL Generator:")
    print("   - Scopes: bot")
    print("   - Permissions: Send Messages, Embed Links, Read Messages")
    print("7. Copy the generated URL and invite bot to your server")
    print("\n" + "="*50)
    print("\n📝 Usage in Discord:")
    print("  !set_end_time \"DD/MM/YYYY HH:MM\"")
    print("  !countdown_status")
    print("\n" + "="*50 + "\n")
    
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ Invalid token! Update TOKEN variable and try again.")
