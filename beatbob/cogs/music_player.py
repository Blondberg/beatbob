import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandRegistrationError
from discord.utils import get
import youtube_dl
import asyncio
import helpers.checkers as checkers
from helpers.messages import Message

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
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class MusicPlayer(commands.Cog, name="Music Player"):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot

        # queue is a directory that keeps track of the tracks
        self.queue = {}


    @commands.command(name='join', description='You want Beatbob in your life')
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice:
            await ctx.send(Message.USER_NOT_IN_CHANNEL.value)
            return
        channel = ctx.author.voice.channel

        await channel.connect()


    @commands.command()
    async def play(self, ctx: commands.Context, *, url):
        # TODO join channel if not in one
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            self.resume(ctx)
            return

        if voice_client.is_playing():
            # TODO add to queue
            return

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')


    @commands.command(name='leave', description='You no longer need Beatbob in your life')
    async def leave(self, ctx: commands.Context):
        # TODO remove current queue
        if checkers.is_connected(ctx):
            await ctx.voice_client.disconnect()
            return
        await ctx.send(Message.NOT_IN_CHANNEL.value)


    @commands.command(name='pause', description="Pause the current song.")
    async def pause(self, ctx: commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()

        else:
            await ctx.send("I am not playing anything currently...")

    @commands.command(name="resume", description="Resume a paused song")
    async def resume(self, ctx: commands.Context):
        return True


def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))