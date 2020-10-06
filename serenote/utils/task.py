"""Contains the Task class."""

import discord


class Task:
    """Custom task."""

    EMBED_COLOR = 0x7289DA
    def __init__(self, ctx):
        """Initilize task and declare self variables."""
        self.ctx = ctx
        self.reply_task = None
        self.actions = {
            "complete": '✅',
            "delete": '❌',
        }

    async def __new__(cls, ctx, title: str, description: str = discord.Embed.Empty, channel=None):
        """Use async to create embed and passive task on class creation."""
        self = super().__new__(cls)
        self.__init__(ctx)

        # Create and send task embed
        embed = discord.Embed(title=title, description=description, color=0x7289DA)
        embed.set_author(name="To-do", icon_url="https://media.discordapp.net/attachments/757710892317278279/762880963218243584/Empty_Group.png")
        dest = channel if channel else ctx.channel
        self.message = await dest.send(embed=embed)

        # Wait for task action
        for action in self.actions.values():
            await self.message.add_reaction(action)
        reaction, _ = await self.ctx.bot.wait_for('reaction_add', check=self.event_check(valids=set(self.actions.values())))
        await self.message.clear_reactions()

        # Deal with reaction
        if reaction.emoji == self.actions['complete']:
            embed.set_author(name="Complete!", icon_url="https://media.discordapp.net/attachments/757710892317278279/762880965445025792/Check_Empty_Group.png")
            await self.message.edit(embed=embed)
        elif reaction.emoji == self.actions['delete']:
            await self.message.delete()

        return self

    def event_check(self, valids: set):
        return lambda r, u: \
            (r.message.id, u.id) == (self.message.id, self.ctx.author.id) and \
            (r.emoji in valids)
