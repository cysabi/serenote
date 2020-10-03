"""Holds the custom Bot subclass."""

import logging

import discord
from discord.ext import commands, tasks

import ui
from . import utils


class Bot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help_command = utils.HelpCommand()

    async def on_ready(self):
        logging.info("Logged in as: %s", self.user.name)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ui.Alert(ctx, ui.Alert.Style.DANGER,
                title="Missing Required Argument",
                description=f"You can use `{ctx.prefix}help {ctx.command.qualified_name}` for help.")
        elif isinstance(error, (commands.errors.CommandNotFound, commands.errors.TooManyArguments)):
            await ui.Alert(ctx, ui.Alert.Style.DANGER,
                title="Unknown Command",
                description=f"You can use `{ctx.prefix}help` for help.")
        if isinstance(getattr(error, 'original', None), ui.exc.CommandCancel):
            return
        else:
            logging.error(error)
            raise error
