import discord
import os
from discord.ext import commands
from discord.gateway import EventListener
from dotenv import load_dotenv
from apis.spotify_api import SpotifyApi
import cogs.music.player_handler
import cogs.misc

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX")

bot = commands.Bot(command_prefix=commands.when_mentioned_or(BOT_PREFIX))

cogs.music.player_handler.setup(bot)
cogs.misc.setup(bot)


@bot.event
async def on_ready():
    print("I am ready!")


@bot.event
async def on_message(message):
    """This is just used for logging purposes

    Args:
        message (ctx): meta data for a sent message aimed towards the bot
    """
    print("{0}: {1}".format(message.author, message.content))
    await bot.process_commands(message)


bot.run(DISCORD_TOKEN)

