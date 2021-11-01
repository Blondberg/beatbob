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
            print("Finished playing song: {}".format(source.title))

        # TODO clear everything if the bot is closed


    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if not voice_client or not voice_client.is_connected():
            await ctx.send("I am not connected to a channel...")
            return
        if voice_client.is_playing():
            voice_client.pause()

        else:
            await ctx.send("Can't pause music if I'm not playing")


    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.play()
        return


    async def play(self, ctx, url):
        voice_client = ctx.message.guild.voice_client

        if not voice_client or not voice_client.is_connected():
            await ctx.send("I am not connected to a voice channel! INCOMING!")
            voice_client = await self.join(ctx)

        if not url:
            await ctx.send("You need to give me an url so I know what to play...")
            return

        if not self.loop_created:
            self.bot.loop.create_task(self.player_loop(ctx))

        if voice_client.is_paused():
            self.resume(ctx)
            return

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)

            await self.queue.put(player)
            await ctx.send("Queued song: {} - [{}]".format(player.title, player.duration))
        return


    async def join(self, ctx):
        """Join a voice_client

        Args:
            ctx (ctx): commands.ctx

        Returns:
            voice_client: The voice_client connected to (if successful)
        """
        if not ctx.author.voice:
            await ctx.send("You need to be in a joinable channel for me to join the party.")
            return

        try:
            channel = ctx.author.voice.channel

            await channel.connect()

            voice_client = ctx.message.guild.voice_client
        except ClientException:
            print("Can't join a channel when already connected to it")
            return False

        return voice_client

    async def leave(self, ctx):
        """Leave the current voice channel (if any)

        Args:
            ctx (ctx): Info about the message (channel etc.)
        """
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

        await ctx.send("I am not in a channel, so I can't leave.")
        return


    async def skip(self, ctx):
        try:
            ctx.message.guild.voice_client.stop()
            self.next.set()
            if self.queue.empty():
                await ctx.send("There are no more songs in the queue! Used -p to add more.")
        except Exception as e:
            print("Something went wrong skipping song.")
            print(e)