import asyncio
import discord
from helpers.ytdlsource import YTDLSource
from discord.errors import ClientException
from helpers.songlist import SongList

import logging

class MusicPlayer:
    def __init__(self, bot, guild_id):

        self.logger = loggin.getLogger('musicplayer')
        self.guild_id = guild_id
        self.shuffle = False
        self.loop = False
        self.bot = bot

        self.loop_created = False

        self.next = asyncio.Event() # used to tell the player loop when the next song can be loaded

        self.songlist = SongList()


    async def player_loop(self, ctx):
        await self.bot.wait_until_ready()

        voice_client = ctx.guild.voice_client

        self.loop_created = True

        while not self.bot.is_closed():
            self.next.clear()

            # remove and return an item from the queue. Wait for available item if empty
            source = await self.songlist.get_next()

            # play a song and set Event flag to true when done
            voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            # Wait for the previous song to finish
            await self.next.wait()

        # TODO clear everything if the bot is closed


    async def pause(self, ctx):
        """Pause the current song

        Args:
            ctx (commands.Context): Context which the command is invoked under
        """
        voice_client = ctx.message.guild.voice_client

        if not voice_client or not voice_client.is_connected():
            await ctx.send("I am not connected to a channel...")
            return
        if voice_client.is_playing():
            voice_client.pause()

        else:
            await ctx.send("Can't pause music if I'm not playing")


    async def resume(self, ctx):
        """Resume the current song if player is paused, otherwise do nothing

        Args:
            ctx (commands.context): Context which the command is invoked under
        """
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.play()
        return


    async def play(self, ctx, url):
        """Either start playing if paused, or add a new song to the queue

        Args:
            ctx (commands.Context): Context which the command is invoked under the
            url (string): Youtube/Spotify url for the chosen song (could also be a youtube search)
        """
        voice_client = ctx.message.guild.voice_client

        if not voice_client or not voice_client.is_connected():
            await ctx.send("I am not connected to a voice channel! INCOMING!")
            voice_client = await self.join(ctx)

        if voice_client.is_paused():
            self.resume(ctx)
        elif not url:
            if self.songlist.get_queue().empty():
                await ctx.send("You need to give me an url so I know what to play...")
            return

        if not self.loop_created:
            self.bot.loop.create_task(self.player_loop(ctx))

        if voice_client.is_paused():
            self.resume(ctx)
            return


        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)

            await self.songlist.add_song(player)
            await ctx.send("Queued song: {} - [{}]".format(player.title, player.duration))
        return


    async def queue(self, ctx, url=''):
        """Show the queue or queue a song if an url is added

        Args:
            ctx (commands.Context): Context which the command is invoked under
            url (string): Youtube/Spotify url or Youtube search
        """
        queue_embed = self.songlist.get_queue_embed()
        async with ctx.typing():
            await ctx.send("Current queue: \n{}".format(queue_embed))


    async def join(self, ctx):
        """Join a voice_client

        Args:
            ctx (commands.Context): Context the comand is invoked under

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
            ctx (commands.Context): Context the command is invoked under
        """
        try:
            voice_client = ctx.message.author.guild.voice_client
            if voice_client or not voice_client.is_connected() :
                await ctx.voice_client.disconnect()
                self.bot.loop.clear()
                self.songlist.clear()
                return
        except Exception as e:
            print("Something went wrong when trying to leave channel")
            print(e)

        await ctx.send("I am not in a channel, so I can't leave.")


    async def skip(self, ctx):
        """Skip the currently playing song. Notify if the queue is empty.py

        Args:
            ctx (commands.Context): Context which the command is invoked under
        """
        try:
            ctx.message.guild.voice_client.stop()
            self.next.set()
            if self.songlist.get_queue().empty():
                await ctx.send("There are no more songs in the queue! Used -p to add more.")
        except Exception as e:
            print("Something went wrong skipping song.")
            print(e)