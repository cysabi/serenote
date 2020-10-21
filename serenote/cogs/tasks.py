import re

import discord
from discord.ext import commands

from serenote import utils, db


class Tasks(commands.Cog):
    """Commands to managing tasks."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(invoke_without_command=True)
    async def task(self, ctx, *, task):
        """Create a new task.

        ```
        +task [<assignees>] <name>
        [<details>]
        ```
        """
        # Parse task
        lines = task.split("\n")
        assignees, lines[0] = self.get_assignees(ctx, lines[0])
        if lines[0] == '':
            raise commands.MissingRequiredArgument(self.task)
        # Make args
        args = [ctx, lines[0]]
        if len(lines) > 1:
            args.append("\n".join(lines[1:]))
        # Build task
        await ctx.message.delete()
        await utils.Task.create(*args, assignees=assignees)

    @staticmethod
    def get_assignees(ctx, content):
        """Get all assignee ids.
        :returns: tuple(
            tuple(assignee ids, assignee role ids),
            The pruned task content without assignee mentions
        )
        """
        assignee_ids = [ctx.author.id]
        assigned_role_ids = []
        words = content.split()
        for word in content.split():
            if re.match(r'<@!?\d{1,}>', word):  # Assign a user
                assignee_ids.append(int(re.sub(r'\D', '', word)))
                words.pop(0)
            elif re.match(r'<@&\d{1,}>', word):  # Assign a role
                assigned_role_ids.append(int(re.sub(r'\D', '', word)))
                words.pop(0)
            elif str(ctx.author.id) in word and ctx.author.id in assignee_ids:  # Unassign the author
                assignee_ids.remove(ctx.author.id)
            else:
                break
        return (assignee_ids, assigned_role_ids), " ".join(words)

    @commands.command()
    async def tasks(self, ctx):
        """Get a list of all of your tasks.
        Please note that this only retrieves the tasks that are directly assigned to you, not by role.
        """
        tasks = await utils.Task.query(ctx, assignee_ids=ctx.author.id)
        task_list = "\n".join([
            f"`-` [{task.panel.title}]({task.message.jump_url})" for task in tasks
        ])
        await ctx.send(embed=discord.Embed(
            color=discord.Color.blurple(),
            title=f"Tasks assigned to **{ctx.author.name}**",
            description=task_list
        ))

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def task_action_add(self, payload):
        """Run task.action if the added reaction is on the task message."""
        if task := await self.get_task(payload):
            try:
                await task.action(payload, True)
            except discord.NotFound:
                pass

    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def task_action_remove(self, payload):
        """Run task.action if the removed reaction is on the task message."""
        if task := await self.get_task(payload):
            try:
                await task.action(payload, False)
            except discord.NotFound:
                pass
    
    @commands.Cog.listener(name='on_message_delete')
    async def task_delete(self, message):
        """Run task delete if the user deletes the deleted."""
        if task_obj := db.get_task(message.id):
            task_obj.delete()

def setup(bot):
    bot.add_cog(Tasks(bot))
