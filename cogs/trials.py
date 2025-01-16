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
from services import Utilities, RosterExtended, Librarian, EmbedFactory
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
        await interaction.response.send_modal(ProgModal(interaction, self.bot.config, self.bot.language[user_language]))

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
                    limits += f"{i}: {roles[i]}\n"
            await ctx.send(limits)
            await ctx.send(all_limits)
        except Exception as e:
            await ctx.send(f"{self.bot.language[user_language]['Incomplete']}")
            logging.error(f"Print Limits Error: {str(e)}")

            # TODO:
            #   PUT ROSTER JOIN CODE HERE TO ADD USER INTO THE ROSTER

                update_db(channel_id, raid) # TODO: UPDATE TO NEW LIBRARIAN PROCESS AND NEW MULTI-LINGUAL SUPPORT
            except Exception as e:
                return
            await ctx.reply(f"{result}")
        except (UnknownError, NoDefaultError, NoRoleError) as e:
            raise e
        except Exception as e:
            await ctx.send(f"I was was unable to sign you up due to processing errors.")

    @commands.command(name='status')
    async def send_status_embed(self, ctx: commands.Context):
        """Posts the current roster information"""
        user_language = Utilities.get_language(ctx.author)
        try:
            channel_id = ctx.message.channel.id
            try:
                roster_data = Librarian.get_roster(channel_id, table_config=self.bot.config['Dynamo']["RosterDB"],
                                                   credentials=self.bot.config["AWS"])
                if roster_data is None:
                    await ctx.send(f"Sorry! This command only works in a roster channel!")
                    return
            except Exception as e:
                await ctx.send("Unable to load raid.")
                logging.error(f"Status Load Raid Error: {str(e)}")
                return

            guild = ctx.message.author.guild
            ui_lang = self.bot.language[user_language]["ui"]
            roles = RosterExtended.get_limits(table_config=self.bot.config['Dynamo']['ProgDB'],
                                              roles_config=self.bot.config['raids']['ranks'],
                                              creds_config=self.bot.config['AWS'])

            if isinstance(roles[roster_data.role_limit], list):
                # Need to work with 3 roles to check, dps | tank | healer order
                # TODO: Make the prog roles be gotten if they exist, but for the main limiters consider global permanent variables
                limiter_dps = utils.get(guild.roles, name=roles[roster_data.role_limit][0])
                limiter_tank = utils.get(guild.roles, name=roles[roster_data.role_limit][1])
                limiter_healer = utils.get(guild.roles, name=roles[roster_data.role_limit][2])

                roles_req = f"{limiter_dps.mention} {limiter_tank.mention} {limiter_healer.mention}"
            else:
                limiter = utils.get(guild.roles, name=roles[roster_data.role_limit])
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
