import discord
import os
from discord.ext import commands
from discord.gateway import EventListener
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX")

bot = commands.Bot(command_prefix=commands.when_mentioned_or(BOT_PREFIX))

@bot.event
async def on_ready():
    print("I am ready!")

bot.run(DISCORD_TOKEN)