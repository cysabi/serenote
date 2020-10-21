"""Contains the Task class."""

import discord

from serenote import utils, db


class Task:
    """Task class to handle all the work of managing a task."""

    actions = {
        "complete": 762882665274933248,
        "delete": 763192427732926465,
    }

    @classmethod
    async def create(cls, ctx, title, description=discord.Embed.Empty, **kwargs):
        """Create a new task and return associated Task object."""
        # Create task panel
        panel = cls.create_panel(ctx, title, description, **kwargs)
        message = await ctx.send(embed=panel)  # Send panel embed
        # Add actions
        for action in cls.actions.values():
            react = ctx.bot.get_emoji(action)
            await message.add_reaction(react)
        # Insert task into database
        db_task = db.Task(
            message_id=message.id,
            channel_id=message.channel.id,
            author_id=ctx.author.id,
            assignee_ids=kwargs['assignees'][0],
            assigned_role_ids=kwargs['assignees'][1]
        )
        db_task.save()
        # Build task object
        return Task(message)
    
    @classmethod
    def create_panel(cls, ctx, title, description, **kwargs):
        """Create task panel."""
        # Get task panel type
        task_panel_type = cls.get_type(False)
        # Add panel meta
        panel_meta = {}
        panel_meta["Assignees"] = cls.get_assignees(ctx, kwargs['assignees'])  # display assignees meta
        # Return panel object
        return utils.Panel(
            **task_panel_type,
            meta=panel_meta,
            title=title,
            description=description)

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

    async def action(self, payload, reaction_add: bool):
        """Validate payload and run a task action."""
        if self.validate_user(payload.user_id):
            await {
                'complete': self.complete,
                'delete': self.delete
            }[payload.emoji.name](reaction_add)

    def validate_user(self, user_id):
        """Return whether the user_id has permission to interact with the task."""
        if user_id == self.db.author_id:
            return True
        if user_id in self.db.assignee_ids:
            return True
        if any(role in self.guild.get_member(user_id).roles for role in self.assigned_roles):
            return True

    async def complete(self, checked: bool):
        """Action task complete as checked value."""
        self.panel.set_type(**self.get_type(checked))
        await self.message.edit(embed=self.panel)

    async def delete(self, checked=True):
        """Action task delete."""
        if checked:
            await self.message.delete()
            self.db.delete()

    @classmethod
    def get_type(cls, complete):
        """Get task panel type, based on complete status."""
        return {
            False: {"type": "Task", "type_icon": utils.Panel.icons("unchecked")},
            True: {"type": "Task", "type_icon": utils.Panel.icons("checked")},
        }[complete]

    @staticmethod
    def get_assignees(ctx, ids) -> list:
        """Return a list of all role and user objects that are assignees."""
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
