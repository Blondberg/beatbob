import discord
import os
from discord.ext import commands
from discord.gateway import EventListener
from dotenv import load_dotenv
from apis.spotify_api import SpotifyApi
import cogs.music_player as music_player
import cogs.common as common_commands

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX")

bot = commands.Bot(command_prefix=commands.when_mentioned_or(BOT_PREFIX))

music_player.setup(bot)
common_commands.setup(bot)


@bot.event
async def on_ready():
    print("I am ready!")

bot.run(DISCORD_TOKEN)

