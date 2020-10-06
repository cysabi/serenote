import asyncio
import discord
from discord.ext import commands

from serenote import utils


class Tasks(commands.Cog):
    """Commands to managing tasks."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(invoke_without_command=True)
    async def task(self, ctx, *, task):
        """Create a new task.

        ```
        +task <name>
        <details>
        ```
        """
        await ctx.message.delete()
        lines = task.split("\n")
        if len(lines) == 1:
            await utils.Task(ctx, lines[0])
        else:
            await utils.Task(ctx, lines[0], "\n".join(lines[1:]))

def setup(bot):
    bot.add_cog(Tasks(bot))
