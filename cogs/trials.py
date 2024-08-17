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
from models import Roster, Count
from services import Utilities, RosterExtended, Librarian
from ui import RosterSelector

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")

roster_map = {}

class Trials(commands.Cog, name="Trials"):
    """Commands related to Trials And Rosters"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_load_on_ready(self, bot):
        global roster_map
        fetched = Librarian.get_roster_map(table_config=bot.config['Dynamo']["MapDB"], credentials=bot.config["AWS"])
        if fetched is not None:
            roster_map = fetched
        logging.info(f"Loaded Roster Map")

    @commands.Cog.listener()
    async def on_reload_roster_map(self, new_roster_map):
        global roster_map
        roster_map = new_roster_map
        logging.info(f"Loaded New Roster Map")

    @app_commands.command(name='trial', description='For Raid Leads: Opens Trial Creation Modal')
    @permissions.application_has_raid_lead()
    async def create_roster(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_modal(TrialModal(None, interaction, self.bot, user_language, roster_map))

    @app_commands.command(name="modify", description="For Raid Leads: Modify your Trial Roster Details")
    @permissions.application_has_raid_lead()
    async def modify_roster(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_message(f"{self.bot.language[user_language]['replies']['SelectRoster']['Select']}",
                                                view=RosterSelector(interaction, self.bot, interaction.user,"modify",
                                                                    user_language, roster_map))

    @app_commands.command(name="close", description="For Raid Leads: Close out a Roster")
    @permissions.application_has_raid_lead()
    async def close_roster(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_message(f"{self.bot.language[user_language]['replies']['SelectRoster']['Select']}",
                                                view=RosterSelector(interaction, self.bot, interaction.user,"close",
                                                                    user_language, roster_map))

    @app_commands.command(name='prog', description='For Raid Leads: Sets Prog role information')
    @permissions.application_has_raid_lead()
    async def set_prog_roles(self, interaction: Interaction) -> None:
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

    @commands.command(name='trial',
                      aliases=['date', 'datetime', 'time', 'leader', 'change', 'rolenum', 'memo', 'limit', 'call', 'modify',
                               'fill', 'close', 'runcount', 'remove', 'add'],
                      hidden=True)
    async def old_commands_alert(self, ctx: commands.Context):
        user_language = Utilities.get_language(ctx.author)
        now_modify = ['date', 'datetime', 'time', 'leader', 'change', 'rolenum', 'memo', 'limit']
        if ctx.invoked_with in now_modify:
            new_command = 'modify'
        else:
            new_command = ctx.invoked_with
        await ctx.reply(f"{self.bot.language[user_language]['replies']['MovedAnswer'] % new_command}")

    @commands.command(name="default")
    @permissions.language()
    async def set_default_role(self, ctx: commands.Context, role="check", **kwargs):
        """Set or check your default for rosters | `!default [optional: role]`"""
        # TODO: Make Role mapper for this from the supported languages to dps, healer, or tank
        language = kwargs.get('language')
        try:
            role = role.lower()
            user_id = ctx.message.author.id
            if role.lower() == "heal" or role.lower() == "heals":
                role = "healer"
            if role == "dps" or role == "healer" or role == "tank":
                try:
                    Librarian.put_default(user_id=user_id, default=role,  table_config=self.bot.config['Dynamo']['DefaultDB'],
                                          credentials=self.bot.config['AWS'])
                    await ctx.reply(f"{ctx.message.author.display_name}: {self.bot.language[language]['replies']['Default']['Set'] % role}")
                except Exception as e:
                    await ctx.reply(f"{Utilities.format_error(language, self.bot.language[language]['replies']['DBConError'])}")
                    logging.error(f"Default error: {str(e)}")
                    return
            elif role == "check":
                try:
                    default = Librarian.get_default(user_id, table_config=self.bot.config['Dynamo']['DefaultDB'],
                                          credentials=self.bot.config['AWS'])
                    if default is None:
                        await ctx.reply(f"{ctx.message.author.display_name}: {self.bot.language[language]['replies']['Default']['NoneSet']}")
                    else:
                        await ctx.reply(f"{ctx.message.author.display_name} {self.bot.language[language]['replies']['Default']['Answer']} {default}")
                except Exception as e:
                    await ctx.send(f"{Utilities.format_error(language, self.bot.language[language]['replies']['DBConError'])}")
                    logging.error(f"Default error: {str(e)}")
                    return
            else:
                await ctx.reply(f"{Utilities.format_error(language, self.bot.language[language]['replies']['Default']['BadRoleError'])}")
        except Exception as e:
            await ctx.send(f"{Utilities.format_error(language, self.bot.language[language]['replies']['DBConError'])}")
            logging.error(f"Default Role Set Error: {str(e)}")



async def setup(bot: commands.Bot):
    await bot.add_cog(Trials(bot))