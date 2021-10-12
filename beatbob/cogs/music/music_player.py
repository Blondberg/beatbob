import asyncio
import discord
from helpers.ytdlsource import YTDLSource
from discord.errors import ClientException

class MusicPlayer:
    def __init__(self, bot, guild_id):
        self.guild_id = guild_id
        self.shuffle = False
        self.loop = False
        self.bot = bot

        self.loop_created = False

        # used to tell the player loop when the next song can be loaded
        self.next = asyncio.Event()
        self.queue = asyncio.Queue()


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


    async def resume():
        return

    async def play(self, ctx, url):
        voice_client = ctx.message.guild.voice_client

        if not voice_client or not voice_client.is_connected():
            await ctx.send("I am not connected to a voice channel! Try -join.")
            return False

        if not url:
            await ctx.send("You need to give me an url so I know what to play...")
            return False

        if not self.loop_created:
            self.bot.loop.create_task(self.player_loop(ctx))

        if voice_client.is_paused():
            self.resume(ctx)
            return

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)

            await self.queue.put(player)
        return

    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("You are currently not in a joinable channel")
            return False

        try:
            channel = ctx.author.voice.channel

            await channel.connect()
        except ClientException as e:
            print("Can't join a channel when already connected to it")
            return True

    async def clear():
        return

    async def queue():
        return

    async def loop():
        return

    async def shuffle():
        return
