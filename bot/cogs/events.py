#!/usr/bin/python3
from discord.ext import commands
from discord import app_commands, Interaction, utils, Member, Role
import logging
import time

# My created imports
from bot import decor as permissions
from bot.errors import *
from bot.modals import *
from bot.models import Roster, Count
from bot.services import Utilities, RosterExtended, EmbedFactory
from bot.ui import RosterSelector

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")

rosters = {}
limits = []
last4z = []
last4t = []


#TODO: Change zone and trial to use the multi-language support by printing each after second language is added.


# Singular function to get random zones
def get_zone_option(cap):
    loop = True
    while loop:
        ran = random.randint(1, cap)
        if ran not in last4z:
            loop = False
    if len(last4z) < 4:
        last4z.append(ran)
    else:
        last4z.pop(0)
        last4z.append(ran)
    return ran - 1


def get_event_option():
    options = ['SSH', 'WBC', 'PDC', 'OL']
    ran = random.randint(1, len(options))
    return options[ran - 1]


# TODO:
#   Create a command to rank someone, if they have the notification tag enabled give them the tier notification tag that they got (T1, T2, T3)
#   And also create a temp mute command that will mute someone in VC for 30 seconds to 5 minutes based on input. Any number 10 and over is seconds otherwise minutes.


class Events(commands.Cog, name="Events"):
    """Commands related to Rosters for Trials, PVP, and other events"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_load_on_ready(self, bot):
        global rosters
        global limits
        fetched = self.bot.librarian.get_all_rosters()
        if fetched is not None:
            rosters = fetched
            logging.info(f"Found and Loaded Rosters")
        else:
            logging.info(f"No Rosters Found")
        fetched = RosterExtended.get_limits(librarian=self.bot.librarian,
                                            roles_config=self.bot.config['raids']['ranks'])
        if fetched is not None:
            limits = fetched
            logging.info(f"Found and Loaded Limits")
        else:
            logging.info(f"No Limits Found")

    @commands.Cog.listener()
    async def on_update_rosters_data(self, channel_id, method, channel_name=None, update_roster: Roster = None,
                                     interaction: Interaction = None, user_language=None, removed=None, people=None,
                                     sort=None):
        global rosters

        update_roster_db = False
        is_new_roster = False

        channel_id = int(channel_id)

        if method == "save_roster":
            update_roster_db = True

        elif method == "create_update":

            if channel_id not in rosters.keys():
                rosters[channel_id] = update_roster
                logging.info(f"Loaded New Roster Into Memory")
                update_roster_db = True
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

        elif method == "close":
            del rosters[channel_id]
            logging.info(f"Roster removed from Roster List.")

        elif method == "remove":
            names = ""
            for i in removed:
                if people[i] in rosters[channel_id].dps.keys() or i in rosters[channel_id].backup_dps.keys():
                    rosters[channel_id].remove_dps(people[i])
                    names += f"{interaction.guild.get_member(int(people[i])).display_name}\n"
                elif (people[i] in rosters[channel_id].healers.keys() or people[i] in
                      rosters[channel_id].backup_healers.keys()):
                    rosters[channel_id].remove_healer(people[i])
                    names += f"{interaction.guild.get_member(int(people[i])).display_name}\n"
                elif (people[i] in rosters[channel_id].tanks.keys() or people[i] in
                      rosters[channel_id].backup_tanks.keys()):
                    rosters[channel_id].remove_tank(people[i])
                    names += f"{interaction.guild.get_member(int(people[i])).display_name}\n"
            await interaction.response.send_message(f"{self.bot.language[user_language]['replies']['Remove']['Removed']
                                                       % (channel_name, names)}")
            update_roster_db = True

        elif method == "fill":
            result = rosters[channel_id].fill_spots()
            if result:
                await interaction.response.send_message(f"{self.bot.language[user_language]['replies']['Fill']['Filled']
                                                           % channel_name}")
                update_roster_db = True
            else:
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Fill']['NotFilled'])}")
                return

        # TODO: On create or modify stop the existing async task for that roster if there is one, and restart with the new timestamp
        #   IF the timestamp changed.
        #   As part of this will need to keep the tasks in an dictionary so they can be accessible in some way.
        try:
            if update_roster_db:
                try:
                    logging.info(f"Saving Roster to DB")
                    self.bot.librarian.put_roster(channel_id, rosters[channel_id].get_roster_data())
                    logging.info(f"Saved Roster to DB")

                except Exception as e:
                    await interaction.response.send_message(
                        f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['TrialModify']['DBSaveError'])}")
                    logging.error(f"Roster Save DynamoDB Error: {str(e)}")

        except Exception as e:
            logging.info(f"Error on Saving Roster to DB: {str(e)}")
            alert_channel = self.bot.get_guild(self.bot.config['guild']).get_channel(self.bot.config['private'])
            await alert_channel.send(f"Saving Roster or Map error encountered: {str(e)}")

        if is_new_roster:
            await interaction.response.send_message(
                f"{self.bot.language[user_language]['replies']['TrialModify']['NewRosterCreated'] % channel_name}")

        elif method == "create_update" and not is_new_roster:
            await interaction.response.send_message(
                f"{self.bot.language[user_language]['replies']['TrialModify']['ExistingUpdated'] % channel_name}")

        if sort:
            try:
                # Order Channels correctly now
                new_positions = RosterExtended.sort_rosters(rosters)
                for i in new_positions:
                    channel = self.bot.get_channel(i)
                    await channel.edit(position=new_positions[i])
                    time.sleep(2)
            except Exception as e:
                logging.error(f"Position Change Error: {str(e)}")
                await interaction.followup.send(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['TrialModify']['CantPosition'])}")
                return
        return

    @commands.Cog.listener()
    async def on_update_limits_data(self):
        global limits
        limits = RosterExtended.get_limits(librarian=self.bot.librarian, roles_config=self.bot.config['raids']['ranks'])

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Event listener for when someone leaves the server to remove them from all rosters they are on."""
        private_channel = member.guild.get_channel(self.bot.config['administration']['private'])
        try:
            was_on = False
            user_id = f"{member.id}"
            to_send = f"{member.name} - {member.display_name} has left the server\n"
            for i in rosters:
                is_on = False
                channel_name = ""
                if user_id in rosters[i].dps.keys():
                    channel_name = self.bot.get_channel(int(i)).name
                    rosters[i].remove_dps(user_id)
                    to_send += f"Traitor was removed as a DPS from {channel_name}\n"
                    was_on = True
                    is_on = True
                elif user_id in rosters[i].backup_dps.keys():
                    channel_name = self.bot.get_channel(int(i)).name
                    rosters[i].remove_dps(user_id)
                    to_send += f"Traitor was removed as a backup DPS from {channel_name}\n"
                    was_on = True
                    is_on = True
                elif user_id in rosters[i].healers.keys():
                    channel_name = self.bot.get_channel(int(i)).name
                    rosters[i].remove_healer(user_id)
                    to_send += f"Traitor was removed as a Healer from {channel_name}\n"
                    was_on = True
                    is_on = True
                elif user_id in rosters[i].backup_healers.keys():
                    channel_name = self.bot.get_channel(int(i)).name
                    rosters[i].remove_healer(user_id)
                    to_send += f"Traitor was removed as a backup Healer from {channel_name}\n"
                    was_on = True
                    is_on = True
                elif user_id in rosters[i].tanks.keys():
                    channel_name = self.bot.get_channel(int(i)).name
                    rosters[i].remove_tank(user_id)
                    to_send += f"Traitor was removed as a Tank from {channel_name}\n"
                    was_on = True
                    is_on = True
                elif user_id in rosters[i].backup_tanks.keys():
                    channel_name = self.bot.get_channel(int(i)).name
                    rosters[i].remove_tank(user_id)
                    to_send += f"Traitor was removed as a backup Tank from {channel_name}\n"
                    was_on = True
                    is_on = True
                if is_on:
                    logging.info(f"Updating Roster {channel_name} for member removal")
                    self.bot.dispatch("update_rosters_data", channel_id=i, method="save_roster")
            if was_on:
                to_send += f"The Traitor has been removed from all active rosters."
            else:
                to_send += f"The Traitor was not on any active rosters."

            await private_channel.send(to_send)
        except Exception as e:
            logging.error(f"User Roster Exit Removal Error: {str(e)}")
            await private_channel.send(f"Unable to remove user on exit from rosters.")

    @app_commands.command(name='trial', description='For Raid Leads: Opens Trial Creation Modal')
    @permissions.application_has_raid_lead()
    @permissions.private_channel_only()
    async def create_roster(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_modal(
            TrialModal(roster=None, interaction=interaction, bot=self.bot, lang=user_language, limits=limits))

    @app_commands.command(name="modify", description="For Raid Leads: Modify your Trial Roster Details")
    @permissions.application_has_raid_lead()
    @permissions.private_channel_only()
    async def modify_roster(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_message(
            f"{self.bot.language[user_language]['replies']['SelectRoster']['Select']}",
            view=RosterSelector(interaction=interaction, bot=self.bot, caller=interaction.user, cmd_called="modify",
                                user_language=user_language, rosters=rosters, limits=limits))

    @app_commands.command(name="close", description="For Raid Leads: Close out a Roster")
    @permissions.application_has_raid_lead()
    @permissions.private_channel_only()
    async def close_roster(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_message(
            f"{self.bot.language[user_language]['replies']['SelectRoster']['Select']}",
            view=RosterSelector(interaction=interaction, bot=self.bot, caller=interaction.user, cmd_called="close",
                                user_language=user_language, rosters=rosters))

    @app_commands.command(name='prog', description='For Raid Leads: Sets Prog role information')
    @permissions.application_has_raid_lead()
    @permissions.private_channel_only()
    async def set_prog_roles(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_modal(
            ProgModal(self.bot, interaction, user_language))

    @app_commands.command(name="runcount", description="For Raid Leads: Increases a rosters members run counts.")
    @permissions.application_has_raid_lead()
    @permissions.private_channel_only()
    async def increase_run_count(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_message(
            f"{self.bot.language[user_language]['replies']['SelectRoster']['Select']}",
            view=RosterSelector(interaction=interaction, bot=self.bot, caller=interaction.user, cmd_called="run_count",
                                user_language=user_language, rosters=rosters))

    @app_commands.command(name="remove", description="For Raid Leads: Remove people from a roster")
    @permissions.application_has_raid_lead()
    @permissions.private_channel_only()
    async def remove_people_from_roster(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_message("Select the roster",
                                                view=RosterSelector(interaction=interaction, bot=self.bot,
                                                                    caller=interaction.user,
                                                                    cmd_called="remove", user_language=user_language,
                                                                    rosters=rosters))

    @app_commands.command(name="fill", description="For Raid Leads: Fill a roster from backup")
    @permissions.application_has_raid_lead()
    @permissions.private_channel_only()
    async def fill_roster(self, interaction: Interaction) -> None:
        user_language = Utilities.get_language(interaction.user)
        await interaction.response.send_message(
            f"{self.bot.language[user_language]['replies']['SelectRoster']['Select']}",
            view=RosterSelector(interaction=interaction, bot=self.bot, caller=interaction.user, cmd_called="fill",
                                user_language=user_language, rosters=rosters))

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
            await ctx.send(
                f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Incomplete'])}")
            logging.error(f"Print Limits Error: {str(e)}")

    @commands.command(name='su', aliases=['signup', 'bu', 'backup'])
    async def add_user_to_roster(self, ctx: commands.Context):
        """Signs you up to a roster | `!su [optional role] [optional message]`"""
        user_language = Utilities.get_language(ctx.author)
        try:

            # Disqualifier check
            if any(self.bot.config['raids']['punish'] in role.name for role in ctx.author.roles):
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Punish'])}")
                return

            channel_id = ctx.message.channel.id
            try:
                if not rosters.get(channel_id):
                    await ctx.reply(
                        f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['WrongChannel'])}")
                    return
            except Exception as e:
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['DBConError'])}")
                logging.error(f"SU Load Raid Error: {str(e)}")
                return

            index = int(rosters[channel_id].role_limit)
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
                role = self.bot.librarian.get_default(user_id)
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
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['NoRankError'] % (role, self.bot.config['ranks_channel'], index))}")
                return
            elif allowed is False and prog_role is True:
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['ProgRoster'])}")
                return

            primary = ['su', 'signup', 'SU', 'SIGNUP']
            backup = ['bu', 'backup', 'BU', 'BACKUP']

            # TODO: Update with multi-lingual support later.
            which = None
            if ctx.invoked_with.lower() in primary:
                which = 'su'
            elif ctx.invoked_with.lower() in backup:
                which = 'bu'
            else:
                raise UnknownError(f"Unreachable segment not sure how I got here. SU/BU used was not a valid option!")

            if len(msg) > 30:
                msg = msg[:30]

            validation = rosters[channel_id].add_member(user_id=user_id, role=role, msg=msg, which=which)
            if validation == 0:
                await ctx.reply(
                    f"{self.bot.language[user_language]['replies']['Roster']['Added'] % role}")  # Added into roster
            elif validation == 1 and ctx.invoked_with in primary:
                await ctx.reply(
                    f"{self.bot.language[user_language]['replies']['Roster']['Full'] % role}")  # Slots full, added as backup
            elif validation == 1 and ctx.invoked_with in backup:
                await ctx.reply(
                    f"{self.bot.language[user_language]['replies']['Roster']['Backup'] % role}")  # Slots full, added as backup
            elif validation == 2:  # Unable to find role
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['NoDefault'] % ctx.invoked_with)}")
                return
            else:  # Unreachable
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Unknown'])}")
                return

            await ctx.author.add_roles(ctx.guild.get_role(rosters[channel_id].pingable))
            self.bot.dispatch("update_rosters_data", channel_id=channel_id, method="save_roster")
        except (UnknownError, NoDefaultError, NoRoleError) as e:
            raise e
        except Exception as e:
            await ctx.send(
                f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Unknown'])}")
            logging.error(f"SUBU Error: {str(e)}")
            return

    @commands.command(name='msg', aliases=['message'])
    async def update_user_message(self, ctx: commands.Context):
        """Update a users message"""
        user_language = Utilities.get_language(ctx.author)
        try:
            channel_id = ctx.message.channel.id
            if not rosters.get(channel_id):
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['WrongChannel'])}")
                return

            msg = ''
            msg_vals = ctx.message.content.split(" ", 2)
            if len(msg_vals) == 2:
                msg = msg_vals[1]
            elif len(msg_vals) > 2:
                msg = f"{msg_vals[1]} {msg_vals[2]}"

            if len(msg) > 30:
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['MsgLength'])}")
                return

            user_id = f"{ctx.author.id}"
            check = rosters[channel_id].update_message(user_id=user_id, new_message=msg)
            if check:
                await ctx.reply(f"{self.bot.language[user_language]['replies']['Roster']['MsgUpdated']}")
            else:
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['NotInRoster'])}")
                return
            self.bot.dispatch("update_rosters_data", channel_id=channel_id, method="save_roster")

        except Exception as e:
            await ctx.send(
                f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Unknown'])}")
            logging.error(f"MSG Error: {str(e)}")
            return

    @commands.command(name='wd', aliases=['withdraw'])
    async def remove_user_from_roster(self, ctx: commands.Context):
        """Removes you from a roster."""
        user_language = Utilities.get_language(ctx.author)
        try:
            channel_id = ctx.message.channel.id
            try:
                if not rosters.get(channel_id):
                    await ctx.reply(
                        f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['WrongChannel'])}")
                    return
            except Exception as e:
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['DBConError'])}")
                logging.error(f"WD Load Raid Error: {str(e)}")
                return

            validation = rosters[channel_id].remove_member(user_id=f"{ctx.author.id}")
            if validation:  # Found and removed from roster
                await ctx.author.remove_roles(ctx.guild.get_role(rosters[channel_id].pingable))
                await ctx.reply(f"{self.bot.language[user_language]['replies']['Roster']['Removed']}")
            elif not validation:  # User not in roster
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['NotInRoster'])}")
                return
            else:  # Unreachable
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Unknown'])}")
                return

            self.bot.dispatch("update_rosters_data", channel_id=channel_id, method="save_roster")
        except (UnknownError, NoDefaultError, NoRoleError) as e:
            raise e
        except Exception as e:
            await ctx.send(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"WD Error: {str(e)}")
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
                    await ctx.send(
                        f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['WrongChannel'])}")
                    return
            except Exception as e:
                await ctx.reply(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['DBConError'])}")
                logging.error(f"Status Load Raid Error: {str(e)}")
                return

            guild = ctx.message.author.guild
            ui_lang = self.bot.language[user_language]["ui"]

            if isinstance(limits[roster_data.role_limit], list):
                # Need to work with 3 roles to check, dps | tank | healer order
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
        # TODO: Make it so this can be deleted with entering Clear or None as possible options
        language = kwargs.get('language')
        try:
            role = role.lower()
            user_id = ctx.message.author.id
            if role.lower() == "heal" or role.lower() == "heals":
                role = "healer"
            if role == "dps" or role == "healer" or role == "tank":
                try:
                    self.bot.librarian.put_default(user_id=user_id, default=role)
                    await ctx.reply(
                        f"{ctx.message.author.display_name}: {self.bot.language[language]['replies']['Default']['Set'] % role}")
                except Exception as e:
                    await ctx.reply(
                        f"{Utilities.format_error(language, self.bot.language[language]['replies']['DBConError'])}")
                    logging.error(f"Default error: {str(e)}")
                    return
            elif role == "check":
                try:
                    default = self.bot.librarian.get_default(user_id)
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

    @commands.command(name="count")
    async def check_own_count(self, ctx: commands.Context):
        """A way for people to check their number of raid runs"""
        user_language = Utilities.get_language(ctx.author)
        try:
            counts: Count = self.bot.librarian.get_count(ctx.author.id)
            if counts is not None:
                embed = EmbedFactory.create_count(counts, self.bot.language[user_language]['ui']['Count'],
                                                  ctx.author.display_name, ctx.guild.name)
                await ctx.reply(embed=embed)
            else:
                await ctx.send(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Count']['NoHistory'])}")
        except Exception as e:
            await ctx.send(
                f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['DBConError'])}")
            logging.error(f"Count check error: {str(e)}")

    @app_commands.command(name='add', description='For Raid Leads: Manually add to roster')
    @app_commands.describe(role='Tank, Healer, or DPS Role to add user into.')
    @app_commands.describe(member='Discord user to add to roster.')
    @permissions.application_has_raid_lead()
    async def add_to_roster(self, interaction: Interaction, role: str, member: Member):
        user_language = Utilities.get_language(interaction.user)
        try:
            channel_id = interaction.channel_id
            if not rosters.get(channel_id):
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['WrongChannel'])}")
                return
            if member.bot is True:
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['ProgLeadRole']['NoBots'])}")
                return

            # Validate the role input
            acceptable_roles = ['dps', 'tank', 'healer']  # TODO: Update with multi-lingual later.
            role = role.lower()

            if role not in acceptable_roles:
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Roster']['AddBad'])}")
                return

            logging.info(f"Add called by {interaction.user.display_name} to add {member.display_name} as {role}")

            validation = rosters[channel_id].add_member(user_id=member.id, role=role, msg='', which='su')
            if validation == 0:
                await interaction.response.send_message(
                    f"{member.display_name}: {self.bot.language[user_language]['replies']['Roster']['Added'] % role}")  # Added into roster
            elif validation == 1:
                await interaction.response.send_message(
                    f"{member.display_name}: {self.bot.language[user_language]['replies']['Roster']['Full'] % role}")  # Slots full, added as backup
                return
            else:  # Unreachable
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Unknown'])}")
                return

            self.bot.dispatch("update_rosters_data", channel_id=channel_id, method="save_roster",
                              user_language=user_language)

        except Exception as e:
            await interaction.response.send_message(
                f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Unknown'])}")
            logging.error(f"Add To Roster Error: {str(e)}")

    @app_commands.command(name="grant-role", description="For Leads: Gives mentioned user a prog role.")
    @app_commands.describe(member="Discord user to grant role to.")
    @app_commands.describe(role="Discord role to grant to the user.")
    @permissions.application_has_prog_lead()
    async def grant_discord_role(self, interaction: Interaction, member: Member, role: Role):
        user_language = Utilities.get_language(interaction.user)
        try:
            if member.bot is True:
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['ProgLeadRole']['NoBots'])}")
                return
            elif interaction.user not in role.members:
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['ProgLeadRole']['NoRole'])}")
                return
            if role.name not in limits:
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['ProgLeadRole']['NotProg'])}")
                return
            logging.info(
                f"Grant Role called by {interaction.user.display_name} to grant {role.name} to {member.display_name}")
            await member.add_roles(role)
            await interaction.response.send_message(
                f"{self.bot.language[user_language]['replies']['ProgLeadRole']['Granted'] % (role.name, member.display_name)}")
        except Exception as e:
            logging.error(f"Grant Role Error: {str(e)}")
            raise e

    @app_commands.command(name="remove-role", description="For Leads: Removes mentioned user a prog role.")
    @app_commands.describe(member="Discord user to remove role from.")
    @app_commands.describe(role="Discord role to remove from user.")
    @permissions.application_has_prog_lead()
    async def remove_discord_role(self, interaction: Interaction, member: Member, role: Role):
        user_language = Utilities.get_language(interaction.user)
        try:
            if member.bot is True:
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['ProgLeadRole']['NoBots'])}")
                return
            elif interaction.user not in role.members:
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['ProgLeadRole']['NoRole'])}")
                return
            if role.name not in limits:
                await interaction.response.send_message(
                    f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['ProgLeadRole']['NotProg'])}")
                return
            logging.info(
                f"Remove Role called by {interaction.user.display_name} to remove {role.name} from {member.display_name}")
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"{self.bot.language[user_language]['replies']['ProgLeadRole']['Removed'] % (role.name, member.display_name)}")
        except Exception as e:
            logging.error(f"Remove Role Error: {str(e)}")
            raise e

    #@app_commands.command(name='rank', description='For Officers: Ranks users')
    #@app_commands.describe(role='Healer, Tanks, or DPS')
    #@app_commands.describe(tier='Number based on which tier they qualify for')
    #@app_commands.describe(member='The Member')
    #@permissions.has_officer()
    #async def add_new_rank(self, interaction: Interaction, role: str, member: Member):
    #    user_language = Utilities.get_language(interaction.user)
    #    try:
    #        pass
    #        # TODO: Fetch the correct rank through the config and apply it to the person. Remove higher ranks if needed.
    #        #   If they have the ping tag, apply the appropriate pings.
    #    except Exception as e:
    #        await interaction.response.send_message(
    #            f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['Unknown'])}")
    #        logging.error(f"Add To Roster Error: {str(e)}")

    @commands.command(name="event")
    async def random_event(self, ctx: commands.Context):
        """Gives you a random event and zone to do"""
        user_language = Utilities.get_language(ctx.author)
        try:
            options = self.bot.language[user_language]['replies']['Zones']
            ran = get_zone_option(len(options))
            event = get_event_option()
            await ctx.send(f"{self.bot.language[user_language]['replies']['Events'][event]} {options[ran]}")
        except Exception as e:
            await ctx.reply(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"Get Event Error: {str(e)}")

    @commands.command(name="zone")
    async def random_zone(self, ctx: commands.Context):
        """Gives you a random zone to do for your event"""
        """Gives you a random normal trial to do"""
        user_language = Utilities.get_language(ctx.author)
        try:
            options = self.bot.language[user_language]['replies']['Zones']
            ran = get_zone_option(len(options))
            await ctx.send(f"{options[ran]}")
        except Exception as e:
            await ctx.reply(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"Get Zone Error: {str(e)}")

    # Get a trial randomly chosen
    @commands.command(name="ntrial", aliases=['vtrial', 'hmtrial'])
    async def generate_trial_to_run(self, ctx: commands.Context):
        """Gives you a random trial to do"""
        user_language = Utilities.get_language(ctx.author)
        try:
            options = self.bot.language[user_language]['replies']['Trials']
            loop = True
            ran = 0
            while loop:
                ran = random.randint(1, cap)
                if ran not in last4t:
                    loop = False
            if len(last4t) < 4:
                last4t.append(ran)
            else:
                last4t.pop(0)
                last4t.append(ran)
            ran = ran-1
            if ctx.invoked_with == 'ntrial':
                await ctx.send(f"{self.bot.language[user_language]['replies']['Events']['Norm']} {options[ran]}")
            elif ctx.invoked_with == 'vtrial':
                await ctx.send(f"{self.bot.language[user_language]['replies']['Events']['Vet']} {options[ran]}")
            elif ctx.invoked_with == 'hmtrial':
                await ctx.send(
                    f"{self.bot.language[user_language]['replies']['Events']['Vet']} {options[ran]} {self.bot.language[user_language]['replies']['Events']['HM']}")
        except Exception as e:
            await ctx.reply(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"Generate Random Trial Error: {str(e)}")

    # Creator-Only commands

    @commands.command(name="roster")
    @permissions.creator_only()
    async def printout_roster(self, ctx: commands.Context, channel_id):
        """Printout a roster directly for any debugging needs"""
        try:
            await ctx.reply(rosters[str(channel_id)].get_roster_data())
        except Exception as e:
            await ctx.reply(f"Unable to complete: {str(e)}")

    @commands.command(name="allrosters")
    @permissions.creator_only()
    async def printout_all_rosters(self, ctx: commands.Context):
        """Printout all rosters directly for any debugging needs"""
        try:
            for i in rosters:
                await ctx.reply(rosters[i].get_roster_data())
        except Exception as e:
            await ctx.reply(f"Unable to complete: {str(e)}")

    @commands.command(name="saverosters")
    @permissions.creator_only()
    async def save_roster_info(self, ctx: commands.Context):
        """Force Save current Roster Map and Rosters"""
        try:
            for i in rosters:
                self.bot.librarian.put_roster(i, rosters[i].get_roster_data())
            await ctx.reply(f"Rosters saved.")

        except Exception as e:
            await ctx.reply(f"Unable to complete: {str(e)}")

    @commands.command(name="reloadrosters")
    @permissions.creator_only()
    async def reload_roster_info(self, ctx: commands.Context):
        """Force Reload all Roster information"""
        try:
            logging.info("Force Reload Roster Information Called")
            global rosters

            fetched = self.bot.librarian.get_all_rosters()
            if fetched is not None:
                rosters = fetched
                logging.info(f"Found and Loaded Rosters")
            await ctx.reply(f"Roster Information Reloaded.")
        except Exception as e:
            await ctx.reply(f"Unable to complete: {str(e)}")

    @commands.command(name="resort")
    @permissions.creator_only()
    async def force_resort_rosters(self, ctx: commands.Context):
        """Force all Rosters to be sorted again."""
        try:
            new_positions = RosterExtended.sort_rosters(rosters)
            for i in new_positions:
                channel = self.bot.get_channel(i)
                await channel.edit(position=new_positions[i])
                time.sleep(2)
            await ctx.reply(f"Finished Sorting!")
        except Exception as e:
            await ctx.reply(f"Unable to complete: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
