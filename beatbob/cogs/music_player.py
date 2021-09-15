import discord
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
        self.url = meta_data.get('url') # a specific URL needed for discord to play the music
        self.duration = meta_data.get('duration')
        print(self.duration)

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop
        meta_data = ytdl.extract_info(url, download=False) # await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False)) # use the default exectutor (exectute calls asynchronously)

        # TODO This is redundant and for debug purposes only!
        with open('output.json', 'w') as f:
            f.write(json.dumps(meta_data))

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


    @commands.command(name='join', description='You want Beatbob in your life')
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice:
            await ctx.send(Message.USER_NOT_IN_CHANNEL.value)
            return False
        channel = ctx.author.voice.channel

        await channel.connect()

        return True


    @commands.command(name="play", aliases=['p'], description="Plays the song from url or adds it to the queue")
    async def play(self, ctx: commands.Context, *, url):
        voice_client = ctx.message.guild.voice_client

        # Try to join channel if not connected
        if not voice_client or not voice_client.is_connected():
            if not self.join(ctx): # if join failed, don't continue
                return False

        if voice_client.is_paused():
            self.resume(ctx)
            return

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            self.songlist.add(player)

            if voice_client.is_playing():
                # TODO add to queue
                self.bot.loop.create_task()
            print("Current songlist: ", self.songlist)
            voice_client.play(player)
        await ctx.send(f'Now playing: {player.title}')


    @commands.command(name='leave', aliases=['l'], description='You no longer need Beatbob in your life')
    async def leave(self, ctx: commands.Context):
        # TODO remove current queue
        try:
            voice_client = ctx.message.author.guild.voice_client
            if voice_client or not voice_client.is_connected() :
                await ctx.voice_client.disconnect()
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


    @commands.command(name="queue", description="Display the current song queue")
    async def queue(self, ctx: commands.Context):
        await ctx.send("The current queue is: ")



    @commands.command(name="resume", aliases=['r'], description="Resume a paused song")
    async def resume(self, ctx: commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.play()


def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))