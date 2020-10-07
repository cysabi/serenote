"""Holds the custom Bot subclass."""

import logging

import discord
from discord.ext import commands

from . import utils


class Bot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help_command = utils.HelpCommand()

    async def on_ready(self):
        logging.info("Logged in as: %s", self.user.name)

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.MissingRequiredArgument):
            await context.send(embed=utils.Panel(
                type="Error",
                type_icon=utils.Panel.icons("error"),
                title="Missing Required Argument",
                description=exception.args[0],
            ))
        else:
            raise exception
