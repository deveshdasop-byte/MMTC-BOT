import discord
from discord.ext import commands, tasks
import json, os
import aiohttp

TOKEN = os.getenv("TOKEN")
SOURCE_URL = "https://your-website.com/api/players.json" 
ANNOUNCE_CHANNEL_ID = 123456789

TIER_POINTS = {"HT1":100,"HT2":80,"HT3":60,"LT1":40,"LT2":25,"LT3":15,"LT4":8,"LT5":3,"Untested":0}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
old_data = {}

@bot.event
async def on_ready():
    print(f"Logged as {bot.user} - FULL AUTO MODE ON")
    auto_checker.start()

@tasks.loop(minutes=2)
async def auto_checker():
    global old_data
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SOURCE_URL) as r:
                new_data = await r.json()
        channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
        for ign, tiers in new_data.items():
            if ign not in old_data:
                if channel:
                    await channel.send(f"✅ **AUTO ADDED:** {ign} joined MMTC!")
            else:
                for mode, new_tier in tiers.items():
                    old_tier = old_data.get(ign, {}).get(mode, "Untested")
                    if old_tier != new_tier:
                        embed = discord.Embed(title=f"AUTO UPDATE: {ign}", color=0x00ff00)
                        embed.add_field(name=mode, value=f"{old_tier} -> **{new_tier}**")
                        if channel:
                            await channel.send(embed=embed)
        old_data = new_data
    except Exception as e:
        print(f"Auto check fail: {e}")

bot.run(TOKEN)
