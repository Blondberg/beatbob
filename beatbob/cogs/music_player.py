import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandRegistrationError
from discord.utils import get
import youtube_dl
import asyncio

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
            await ctx.send("You are not in a voice channel... idiot...")
            return
        channel = ctx.author.voice.channel

        await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)


    # @commands.command(name='play', description='Play the song of your choice!')
    # async def play(self, ctx: commands.Context, link='https://www.youtube.com/watch?v=nQOvMqePwMg'):

    #     song_info = ytdl.extract_info(link, download=False)
    #     voice = get(self.bot.voice_clients, guild=ctx.guild)

    #     if not link: # check if there is a link
    #         self.join(self, ctx)
    #         return

    #     await ctx.send(song_info)


    @commands.command()
    async def play(self, ctx: commands.Context, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')




    @commands.command(name='leave', description='You no longer need Beatbob in your life')
    async def leave(self, ctx: commands.Context):
        await ctx.voice_client.disconnect()


def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))