"""Contains the Alert class."""

from typing import Optional

import discord


class Alert:
    """Custom polished alerts."""

    class Style:
        """Alert styles and their colors."""
        SUCCESS = 0x78b354
        DANGER = 0xdd2e44
        WARNING = 0xffcc4d
        INFO = 0x3b88c3

    def __init__(self, ctx, style: Style, *, title: str, description: str = discord.Embed.Empty):
        """Create alert embed."""
        self.ctx = ctx
        self.embed: discord.Embed = self.create_embed(style, title, description)
        self.alert: Optional[discord.Message] = None

    async def __new__(cls, *args, **kwargs):
        """Create message on class creation using async."""
        self = super().__new__(cls)
        self.__init__(*args, **kwargs)

        self.alert = await self.ctx.send(embed=self.embed)
        return self

    @classmethod
    def create_embed(cls, style, title: str, description: str = discord.Embed.Empty) -> discord.Embed:
        """Create alert embed."""
        emoji_key = {
            cls.Style.SUCCESS: ':white_check_mark:',
            cls.Style.DANGER:  ':no_entry_sign:',
            cls.Style.WARNING: ':warning:',
            cls.Style.INFO:    ':information_source:',
        }
        title_key = {
            cls.Style.SUCCESS: lambda t: f' {emoji_key[style]} Success: **{t}**',
            cls.Style.DANGER:  lambda t: f' {emoji_key[style]} Error: **{t}**',
            cls.Style.WARNING: lambda t: f' {emoji_key[style]} Warning: **{t}**',
            cls.Style.INFO:    lambda t: f' {emoji_key[style]} Info: **{t}**',
        }
        return discord.Embed(title=title_key[style](title), description=description, color=style)

    async def delete(self) -> None:
        """Remove alert."""
        if self.alert:
            await self.alert.delete()
            self.alert = None
