import re

import discord
from discord.ext import commands

from serenote import utils, db


class Task(commands.Cog):
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
            if str(ctx.author.id) in word and ctx.author.id in assignee_ids:  # Unassign the author
                assignee_ids.remove(ctx.author.id)
            elif re.match(r'<@!?\d{1,}>', word):  # Assign a user
                assignee_ids.append(int(re.sub(r'\D', '', word)))
            elif re.match(r'<@&\d{1,}>', word):  # Assign a role
                assigned_role_ids.append(int(re.sub(r'\D', '', word)))
            else:
                break
        return (assignee_ids, assigned_role_ids), " ".join(words)

    @commands.command()
    async def tasks(self, ctx):
        """Get a list of all of your tasks.
        Please note that this only retrieves the tasks that are directly assigned to you, not by role.
        """
        tasks = await utils.Task.query(ctx, assignee_ids=ctx.author.id)
        bullet = {
            "unchecked": 768579164445605928,
            "checked": 768579164092628994
        }
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title=f"Tasks assigned to **{ctx.author.name}**",
            description=self.create_task_list(tasks, bullet["unchecked"], False)
        )
        if completed := self.create_task_list(tasks, bullet["checked"], True):
            embed.add_field(name="Completed Tasks", value=completed)
        await ctx.send(embed=embed)

    def create_task_list(self, tasks, bullet, check):
        task_list = "\n".join([
            f"{self.bot.get_emoji(bullet)} [{task.panel.title}]({task.message.jump_url})"
            for task in tasks
            if task.checked() == check
        ])
        if not task_list and not check:
            return "> *You don't have any tasks, make some!*"
        return task_list

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def task_action_add(self, payload):
        await self.on_reaction(payload, True)

    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def task_action_remove(self, payload):
        await self.on_reaction(payload, False)

    async def on_reaction(self, payload, add: bool):
        """Run task.action if the reaction is on the task message."""
        if task := await utils.Task.get(self.bot, payload.message_id):
            try:
                await task.action(payload.user_id, payload.emoji.name, add)
            except discord.NotFound:
                pass

    @commands.Cog.listener(name='on_message_delete')
    async def task_delete(self, message):
        """Run task delete if the user deletes the deleted."""
        if task_obj := db.get_task(message.id):
            task_obj.delete()

def setup(bot):
    bot.add_cog(Task(bot))
