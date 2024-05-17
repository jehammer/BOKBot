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

    @commands.command(name='limits')
    @permissions.has_raid_lead()
    async def print_limits(self, ctx: commands.Context):
        """For Raid Leads: Lists Values of Limits for Rosters"""
        try:
            user_language = Utilities.get_language(ctx.author)
            limits = f"{self.bot.language[user_language]['replies']['Limits']}\n"

            roles = RosterExtended.get_limits(table_config=self.bot.config['Dynamo']['ProgDB'],
                                              roles_config=self.bot.config['raids']['roles'],
                                              creds_config=self.bot.config['AWS'])
            for i in range(len(roles)):
                if len(roles[i]) == 3:
                    limits += f"{i}: {roles[i][0]} | {roles[i][1]} | {roles[i][2]}\n"
                else:
                    limits += f"{i}: {roles[i]}\n"
            await ctx.send(limits)
        except Exception as e:
            await ctx.send(f"I was unable to print the limits")
            logging.error(f"Print Limits Error: {str(e)}")


    @commands.command(name="pin", aliases=["unpin"])
    @permissions.has_raid_lead()
    async def pin_message(self, ctx: commands.Context):
        """For Raid Leads: Allows pinning of a message"""
        user_language = Utilities.get_language(ctx.author)
        try:
            ref = ctx.message.reference
            if ref is not None:
                # Is a reply - pin or unpin the reply message
                message = await ctx.fetch_message(ref.message_id)
                if message.pinned is True:
                    await message.unpin()
                    await ctx.reply(f"{self.bot.language[user_language]['replies']['Pin']['Unpinned']}")
                    return
                else:
                    await message.pin()
                    return
            else:
                # Is not a reply - pin the command message
                await ctx.message.pin()
                return
        except Exception as e:
            await ctx.reply(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"Pin Error: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Trials(bot))