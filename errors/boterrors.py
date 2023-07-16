from discord.ext import commands

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