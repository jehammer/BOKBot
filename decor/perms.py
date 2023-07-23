import discord
from discord.ext import commands
from discord import app_commands
from functools import wraps


def has_officer():
    """A decorator that validates if someone has the officer role"""
    def decorator(original_function):
        @wraps(original_function)
        async def wrapper_function(*args, **kwargs):
            ctx = args[1]
            self = args[0]
            officer_role = discord.utils.get(ctx.guild.roles, name=self.bot.config["roles"]["admin"])
            if officer_role in ctx.author.roles:
                return await original_function(*args, **kwargs)
            else:
                raise commands.MissingRole(str(officer_role))
        return wrapper_function
    return decorator


def has_raid_lead():
    """A decorator that validates if someone has the raid lead role"""
    def decorator(original_function):
        @wraps(original_function)
        async def wrapper_function(*args, **kwargs):
            ctx = args[1]
            self = args[0]
            raid_lead = discord.utils.get(ctx.guild.roles, name=self.bot.config["raids"]["lead"])
            if raid_lead in ctx.author.roles:
                return await original_function(*args, **kwargs)
            else:
                raise commands.MissingRole(str(raid_lead))
        return wrapper_function
    return decorator

def application_has_raid_lead():
    """A decorator that validates if someone has the raid lead role"""
    def decorator(original_function):
        @wraps(original_function)
        async def wrapper_function(*args, **kwargs):
            interaction = args[1]
            self = args[0]
            raid_lead = discord.utils.get(interaction.guild.roles, name=self.bot.config["raids"]["lead"])
            if raid_lead in interaction.user.roles:
                return await original_function(*args, **kwargs)
            else:
                raise app_commands.MissingRole(str(raid_lead))
        return wrapper_function
    return decorator

def creator_only():
    """A decorator that checks if bot creator is the one calling the command"""
    def decorator(original_function):
        @wraps(original_function)
        async def wrapper_function(*args, **kwargs):
            ctx = args[1]
            self = args[0]
            creator_id = self.bot.config["creator"]
            if creator_id == ctx.author.id:
                return await original_function(*args, **kwargs)
            else:
                raise commands.NotOwner
        return wrapper_function
    return decorator
