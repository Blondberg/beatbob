from discord.utils import get
from discord.ext import commands


def is_connected(ctx: commands.Context):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client