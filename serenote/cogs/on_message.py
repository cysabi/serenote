from contextlib import contextmanager

import discord
from discord.ext import commands


class OnMessage(commands.Cog):
    """Holds on_message listener."""

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, client, message):
        """When a new message is sent."""
        if any({
            self.locked(client, message),
            self.override_commands(client, message),
        }):
            return

        if (ctx := await client.get_context(message)).command is None and not ctx.invoked_with:
            return

        with self.lock_command_access(client, message):
            await client.process_commands(message)

    def locked(self, client, message):
        """Check if the user has been command-locked."""
        if getattr(client, 'ongoing_commands', False) is not False:
            return message.author.id in client.ongoing_commands[message.channel.id]
        return True

    def override_commands(self, client, message):
        """Check if the user wants to send a message without it being seen by the bot."""
        if message.content.startswith("\\"):
            return True
        return None

    @contextmanager
    def lock_command_access(self, client, message):
        """Make sure the user can't call another command while in the middle of one."""
        try:
            client.ongoing_commands[message.channel.id].add(message.author.id)
            yield
        finally:
            client.ongoing_commands[message.channel.id].remove(message.author.id)


def setup(bot):
    bot.add_cog(OnMessage(bot))
