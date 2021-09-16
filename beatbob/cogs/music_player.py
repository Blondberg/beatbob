import discord
from discord.errors import ClientException
from discord.ext import commands
from discord.ext.commands.errors import CommandRegistrationError
from discord.utils import get
import youtube_dl
import asyncio
import helpers.checkers as checkers
from helpers.messages import Message
from helpers.songlist import SongList

import json

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ytdl = youtube_dl.YoutubeDL(ydl_opts)


ffmpeg_options = {
    'options': '-vn'
}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, meta_data, volume=0.5):
        super().__init__(source, volume)

        self.meta_data = meta_data

        self.title = meta_data.get('title')
         # a specific URL needed for discord to play the music
        self.url = meta_data.get('url')
        self.duration = meta_data.get('duration')

    @classmethod
    async def from_url(cls, url, *, loop=None):

        # await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False)) # use the default exectutor (exectute calls asynchronously)
        meta_data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        # # TODO This is redundant and for debug purposes only!
        # with open('output.json', 'w') as f:
        #     f.write(json.dumps(meta_data))

        # TODO handle if it is a playlist, currently just takes the first song
        if 'entries' in meta_data:
            # take first item from a playlist
            meta_data = meta_data['entries'][0]

        return cls(discord.FFmpegPCMAudio(meta_data['url'], **ffmpeg_options), meta_data=meta_data)


class MusicPlayer(commands.Cog, name="Music Player"):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.songlist = SongList()

        # used to tell the player loop when the next song can be loaded
        self.next = asyncio.Event()
        self.queue = asyncio.Queue()

        self.loop_created = False


    async def player_loop(self, ctx):
        await self.bot.wait_until_ready()

        voice_client = ctx.guild.voice_client

        self.loop_created = True

        while not self.bot.is_closed():
            self.next.clear()

            # remove and return an item from the queue. Wait for available item if empty
            source = await self.queue.get()

            # play a song and set Event flag to true when done
            voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            # Wait for the previous song to finish
            await self.next.wait()

        # TODO clear everything if the bot is closed


    @commands.command(name="play", aliases=['p'], description="Plays the song from url or adds it to the queue")
    async def play(self, ctx: commands.Context, *, url):
        voice_client = ctx.message.guild.voice_client

        if not self.loop_created:
            self.bot.loop.create_task(self.player_loop(ctx))

        if voice_client.is_paused():
            self.resume(ctx)
            return

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)

            await self.queue.put(player)


    @commands.command(name='join', description='You want Beatbob in your life')
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice:
            await ctx.send(Message.USER_NOT_IN_CHANNEL.value)
            return False

        try:
            channel = ctx.author.voice.channel

            await channel.connect()
        except ClientException as e:
            print("Can't join a channel when already connected to it")
            return True


    @commands.command(name='leave', aliases=['l'], description='You no longer need Beatbob in your life')
    async def leave(self, ctx: commands.Context):
        # TODO remove current queue
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
    bot.add_cog(MusicPlayer(bot))