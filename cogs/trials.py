#!/usr/bin/python3
import random
from discord.ext import commands
from discord import app_commands, Interaction
import logging
import asyncio


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


#TODO: Replace and remove this import for more specific ones
import discord

class Trials(commands.Cog, name="Trials"):
    """Commands related to Trials And Rosters"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(Trials(bot))