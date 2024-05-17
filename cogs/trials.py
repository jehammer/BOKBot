#!/usr/bin/python3
import random
from discord.ext import commands
from discord import app_commands, Interaction
import logging
import asyncio

# My created imports
import decor as permissions
from errors import *
from modals import *
from models import roster, count
from services import Utilities, RosterExtended



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


    @app_commands.command(name='trial', description='For Raid Leads: Opens Trial Creation Modal')
    @permissions.application_has_raid_lead()
    async def create_roster(self, interaction: discord.Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_modal(TrialModal(None, interaction, self.bot.config, self.bot.language[user_language]))


    @app_commands.command(name='prog', description='For Raid Leads: Sets Prog role information')
    @permissions.application_has_raid_lead()
    async def set_prog_roles(self, interaction: discord.Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_modal(ProgModal(interaction, self.bot.config, self.bot.language[user_language]))

async def setup(bot: commands.Bot):
    await bot.add_cog(Trials(bot))