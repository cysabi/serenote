"""Contains the Task class."""

import discord

from serenote import db


class Task:
    """Task class to handle all the work of managing a task."""

    icons = lambda img: f"https://raw.githubusercontent.com/LeptoFlare/serenote/main/static/{img}.png"
    actions = {
        "complete": 762882665274933248,
        "delete": 763192427732926465,
    }

    @classmethod
    async def create_task(cls, ctx, title, description=discord.Embed.Empty, **kwargs):
        """Create a new task and return associated Task object."""
        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blurple())
        cls.set_complete(embed, False)
        # Send task embed
        message = await ctx.send(embed=embed)
        # Add actions
        for action in cls.actions.values():
            react = ctx.bot.get_emoji(action)
            await message.add_reaction(react)

        # Insert task into database
        db_task = db.Task(
            message_id=message.id,
            author_id=ctx.author.id,
            assignee_ids=kwargs['assignees'][0],
            assigned_role_ids=kwargs['assignees'][1]
        )
        db_task.save()

        # Build task object
        return Task(message)
    
    def __init__(self, message):
        self.message = message
        self.db = db.get_task(message.id)
        # Wrap message values
        self.guild = self.message.channel.guild
        self.embed = self.message.embeds[0]
        # Wrap db values
        self.author = self.guild.get_member(self.db.author_id)
        print(self.author)
        self.assignees = [self.guild.get_member(assignee_id) for assignee_id in self.db.assignee_ids]
        self.assigned_roles = [self.guild.get_role(role_id) for role_id in self.db.assigned_role_ids]

    async def action(self, payload, reaction_add: bool):
        """Validate payload and run a task action."""
        if self.validate_user(payload.user_id):
            await {
                'complete': self.complete,
                'delete': self.delete
            }[payload.emoji.name](reaction_add)

    async def complete(self, checked: bool):
        """Action task complete as checked value."""
        await self.message.edit(embed=self.set_complete(self.embed, checked))

    async def delete(self, _=None):
        """Action task delete."""
        await self.message.delete()
        self.db.delete()

    def validate_user(self, user_id):
        """Return whether the user_id has permission to interact with the task."""
        if user_id == self.db.author_id:
            return True
        if user_id in self.db.assignee_ids:
            return True
        if any(role in self.guild.get_member(user_id).roles for role in self.assigned_roles):
            return True

    @classmethod
    def set_complete(cls, embed, checked: bool):
        embed.set_author(**{
            False: {"name": "Incomplete Task", "icon_url": cls.icons("unchecked")},
            True: {"name": "Completed Task", "icon_url": cls.icons("checked")},
        }[checked])
        return embed
