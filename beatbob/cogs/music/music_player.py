import asyncio
import discord
from helpers.ytdlsource import YTDLSource
from discord.errors import ClientException
from helpers.songlist import SongList

import logging

class MusicPlayer:
    def __init__(self, bot, guild_id, ctx):

        self.logger = logging.getLogger('musicplayer')
        self.guild_id = guild_id
        self.shuffle = False
        self.loop = False
        self.bot = bot

        self.ctx = ctx

        self.next = asyncio.Event() # used to tell the player loop when the next song can be loaded

        self.songlist = SongList()

        self.player_loop = self.bot.loop.create_task(self.player_loop_task())

        self.voice_client = None

        self.current_song = None

        self.goodbye = discord.FFmpegPCMAudio("beatbob\cogs\music\goodbye.mp3")


    async def player_loop_task(self):
        await self.bot.wait_until_ready()

        while True:
            self.next.clear()

            self.current_song = await self.songlist.get_next()

            # play a song and set Event flag to true when done
            try:
                self.logger.debug('Trying to play a song')
                self.voice_client.play(self.current_song, after=lambda _: self.bot.loop.call_soon_threadsafe(self.play_next_song))
            except:
                print("Something went wrong when playing song")
            # Wait for the previous song to finish
            await self.next.wait()


    def play_next_song(self, error=None):
        if error:
            self.logger.error('There was an error in play_next_song().')
        self.next.set()


    async def stop(self, ctx):
        await ctx.invoke.pause(ctx)


    async def pause(self, ctx):
        """Pause the current song

        Args:
            ctx (commands.Context): Context which the command is invoked under
        """

        if not self.voice_client or not self.voice_client.is_connected():
            await ctx.send("I am not connected to a channel...")
            return
        if self.voice_client.is_playing():
            self.voice_client.pause()

        else:
            await ctx.send("Can't pause music if I'm not playing")


    async def resume(self, ctx):
        """Resume the current song if player is paused, otherwise do nothing

        Args:
            ctx (commands.context): Context which the command is invoked under
        """
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()



    async def play(self, ctx, url):
        """Either start playing if paused, or add a new song to the queue

        Args:
            ctx (commands.Context): Context which the command is invoked under the
            url (string): Youtube/Spotify url for the chosen song (could also be a youtube search)
        """
        self.voice_client = ctx.message.guild.voice_client

        if not self.voice_client or not self.voice_client.is_connected():
            await ctx.send("I am not connected to a voice channel! INCOMING!")
            await self.join(ctx)


        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()

        if url:
            async with ctx.typing():
                try:
                    player = await YTDLSource.from_url(url, loop=self.bot.loop)
                except:
                    self.logger.error("Something went wrong fetching player")
                else:
                    await self.songlist.add_song(player)
                    await ctx.send("Queued song: {} - [{}]".format(player.title, player.duration))


    async def join(self, ctx):
        """Join a voice_client

        Args:
            ctx (commands.Context): Context the comand is invoked under

        Returns:
            voice_client: The voice_client connected to (if successful)
        """
        if not ctx.author.voice:
            await ctx.send("You are not in a joinable channel!")
            return

        try:
            channel = ctx.author.voice.channel
            await channel.connect()
            self.logger.debug('Joined channel: {}'.format(channel.name))
            self.voice_client = ctx.message.guild.voice_client

        except ClientException:
            print("Can't join a channel when already connected to it")
            return False


    async def skip(self, ctx):
        """Skip the currently playing song. Notify if the queue is empty.py
        """

        try:
            self.logger.info('Trying to skip a song.')
            if self.voice_client.is_playing():
                self.voice_client.stop()

        except:
            self.logger.error('Couldn\'t skip the song.')
        else:
            self.logger.info('Skipped song.')


    async def leave(self, ctx):
        self.voice_client.play(self.goodbye)
        while self.voice_client.is_playing():
            pass
        await self.voice_client.disconnect()
