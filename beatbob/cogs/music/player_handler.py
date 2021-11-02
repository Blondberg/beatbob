import discord
from discord.errors import ClientException
from discord.ext import commands
import youtube_dl
import asyncio
from cogs.music.music_player import MusicPlayer


class PlayerHandler(commands.Cog, name="Music Playing"):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.players = {} # a list of all the players


    @commands.command(name="play", aliases=['p'], description="Plays the song from url or adds it to the queue")
    async def play(self, ctx: commands.Context, *, url=''):
        await self.get_guild(ctx.message.guild.id).play(ctx, url)

    @commands.command(name='queue', aliases=['q'], description='Displays the queue or adds a song to the q if an url is added')
    async def queue(self, ctx: commands.Context, *, url=''):
        await self.get_guild(ctx.message.guild.id).queue(ctx, url)

    @commands.command(name='join', description='You want Beatbob in your life')
    async def join(self, ctx: commands.Context):
        await self.get_guild(ctx.message.guild.id).join(ctx)


    @commands.command(name='leave', aliases=['l'], description='You no longer need Beatbob in your life')
    async def leave(self, ctx: commands.Context):
        await self.get_guild(ctx.message.guild.id).leave(ctx)
        await self.remove_guild(ctx.message.guild.id)


    @commands.command(name='pause', description='Pause the current song.')
    async def pause(self, ctx: commands.Context):
        await self.get_guild(ctx.message.guild.id).pause(ctx)


    @commands.command(name='resume', aliases=['r'], description='Resume a paused song')
    async def resume(self, ctx: commands.Context):
        await self.get_guild(ctx.message.guild.id).resume(ctx)

    @commands.command(name='skip', aliases=['next'], description='Play the next song')
    async def skip(self, ctx: commands.Context):
        await self.get_guild(ctx.message.guild.id).skip(ctx)

    def get_guild(self, guild_id):
        """Get guild from players list by searching for guild_id. Adds new id and player if guild doesn't exist.

        Args:
            guild_id (int): Id for the guild

        Returns:
            Player: A music player connected to the specific guild
        """
        try:
            return self.players[guild_id]
        except KeyError:
            print("The guild ID '{}' does not exist in the player list. Adding it...".format(guild_id))
            self.players[guild_id] = MusicPlayer(self.bot, guild_id)
            return self.players[guild_id]

    def remove_guild(self, guild_id):
        """Remove player from players list to prevent overcrowding

        Args:
            guild_id (guild_id): Id of guild to remove
        """
        try:
            del self.players[guild_id]
        except Exception as e:
            print("Something went wrong guild id from player list")
            print(e)


def setup(bot: commands.Bot):
    bot.add_cog(PlayerHandler(bot))