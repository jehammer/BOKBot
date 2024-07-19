from services import Utilities
from functools import wraps
from discord.ext import commands
from errors import BotUserError

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