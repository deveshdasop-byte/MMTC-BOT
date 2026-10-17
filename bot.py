import discord
import json
import os
import re
from flask import Flask, jsonify
from threading import Thread

# --- FLASK API FOR WEBSITE ---
app = Flask(__name__)

@app.route('/')
def home():
    return "MMTC Bot is Live"

@app.route('/api/leaderboard')
def leaderboard():
    if not os.path.exists('data.json'):
        return jsonify([])
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except:
        return jsonify([])

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- DISCORD BOT ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

VALID_MODES = ["SWORD", "CRYSTAL", "UHC", "AXE", "MACE", "SMP"]
VALID_TIERS = ["HT1","LT1","MT1","HT2","MT2","LT2","HT3","MT3","LT3","HT4","MT4","LT4","HT5","MT5","LT5"]

def load_data():
    if not os.path.exists('data.json'):
        return []
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.author.bot:
        return

    content = message.content.strip()
    if not content:
        return

    # Expected: IGN MODE TIER  e.g. NotArjunYT Sword LT3
    parts = content.split()
    if len(parts) != 3:
        return

    ign, mode, tier = parts
    mode = mode.upper()
    tier = tier.upper()

    if mode not in VALID_MODES:
        return
    if tier not in VALID_TIERS:
        return

    # Clean IGN
    if len(ign) < 2 or len(ign) > 20:
        return

    data = load_data()

    # Remove old entry for same IGN + MODE
    data = [d for d in data if not (d['ign'].lower() == ign.lower() and d['mode'] == mode)]

    # Add new
    data.append({
        "ign": ign,
        "mode": mode,
        "tier": tier
    })

    save_data(data)

    try:
        await message.add_reaction("✅")
    except:
        await message.channel.send(f"Saved: {ign} {mode} {tier}")

if __name__ == "__main__":
    # Start Flask in background
    Thread(target=run_flask, daemon=True).start()
    
    token = os.getenv("TOKEN")
    if not token:
        print("ERROR: TOKEN env variable not set")
    else:
        client.run(token)
