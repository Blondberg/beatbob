import discord
import os
from discord.ext import commands
from discord.gateway import EventListener
from dotenv import load_dotenv
from apis.spotify_api import SpotifyApi
import cogs.music_player as music_player
import youtube_dl

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX")

ydl_opts = {
    'format': 'bestaudio/best'
}
ydl = youtube_dl.YoutubeDL(ydl_opts)

bot = commands.Bot(command_prefix=commands.when_mentioned_or(BOT_PREFIX))

music_player.setup(bot)


@bot.event
async def on_ready():
    print("I am ready!")

bot.run(DISCORD_TOKEN)