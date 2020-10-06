"""Contains HelpCommand class."""

import discord
from discord.ext import commands


class HelpCommand(commands.DefaultHelpCommand):
    """Set up help command for the bot."""

    EMBED_COLOR = 0x7289DA

    async def send_bot_help(self, mapping):
        """Send bot command page."""
        embed = self.create_embed(
            title=f"`{self.clean_prefix}help`",
            fields=[{
                "name": cog.qualified_name if cog else '\u200B',
                "value": "\n".join([
                    self.short(command)
                    for command in await self.filter_commands(cog_commands)
                ])} for cog, cog_commands in mapping.items() if cog_commands][::-1]
        )
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        """Send cog command page."""
        embed = self.create_embed(
            title=cog.qualified_name.capitalize(),
            description=cog.description,
            **({"fields": [{
                "name": f"{cog.qualified_name.capitalize()} Commands:",
                "value": "\n".join([
                    self.short(command)
                    for command in cog.get_commands()])
            }]} if cog.get_commands() else {}))

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        """Send command group page."""
        embed = self.create_embed(
            title=self.short(group, False),
            description=group.help,
            fields=[{
                "name": f"Subcommands:",
                "value": "\n".join([
                    self.short(command)
                    for command in await self.filter_commands(group.commands)
                ])
            }]
        )
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        """Send command page."""
        sig = self.get_command_signature(command)
        embed = self.create_embed(
            title=f"`{sig[:-1] if sig.endswith(' ') else sig}`",
            description=command.help,
        )
        await self.get_destination().send(embed=embed)

    def command_not_found(self, string):
        """Returns message when command is not found."""
        return f"Command {self.short(string, False)} does not exist."

    async def subcommand_not_found(self, command, string):
        """Returns message when subcommand is not found."""
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f"Command {self.short(command, False)} has no subcommand named `{string}`."
        else:
            return f"Command {self.short(command, False)} has no subcommands."

    async def send_error_message(self, error):
        """Send error message, override to support sending embeds."""
        await self.get_destination().send(
            embed=discord.Embed(title="Command/Subcommand not found.", description=error, color=self.EMBED_COLOR))

    def create_embed(self, fields: list = (), **kwargs):
        """Create help embed."""
        embed = discord.Embed(color=self.EMBED_COLOR, **kwargs)
        for field in fields:
            embed.add_field(**field, inline=False)
        embed.set_footer(
            text=f"Type {self.clean_prefix}help command for more info on a command. You can also type {self.clean_prefix}help category for more info on a category.")
        return embed

    def short(self, command, doc=True):
        """List the command as a one-liner."""
        return f'`{self.clean_prefix}{command}` {(command.short_doc if doc else "")}'
