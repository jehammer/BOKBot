from bot.services import Utilities
from functools import wraps
from discord.ext import commands
from bot.errors import BotUserError, NotPrivateError


def language():
    """Decorator to get set language for a function"""

    def decorator(original_function):
        @wraps(original_function)
        async def wrapper_function(*args, **kwargs):
            ctx = args[1]
            kwargs['language'] = Utilities.get_language(ctx.author)
            return await original_function(*args, **kwargs)

        return wrapper_function

    return decorator


def No_Bots():
    """Decorator that checks if a user is a Discord Bot User"""

    def decorator(original_function):
        @wraps(original_function)
        async def wrapper_function(*args, **kwargs):
            ctx: commands.Context = args[1]
            if ctx.author.bot:
                raise BotUserError
            return await original_function(*args, **kwargs)

        return wrapper_function

    return decorator


def private_channel_only():
    """Decorator that checks if the app command was called within the dedicated private channel."""

    def decorator(original_function):
        @wraps(original_function)
        async def wrapper_function(*args, **kwargs):
            interaction = args[1]
            self = args[0]
            if interaction.channel.id == self.bot.config['private']:
                return await original_function(*args, **kwargs)
            else:
                lang = Utilities.get_language(interaction.user)
                raise NotPrivateError(self.bot.language[lang]['replies']['NotPrivate'])

        return wrapper_function

    return decorator

#
# KWARGS DO NOT WORK WITH APPLICATION COMMANDS, will need to review.
#
#def app_language():
#    """Decorator to get set language for an application command function"""
#    def decorator(original_function):
#        @wraps(original_function)
#        async def wrapper_function(*args, **kwargs):
#            self = args[0]
#            interaction = args[1]
#            args[1].language = Utilities.get_language(interaction.user)
#            return await original_function(*args, **kwargs)
#        return wrapper_function
#    return decorator
