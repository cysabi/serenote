"""Contains the Task class."""

import discord

from serenote import db


class Task:
    """Task class to handle all the work of managing a task."""

    icons = lambda img: f"https://raw.githubusercontent.com/LeptoFlare/serenote/main/static/{img}.png"
    actions = {
        "complete": 762882665274933248,
        "delete": 762882924592365609
    }

    @classmethod
    async def create_task(cls, channel, author_id, title, description=discord.Embed.Empty):
        """Create a new task and return associated Task object."""
        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blurple())
        cls.set_complete(embed, False)
        # Send task embed
        message = await channel.send(embed=embed)
        # Add actions
        for action in cls.actions.values():
            react = await channel.guild.fetch_emoji(action)
            await message.add_reaction(react)

        # Insert task into database
        db_task = db.Task(message_id=message.id, author_id=author_id)
        db_task.save()

        # Build task object
        return Task(message, db_task)
    
    def __init__(self, message, db):
        self.message = message
        self.db = db
        self.embed = self.message.embeds[0]

    async def action(self, payload, reaction_add: bool):
        """Validate payload and run a task action."""
        if payload.user_id != self.db.author_id:
            return
        await {
            'complete': self.complete,
            'delete': self.delete
        }(reaction_add)

    async def complete(self, checked: bool):
        """Action task complete as checked value."""
        await self.message.edit(embed=self.set_status(self.embed, checked))

    async def delete(self, _=None):
        """Action task delete."""
        await self.message.delete()
        self.db.delete()

    @classmethod
    def set_complete(cls, embed, checked: bool):
        embed.set_author(**{
            False: {"name": "Incomplete Task", "icon_url": cls.icons("unchecked")},
            True: {"name": "Completed Task", "icon_url": cls.icons("checked")},
        }[checked])
        return embed
