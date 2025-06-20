import discord
import asyncio
import datetime
import requests
import discord
from discord.ext import commands
import asyncio

TOKEN = "YOUR_TOKEN_HERE"  
PREFIX = "!"
WEBHOOK_URL = "YOUR_WEBHOOK_LINK_HERE"

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

afk_users = {}
deleted_messages = {}
edited_messages = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author != bot.user:
        if message.author.id in afk_users:
            await message.channel.send(f" {message.author.mention} is back! (AFK reason: {afk_users[message.author.id]})")
            del afk_users[message.author.id]
        return

    content = message.content.lower()

   
    if content == f"{PREFIX}purge":
        await message.delete()
        deleted = 0
        async for msg in message.channel.history(limit=10000):
            if msg.author == bot.user:
                try:
                    await msg.delete()
                    deleted += 1
                    await asyncio.sleep(1.5)
                except discord.errors.Forbidden:
                    print("Can't delete messages here.")
                    break
        await message.channel.send(f" Deleted {deleted} messages.", delete_after=5)

   
    elif content == f"{PREFIX}scan":
        await message.delete()
        flagged_users = ["1234567890", "0987654321"]
        async for msg in message.channel.history(limit=50):
            user = msg.author
            if user.bot or str(user.id) in flagged_users or len(msg.content) > 300:
                print(f"Possible self-bot or threat detected: {user}")
                await message.channel.send(f"⚠️ **Warning:** {user.mention} may be using a self-bot or be a scammer.")

   
    elif content == f"{PREFIX}read":
        await message.delete()
        messages = []
        async for msg in message.channel.history(limit=1000):  # Limit adjusted for performance
            timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            messages.append(f"[{timestamp}] {msg.author}: {msg.content}")

        with open("chat_log.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(messages))

        await message.channel.send(" Chat history saved!", delete_after=5)
        print("Chat history saved to chat_log.txt")

   
    elif content.startswith(f"{PREFIX}copy"):
        await message.delete()
        async for msg in message.channel.history(limit=10):
            if msg.author != bot.user:
                await message.channel.send(msg.content)
                break

    # Send command (sends a message 5 times)
    elif content.startswith(f"{PREFIX}send "):
        await message.delete()
        msg_to_send = message.content[len(f"{PREFIX}send "):]
        for _ in range(100000):
            await message.channel.send(msg_to_send)
            await asyncio.sleep(1)

   
    elif content.startswith(f"{PREFIX}afk"):
        reason = message.content[len(f"{PREFIX}afk "):] if len(message.content) > len(f"{PREFIX}afk") else "AFK"
        afk_users[message.author.id] = reason
        await message.channel.send(f" {message.author.mention} is now AFK: {reason}")

   
    elif content.startswith(f"{PREFIX}report "):
        args = message.content.split(" ", 3)
        if len(args) < 4:
            await message.channel.send(" Usage: `!report <type> <user> <reason>`", delete_after=5)
            return

        report_type, user, reason = args[1], args[2], args[3]
        report_data = {
            "content": f"🚨 **New Report Submitted!**\n**Type:** {report_type}\n**User:** {user}\n**Reason:** {reason}"
        }
        requests.post(WEBHOOK_URL, json=report_data)
        await message.channel.send(f" Report submitted for {user}.")

   
    elif content.startswith(f"{PREFIX}define "):
        word = message.content[len(f"{PREFIX}define "):].strip()
        if not word:
            await message.channel.send(" Please provide a word to define.", delete_after=5)
            return

        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        if response.status_code == 200:
            definition = response.json()[0]["meanings"][0]["definitions"][0]["definition"]
            await message.channel.send(f" **Definition of {word}:** {definition}")
        else:
            await message.channel.send(f" No definition found for '{word}'.", delete_after=5)

   
    elif content == f"{PREFIX}snipe":
        last_deleted = deleted_messages.get(message.channel.id)
        if last_deleted:
            await message.channel.send(f" **Last Deleted Message:** `{last_deleted.content}` - {last_deleted.author}")
        else:
            await message.channel.send(" No recently deleted messages.")

   
    elif content == f"{PREFIX}editsnipe":
        last_edit = edited_messages.get(message.channel.id)
        if last_edit:
            before, after = last_edit
            await message.channel.send(f"✏ **Last Edit:** `{before.content}` → `{after.content}` - {before.author}")
        else:
            await message.channel.send("❌ No recent message edits.")

@bot.event
async def on_message_delete(message):
    if message.author != bot.user:
        deleted_messages[message.channel.id] = message

@bot.event
async def on_message_edit(before, after):
    if before.author != bot.user:
        edited_messages[before.channel.id] = (before, after)

asyncio.run(run_bot())


