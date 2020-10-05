import discord
from discord.ext import commands

import ui


class Tasks(commands.Cog):
    """Commands to managing tasks."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def task(self, ctx, *, task):
        """Create a new task."""
        await ui.Alert(ctx, ui.Alert.Style.SUCCESS, title="New Task", description=task)

    @task.command()
    async def delete(self, ctx, *, task):
        """Delete a task."""
        await ui.Alert(ctx, ui.Alert.Style.DANGER, title="Task Deleted", description=task)

def setup(bot):
    bot.add_cog(Tasks(bot))
