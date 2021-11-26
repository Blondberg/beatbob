from discord.ext import commands
from discord.ext.commands.errors import MissingPermissions
from cogs.music.music_player import MusicPlayer
import logging
import discord


class PlayerHandler(commands.Cog, name="Music Playing"):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.players = {} # a list of all the players
        self.logger = logging.getLogger('musicplayer')

    @commands.has_permissions(administrator=True)
    @commands.command(name='log', description='Show the bots log')
    async def log(self, ctx: commands.Context, *, level=''):
        with open('musicplayer.log') as f:
            content = f.read().splitlines()

        level = level.upper()

        embed = discord.Embed(title="Beatbob log", color=0xff0000)

        for line in content:
            log_level, log_message = line.split(':', 1)
            if (level and level == log_level) or (not level):
                embed.add_field(name=log_level, value=log_message + '\n', inline=False)

        await ctx.send(embed=embed)

    @log.error
    async def log_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            self.logger.error(f"{ctx.author} does not have permission to use command {ctx.command}")

    @commands.command(name="play", aliases=['p'], description="Plays the song from url or adds it to the queue")
    async def play(self, ctx: commands.Context, *, url=''):
        await self.get_guild(ctx.message.guild.id, ctx).play(ctx, url)

    @commands.command(name='queue', aliases=['q'], description='Displays the queue or adds a song to the q if an url is added')
    async def queue(self, ctx: commands.Context, *, url=''):
        await self.get_guild(ctx.message.guild.id, ctx).queue(ctx, url)

    @commands.command(name='join', description='You want Beatbob in your life')
    async def join(self, ctx: commands.Context):
        await self.get_guild(ctx.message.guild.id, ctx).join(ctx)

    @commands.command(name='pause', description='Pause the current song.')
    async def pause(self, ctx: commands.Context):
        await self.get_guild(ctx.message.guild.id, ctx).pause(ctx)

    @commands.command(name='resume', aliases=['r'], description='Resume a paused song')
    async def resume(self, ctx: commands.Context):
        await self.get_guild(ctx.message.guild.id, ctx).resume(ctx)

    @commands.command(name='skip', aliases=['next'], description='Play the next song')
    async def skip(self, ctx: commands.Context):
        await self.get_guild(ctx.message.guild.id, ctx).skip(ctx)

    @commands.command(name='leave', description='Make beatbob leave')
    async def leave(self, ctx: commands.Context):
        await self.get_guild(ctx.message.guild.id, ctx).leave(ctx)

    def get_guild(self, guild_id, ctx):
        """Get guild from players list by searching for guild_id. Adds new id and player if guild doesn't exist.

        Args:
            guild_id (int): Id for the guild

        Returns:
            Player: A music player connected to the specific guild
        """
        try:
            return self.players[guild_id]
        except KeyError:
            self.logger.info(f"Guild ID '{guild_id}' does not exist in the player list. Adding it")
            self.players[guild_id] = MusicPlayer(self.bot, guild_id, ctx)
            return self.players[guild_id]

    def remove_guild(self, guild_id):
        """Remove player from players list to prevent overcrowding

        Args:
            guild_id (guild_id): Id of guild to remove
        """
        try:
            del self.players[guild_id]
        except KeyError as e:
            self.logger.error(e)


def setup(bot: commands.Bot):
    bot.add_cog(PlayerHandler(bot))