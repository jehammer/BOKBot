#!/usr/bin/python3
import random
from discord.ext import commands
from discord import app_commands, Interaction, utils, TextStyle, Embed, Color, Member, Role, User
import logging
import asyncio

# My created imports
import decor as permissions
from errors import *
from modals import *
from models import Roster, Count
from services import Utilities, RosterExtended, EmbedFactory
from database import Librarian
from ui import RosterSelector

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")

roster_map = {}
rosters = {}
limits = []


class Trials(commands.Cog, name="Trials"):
    """Commands related to Trials And Rosters"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_load_on_ready(self, bot):
        global roster_map
        global rosters
        global limits
        fetched = Librarian.get_roster_map(table_config=bot.config['Dynamo']["MapDB"], credentials=bot.config["AWS"])
        if fetched is not None:
            roster_map = fetched
            logging.info(f"Found and Loaded Roster Map")
        else:
            logging.info(f"No Roster Map Found")
        fetched = Librarian.get_all_rosters(table_config=bot.config['Dynamo']["RosterDB"],
                                            credentials=bot.config["AWS"])
        if fetched is not None:
            rosters = fetched
            logging.info(f"Found and Loaded Rosters")
        else:
            logging.info(f"No Rosters Found")
        fetched = RosterExtended.get_limits(table_config=self.bot.config['Dynamo']['ProgDB'],
                                            roles_config=self.bot.config['raids']['ranks'],
                                            creds_config=self.bot.config['AWS'])
        if fetched is not None:
            limits = fetched
            logging.info(f"Found and Loaded Limits")
        else:
            logging.info(f"No Limits Found")

    @commands.Cog.listener()
    async def on_update_rosters_data(self, channel_id, channel_name, update_roster: Roster, method,
                                     interaction: Interaction, user_language):
        global rosters
        global roster_map

        update_roster_db = False
        update_roster_map_db = False
        is_new_roster = False

        channel_id = int(channel_id)

        if method == "create_update":

            if channel_id not in rosters.keys():
                rosters[channel_id] = update_roster
                logging.info(f"Loaded New Roster Into Memory")
                roster_map[str(channel_id)] = channel_name
                logging.info(f"Loaded New Roster Map")
                update_roster_db = True
                update_roster_map_db = True
                is_new_roster = True

            else:

                # Validate if changes are needed or if someone clicked submit but nothing was changed.
                if update_roster.did_values_change(rosters[channel_id]):
                    update_roster_db = True

                # Account for role changes where there is overflow
                if rosters[channel_id].dps_limit > update_roster.dps_limit:
                    to_remove = rosters[channel_id].dps_limit - update_roster.dps_limit
                    # Get the last n items from the main roster
                    reversed_roster = list(rosters[channel_id].dps.items())[-to_remove:]
                    # Remove these items from the main roster
                    for user_id, _ in reversed_roster:
                        del rosters[channel_id].dps[user_id]
                    # Insert these items at the beginning of the backup roster
                    for user_id, msg in reversed(reversed_roster):
                        rosters[channel_id].backup_dps.update({user_id: msg})
                    logging.info(f"Moved overflow DPS to backup")

                if rosters[channel_id].healer_limit > update_roster.healer_limit:
                    to_remove = rosters[channel_id].healer_limit - update_roster.healer_limit
                    # Get the last n items from the main roster
                    reversed_roster = list(rosters[channel_id].healers.items())[-to_remove:]
                    # Remove these items from the main roster
                    for user_id, _ in reversed_roster:
                        del rosters[channel_id].healers[user_id]
                    # Insert these items at the beginning of the backup roster
                    for user_id, msg in reversed(reversed_roster):
                        rosters[channel_id].backup_healers.update({user_id: msg})
                    logging.info(f"Moved overflow Healers to backup")

                if rosters[channel_id].tank_limit > update_roster.tank_limit:
                    to_remove = rosters[channel_id].tank_limit - update_roster.tank_limit
                    # Get the last n items from the main roster
                    reversed_roster = list(rosters[channel_id].tanks.items())[-to_remove:]
                    # Remove these items from the main roster
                    for user_id, _ in reversed_roster:
                        del rosters[channel_id].tanks[user_id]
                    # Insert these items at the beginning of the backup roster
                    for user_id, msg in reversed(reversed_roster):
                        rosters[channel_id].backup_tanks.update({user_id: msg})
                    logging.info(f"Moved overflow Tanks to backup")

                rosters[channel_id].trial = update_roster.trial
                rosters[channel_id].date = update_roster.date
                rosters[channel_id].leader = update_roster.leader
                rosters[channel_id].dps_limit = update_roster.dps_limit
                rosters[channel_id].tank_limit = update_roster.tank_limit
                rosters[channel_id].healer_limit = update_roster.healer_limit
                rosters[channel_id].role_limit = update_roster.role_limit
                rosters[channel_id].memo = update_roster.memo
                logging.info(f"Memory Roster Values Updated")

            if roster_map[str(channel_id)] != channel_name:
                roster_map[str(channel_id)] = channel_name
                update_roster_map_db = True

        elif method == "close":
            del roster_map[str(channel_id)]
            del rosters[str(channel_id)]
            update_roster_map_db = True
            logging.info(f"Roster removed from Map and Roster List.")

        try:
            if update_roster_db:
                try:
                    logging.info(f"Saving Roster to DB")
                    Librarian.put_roster(channel_id, rosters[channel_id].get_roster_data(),
                                         table_config=self.bot.config['Dynamo']["RosterDB"],
                                         credentials=self.bot.config["AWS"])
                    logging.info(f"Saved Roster to DB")

                except Exception as e:
                    await interaction.response.send_message(
                        f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['TrialModify']['DBSaveError'])}")
                    logging.error(f"Roster Save DynamoDB Error: {str(e)}")

            if update_roster_map_db:
                try:
                    logging.info(f"Saving DB Roster Map")
                    Librarian.put_roster_map(data=roster_map,
                                             table_config=self.bot.config['Dynamo']["MapDB"],
                                             credentials=self.bot.config["AWS"])
                    logging.info(f"Updated DB Roster Map")
                except Exception as e:
                    await interaction.response.send_message(
                        f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['TrialModify']['DBSaveError'])}")
                    logging.error(f"Roster Map Save DynamoDB Error: {str(e)}")
        except Exception as e:
            logging.info(f"Error on Saving Roster to DB: {str(e)}")
            alert_channel = self.bot.get_guild(self.bot.config['guild']).get_channel(self.bot.config['private'])
            await alert_channel.send(f"Saving Roster or Map error encountered: {str(e)}")

        if is_new_roster:
            await interaction.response.send_message(
                f"{self.bot.language[user_language]['replies']['TrialModify']['NewRosterCreated'] % channel_name}")
            return

        elif method == "create_update" and not is_new_roster:
            await interaction.response.send_message(
                f"{self.bot.language[user_language]['replies']['TrialModify']['ExistingUpdated'] % channel_name}")
            return

    @commands.Cog.listener()
    async def on_update_limits_data(self):
        global limits
        limits = RosterExtended.get_limits(table_config=self.bot.config['Dynamo']['ProgDB'],
                                           roles_config=self.bot.config['raids']['ranks'],
                                           creds_config=self.bot.config['AWS'])

    @app_commands.command(name='trial', description='For Raid Leads: Opens Trial Creation Modal')
    @permissions.application_has_raid_lead()
    async def create_roster(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_modal(TrialModal(None, interaction, self.bot, user_language, roster_map))

    @app_commands.command(name="modify", description="For Raid Leads: Modify your Trial Roster Details")
    @permissions.application_has_raid_lead()
    async def modify_roster(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_message(
            f"{self.bot.language[user_language]['replies']['SelectRoster']['Select']}",
            view=RosterSelector(interaction, self.bot, interaction.user, "modify",
                                user_language, roster_map, leader=None))

    @app_commands.command(name="close", description="For Raid Leads: Close out a Roster")
    @app_commands.describe(leader="Raid Leader of the Roster being closed")
    @permissions.application_has_raid_lead()
    async def close_roster(self, interaction: Interaction, leader: Member) -> None:
        user_language = Utilities.get_language(interaction.user)

        if self.bot.config["raids"]["lead"] not in leader.roles:
            leader = None

        await interaction.response.send_message(
            f"{self.bot.language[user_language]['replies']['SelectRoster']['Select']}",
            view=RosterSelector(interaction, self.bot, interaction.user, "close",
                                user_language, roster_map, leader))

    @app_commands.command(name='prog', description='For Raid Leads: Sets Prog role information')
    @permissions.application_has_raid_lead()
    async def set_prog_roles(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_modal(
            ProgModal(self.bot, interaction, user_language))

    @commands.command(name='limits')
    @permissions.has_raid_lead()
    async def print_limits(self, ctx: commands.Context):
        """For Raid Leads: Lists Values of Limits for Rosters"""
        user_language = Utilities.get_language(ctx.author)
        try:
            all_limits = f"{self.bot.language[user_language]['replies']['Limits']}\n"

            for i in range(len(limits)):
                if len(limits[i]) == 3:
                    all_limits += f"{i}: {limits[i][0]} | {limits[i][1]} | {limits[i][2]}\n"
                else:
                    all_limits += f"{i}: {limits[i]}\n"
            await ctx.send(all_limits)
        except Exception as e:
            await ctx.send(f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Incomplete'])}")
            logging.error(f"Print Limits Error: {str(e)}")

    @commands.command(name='su', aliases=['signup', 'bu', 'backup'])
    async def add_user_to_roster(self, ctx: commands.Context):
        """Signs you up to a roster | `!su [optional role] [optional message]`"""
        user_language = Utilities.get_language(ctx.author)
        try:
            channel_id = ctx.message.channel.id
            try:
                roster = rosters.get(channel_id)
                if roster is None:
                    await ctx.reply(
                        f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['WrongChannel'])}")
                    return
            except Exception as e:
                await ctx.send("Unable to load raid.")
                logging.error(f"SU Load Raid Error: {str(e)}")
                return

            index = int(roster.role_limit)
            prog_role = False
            if index >= 4:
                prog_role = True

            # Check for an override otherwise fetch default.

            acceptable_roles = ["dps", "tank", "healer", "heals", "heal"]  # TODO: Update this with multi-lingual later.
            healer_roles = ["healer", "heals", "heal"]

            msg = ''
            role = None
            user_id = f"{ctx.author.id}"

            cmd_vals = ctx.message.content.split(" ", 2)
            if len(cmd_vals) > 1 and cmd_vals[1].lower() in acceptable_roles:
                role = cmd_vals[1].lower()
                if len(cmd_vals) > 2:
                    msg = cmd_vals[2]
            elif len(cmd_vals) >= 2:
                if len(cmd_vals) == 2:
                    msg = cmd_vals[1]
                else:
                    msg = cmd_vals[1] + " " + cmd_vals[2]

            if role is None:
                # Check for a default! If there is no default and no role specified then tell the person.
                role = Librarian.get_default(user_id, table_config=self.bot.config['Dynamo']['DefaultDB'],
                                             credentials=self.bot.config['AWS'])
                if role is None:
                    # Role is still none, tell the user there is a problem.
                    await ctx.reply(
                        f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['NoDefault'] % ctx.invoked_with)}")
                    return

            if role in healer_roles:
                role = 'healer'

            allowed = RosterExtended.validate_join_roster(roster_req=index, limits=limits, user=ctx.author,
                                                          roster_role=role)

            if allowed is False and prog_role is False:
                await ctx.reply(f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['replies']['NoRankError'] % (role, self.bot.config['ranks_channel'], index))}")
                return
            elif allowed is False and prog_role is True:
                await ctx.reply(f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['replies']['ProgRoster'])}")
                return

            primary = ['su', 'signup']
            backup = ['bu', 'backup']

            # TODO: Update with multi-lingual support later.
            which = None
            if ctx.invoked_with in primary:
                which = 'su'
            elif ctx.invoked_with in backup:
                which = 'bu'
            else:
                raise UnknownError(f"Unreachable segment not sure how I got here.")

            validation = rosters[channel_id].add_member(user_id=user_id, role=role, msg=msg, which=which)
            if validation == 0:
                await ctx.reply(f"{self.bot.language[user_language]['replies']['Roster']['Added'] % role}")  # Added into roster
            elif validation == 1 and ctx.invoked_with in primary:
                await ctx.reply(
                    f"{self.bot.language[user_language]['replies']['Roster']['Full'] % role}")  # Slots full, added as backup
            elif validation == 1 and ctx.invoked_with in backup:
                await ctx.reply(f"{self.bot.language[user_language]['replies']['Roster']['Backup'] % role}")  # Slots full, added as backup
            elif validation == 2:   # Unable to find role
                await ctx.reply(f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['NoDefault'] % ctx.invoked_with)}")
                return
            else:  # Unreachable
                await ctx.reply(f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Unknown'])}")
                return

            try:
                Librarian.put_roster(channel_id=channel_id, data=rosters[channel_id].get_roster_data(),
                                     table_config=self.bot.config['Dynamo']["RosterDB"],
                                     credentials=self.bot.config["AWS"])
            except Exception as e:
                await ctx.send("I was unable to save the updated roster.")
                logging.error(f"SU Error saving new roster: {str(e)}")
                return
        except (UnknownError, NoDefaultError, NoRoleError) as e:
            raise e
        except Exception as e:
            await ctx.send(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"SUBU Error: {str(e)}")
            return

    @commands.command(name='status')
    async def send_status_embed(self, ctx: commands.Context):
        """Posts the current roster information"""
        user_language = Utilities.get_language(ctx.author)
        try:
            channel_id = ctx.message.channel.id
            try:
                roster_data: Roster = rosters.get(channel_id)
                if roster_data is None:
                    await ctx.send(f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['WrongChannel'])}")
                    return
            except Exception as e:
                await ctx.send("Unable to load raid.")
                logging.error(f"Status Load Raid Error: {str(e)}")
                return

            guild = ctx.message.author.guild
            ui_lang = self.bot.language[user_language]["ui"]

            if isinstance(limits[roster_data.role_limit], list):
                # Need to work with 3 roles to check, dps | tank | healer order
                # TODO: Make the prog roles be gotten if they exist, but for the main limiters consider global permanent variables
                limiter_dps = utils.get(guild.roles, name=limits[roster_data.role_limit][0])
                limiter_tank = utils.get(guild.roles, name=limits[roster_data.role_limit][1])
                limiter_healer = utils.get(guild.roles, name=limits[roster_data.role_limit][2])

                roles_req = f"{limiter_dps.mention} {limiter_tank.mention} {limiter_healer.mention}"
            else:
                limiter = utils.get(guild.roles, name=limits[roster_data.role_limit])
                roles_req = f"{limiter.mention}"

            embed = EmbedFactory.create_status(roster=roster_data, bot=self.bot, language=ui_lang['Status'],
                                               roles_req=roles_req, guild=guild)

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.reply(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"Status Error: {str(e)}")
            return

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
                    Librarian.put_default(user_id=user_id, default=role,
                                          table_config=self.bot.config['Dynamo']['DefaultDB'],
                                          credentials=self.bot.config['AWS'])
                    await ctx.reply(
                        f"{ctx.message.author.display_name}: {self.bot.language[language]['replies']['Default']['Set'] % role}")
                except Exception as e:
                    await ctx.reply(
                        f"{Utilities.format_error(language, self.bot.language[language]['replies']['DBConError'])}")
                    logging.error(f"Default error: {str(e)}")
                    return
            elif role == "check":
                try:
                    default = Librarian.get_default(user_id, table_config=self.bot.config['Dynamo']['DefaultDB'],
                                                    credentials=self.bot.config['AWS'])
                    if default is None:
                        await ctx.reply(
                            f"{ctx.message.author.display_name}: {self.bot.language[language]['replies']['Default']['NoneSet']}")
                    else:
                        await ctx.reply(
                            f"{ctx.message.author.display_name} {self.bot.language[language]['replies']['Default']['Answer']} {default}")
                except Exception as e:
                    await ctx.send(
                        f"{Utilities.format_error(language, self.bot.language[language]['replies']['DBConError'])}")
                    logging.error(f"Default error: {str(e)}")
                    return
            else:
                await ctx.reply(
                    f"{Utilities.format_error(language, self.bot.language[language]['replies']['Default']['BadRoleError'])}")
        except Exception as e:
            await ctx.send(f"{Utilities.format_error(language, self.bot.language[language]['replies']['DBConError'])}")
            logging.error(f"Default Role Set Error: {str(e)}")



async def setup(bot: commands.Bot):
    await bot.add_cog(Trials(bot))
