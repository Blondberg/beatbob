import discord
from discord.ext import commands

class CommonCog(commands.Cog, name = "Common Commands"):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot

    @commands.command(name="ganggang", description="Links to the gang gang videos")
    async def ganggang(self, ctx: commands.Context):
        await ctx.send("Link to gang gang videos: https://www.youtube.com/user/StaticalFlun98")
        return


def setup(bot: commands.Bot):
    bot.add_cog(CommonCog(bot))