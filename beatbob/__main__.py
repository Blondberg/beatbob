import discord
import os
from discord.ext import commands
from discord.gateway import EventListener
from dotenv import load_dotenv
from apis.spotify_api import SpotifyApi
import cogs.music.player_handler
import cogs.misc
from datetime import datetime

import logging

# Setup discord logger
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Setup music player logger
logger = logging.getLogger('musicplayer')
logger.setLevel(logging.DEBUG)


handler = logging.FileHandler(filename='musicplayer.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX")

bot = commands.Bot(command_prefix=commands.when_mentioned_or(BOT_PREFIX))
game = discord.Game("none of your business")

cogs.music.player_handler.setup(bot)
cogs.misc.setup(bot)

@bot.event
async def on_command(ctx):
    logger = logging.getLogger('musicplayer')
    logger.info("COMMAND: {} > {} > {}".format(ctx.guild.name, ctx.author, ctx.command))


@bot.event
async def on_ready():
    print("I am ready!")
    await bot.change_presence(status=discord.Status.idle, activity=game)
    logger = logging.getLogger('musicplayer')
    logger.info("The bot is ready!")


# @bot.event
# async def on_message(message):
#     """This is just used for logging purposes

#     Args:
#         message (ctx): meta data for a sent message aimed towards the bot
#     """

#     now = datetime.now()
#     print("{} [{}]: {}".format(message.author, now.strftime("%d/%m/%y %H:%M:%S"), message.content))
#     await bot.process_commands(message)


bot.run(DISCORD_TOKEN, reconnect=True)

