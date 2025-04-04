from discord.ext import commands
from discord import app_commands


class IODBError(Exception):
    pass


class DiscordError(Exception):
    pass


class UserError(Exception):
    pass


class NoDefaultError(commands.CommandError):
    pass


class DefaultIOError(Exception):
    pass


class UnknownError(commands.CommandError):
    pass


class NoRoleError(commands.CommandError):
    pass


class BotUserError(Exception):
    pass


class NotPrivateError(app_commands.AppCommandError):
    pass
