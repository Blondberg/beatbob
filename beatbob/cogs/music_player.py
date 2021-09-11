from discord.ext import commands

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


    @commands.command(name='leave', description='You no longer need Beatbob in your life')
    async def leave(self, ctx: commands.Context):
        await ctx.voice_client.disconnect()


def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))