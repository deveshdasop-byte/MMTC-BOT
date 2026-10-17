import discord
from discord.ext import commands
import os, json, re
from flask import Flask, jsonify
from threading import Thread

# TOKEN IS READ FROM RENDER ENV - NO TOKEN INSIDE FILE
TOKEN = os.getenv("TOKEN")

DATA_FILE = "leaderboard.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE,"w") as f:
        json.dump([],f)

def load_data():
    with open(DATA_FILE,"r") as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE,"w") as f:
        json.dump(d,f,indent=2)

# WEBSITE API - your Netlify site will read from here
app = Flask('')
@app.route('/')
def home():
    return "MMTC Board - Alive"

@app.route('/api/leaderboard')
def api():
    return jsonify(load_data())

def run():
    app.run(host='0.0.0.0',port=8080)

def keep_alive():
    Thread(target=run).start()

# DISCORD BOT
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot ON: {bot.user}")
    await bot.tree.sync()

# AUTO RECEIVE - just type: NoMercy Sword LT3
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    match = re.search(r"(\w+)\s+(\w+)\s+(LT\d|HT\d|MT\d|H\d|M\d|L\d)", message.content, re.IGNORECASE)
    if match:
        ign, mode, tier = match.groups()
        data = load_data()
        data = [p for p in data if not (p['ign'].lower()==ign.lower() and p['mode'].lower()==mode.lower())]
        data.append({"ign": ign, "mode": mode.upper(), "tier": tier.upper()})
        save_data(data)
        await message.channel.send(f"✅ AUTO SAVED: **{ign}** | {mode.upper()} = **{tier.upper()}**")

@bot.tree.command(name="start", description="Show board")
async def start(interaction: discord.Interaction):
    data = load_data()
    embed = discord.Embed(title="MMTC - Live Board", color=0x00ff88)
    if not data:
        embed.description = "No players yet - waiting for auto data..."
    else:
        txt = "\n".join([f"#{i+1} **{p['ign']}** - {p['mode']} {p['tier']}" for i,p in enumerate(data[:30])])
        embed.description = txt
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="addtier", description="Manual add")
async def addtier(interaction: discord.Interaction, ign: str, mode: str, tier: str):
    data = load_data()
    data = [p for p in data if not (p['ign'].lower()==ign.lower() and p['mode'].lower()==mode.lower())]
    data.append({"ign": ign, "mode": mode.upper(), "tier": tier.upper()})
    save_data(data)
    await interaction.response.send_message(f"✅ Added {ign} {mode.upper()} {tier.upper()} - website auto updated")

keep_alive()
bot.run(TOKEN)
