import discord
from discord.errors import ClientException
from discord.ext import commands
import youtube_dl
import asyncio
from cogs.music.music_player import MusicPlayer
from helpers.messages import Message
from helpers.songlist import SongList
from helpers.ytdlsource import YTDLSource


class PlayerHandler(commands.Cog, name="Player handler"):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.songlist = SongList()
        self.players = {} # a list of all the players


    @commands.command(name="play", aliases=['p'], description="Plays the song from url or adds it to the queue")
    async def play(self, ctx: commands.Context, *, url=''):
        guild_id = ctx.message.guild.id

        try:
            await self.players[guild_id].play(ctx, url)
        except KeyError as e:
            print(e)
            print("The guild ID '{0}' does not exist in the player list. Adding it...".format(guild_id))
            self.players[guild_id] = MusicPlayer(self.bot, guild_id)
            await self.players[guild_id].play(ctx, url)


    @commands.command(name='join', description='You want Beatbob in your life')
    async def join(self, ctx: commands.Context):
        guild_id = ctx.message.guild.id

        try:
            await self.players[guild_id].join(ctx)
        except KeyError as e:
            print(e)
            print("The guild ID '{0}' does not exist in the player list. Adding it...".format(guild_id))
            self.players[guild_id] = MusicPlayer(self.bot, guild_id)
            await self.players[guild_id].join(ctx)



    @commands.command(name='leave', aliases=['l'], description='You no longer need Beatbob in your life')
    async def leave(self, ctx: commands.Context):
        try:
            voice_client = ctx.message.author.guild.voice_client
            if voice_client or not voice_client.is_connected() :
                await ctx.voice_client.disconnect()
                self.bot.loop.clear()
                self.songlist.clear()
                return
        except AttributeError as e:
            print(e)
            print("Tried to leave channel when not connected")

        await ctx.send(Message.NOT_IN_CHANNEL.value)


    @commands.command(name='pause', description="Pause the current song.")
    async def pause(self, ctx: commands.Context):
        voice_client = ctx.message.guild.voice_client

        if not voice_client or not voice_client.is_connected():
            await ctx.send("I am not connected to a channel...")
            return
        if voice_client.is_playing():
            voice_client.pause()

        else:
            await ctx.send(Message.NOT_PLAYING.value)


    @commands.command(name="resume", aliases=['r'], description="Resume a paused song")
    async def resume(self, ctx: commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.play()


def setup(bot: commands.Bot):
    bot.add_cog(PlayerHandler(bot))