import discord
from discord.ext import commands


class Tasks(commands.Cog):
    """Commands to managing tasks."""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()

    @commands.group(invoke_without_subcommand=True)
    async def task()


def setup(bot):
    bot.add_cog(Tasks(bot))