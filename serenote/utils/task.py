"""Contains the Task class."""

import discord

from serenote import utils, db


class Task:
    """Task class to handle all the work of managing a task."""

    status = {
        False: "<:task_unchecked:807724224411729960>",
        True: "<:task_checked:807724224416317470>"
    }

    @classmethod
    async def create(cls, ctx, title, description=discord.Embed.Empty, **kwargs):
        """Create a new task and return associated Task object."""
        # Create task panel
        embed = cls.create_panel(ctx, title, description, **kwargs)
        panel = await ctx.send(embed=embed)  # Send panel embed
        # Add actions
        actions = {"complete": 762882665274933248, "delete": 763192427732926465}
        for action in actions.values():
            react = ctx.bot.get_emoji(action)
            await panel.add_reaction(react)
        # Insert task into database
        db_task = db.Task(
            message_id=panel.id,
            channel_id=panel.channel.id,
            author_id=ctx.author.id,
            assignee_ids=kwargs['assignees'][0],
            assigned_role_ids=kwargs['assignees'][1]
        )
        db_task.save()
        # Build task object
        return Task(panel)

    @classmethod
    def create_panel(cls, ctx, title, description, **kwargs):
        """Helper function to assist with cls.create."""
        # Add panel meta
        panel_meta = {}
        panel_meta["Assignees"] = cls.get_assignees(ctx, kwargs['assignees'])  # display assignees meta
        # Set panel title
        title = f"{cls.status[False]} {title}"
        # Return panel object
        return utils.Panel("Task", panel_meta,
            title=title,
            description=description)

    @staticmethod
    def get_assignees(ctx, ids) -> list:
        """ Helper function to assist with cls.create_panel.

        Return a list of all role and user objects that are assignees.
        """
        assignees = []
        for role in ids[1]:
            assignee = ctx.guild.get_role(role)
            if not assignee in assignees:
                assignees.append(assignee)
        for user in ids[0]:
            assignee = ctx.bot.get_user(user)
            if not assignee in assignees:
                assignees.append(assignee)
        return assignees

    @staticmethod
    async def get(bot, message_id):
        """Return task object from reaction payload."""
        # Ensure the message even is a task
        if not (db_task := db.get_task(message_id)):
            return
        # Attempt to find task object
        if not (channel := bot.get_channel(db_task.channel_id)):
            return db_task.delete()
        try:
            message = await channel.fetch_message(db_task.message_id)
        except discord.NotFound:
            return db_task.delete()
        # Create task object
        task = Task(message)
        # If task embed has been removed
        if not task.message.embeds:
            return await task.delete()
        return Task(message)

    def __init__(self, message):
        self.message = message
        self.db = db.get_task(message.id)
        # Wrap message values
        self.guild = self.message.channel.guild
        self.panel = utils.Panel.from_embed(self.message.embeds[0])
        # Wrap db values
        self.author = self.guild.get_member(self.db.author_id)
        self.assignees = [self.guild.get_member(assignee_id) for assignee_id in self.db.assignee_ids]
        self.assigned_roles = [self.guild.get_role(role_id) for role_id in self.db.assigned_role_ids]

    async def action(self, user_id, act, reaction_add: bool):
        """Validate payload and run a task action."""
        if self.validate_user(user_id):
            await {
                'complete': self.complete,
                'delete': self.delete
            }[act](reaction_add)

    async def complete(self, checked: bool):
        """Action task complete as checked value."""
        self.use_title(checked)
        await self.message.edit(embed=self.panel)

    async def delete(self, checked=True):
        """Action task delete."""
        if checked:
            await self.message.delete()
            self.db.delete()

    def use_title(self, set=None, index=0):
        """Set and return the current task status based on the title."""
        # Create title tuple
        header = self.panel.title.split()
        title = header[0], " ".join(header[1:])
        # Return status from title
        if set is None:
            return title[index]
        # Update status
        self.panel.title = f"{self.status[set]} {title[1]}"
        return self.use_title(index=index)

    def validate_user(self, user_id):
        """Return whether the user_id has permission to interact with the task."""
        if user_id == self.db.author_id:
            return True
        if user_id in self.db.assignee_ids:
            return True
        if any(role in self.guild.get_member(user_id).roles for role in self.assigned_roles):
            return True
