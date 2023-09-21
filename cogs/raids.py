import datetime
import time
import random
import re
import discord
from discord.ext import commands
from discord import ui, app_commands
import logging
from pytz import timezone
from enum import Enum
from pymongo import MongoClient
import decor.perms as permissions
from errors.boterrors import *

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")

# Global variables for the MongoDB channels, set by set_channels function
global raids
global count
global defaults

#DATE_TEMPLATE = "<t:{date}:f>" # DATE_TEMPLATE.format(date=raid.date)
class Role(Enum):
    DPS = "dps"
    HEALER = "healer"
    TANK = "tank"
    NONE = "none"


# There are a lot of instances were the DB is updated rather than created, so I made a function for that to save lines.
def update_db(channel_id, raid):
    try:
        logging.info(f"Updating Roster channelID: {channel_id}")
        new_rec = {'$set': {'data': raid.get_data()}}
        raids.update_one({'channelID': channel_id}, new_rec)
        logging.info(f"Roster channelID: {channel_id} - {raid.raid} updated")
    except Exception as e:
        logging.error(f"Save to DB Error: {str(e)}")
        raise IODBError(f"Unable to save to DB")


def get_raid(channel_id):
    """Loads raid information from a database or returns None if there is none"""
    try:
        rec = raids.find_one({'channelID': channel_id})
        if rec is None:
            return None
        raid = Raid(rec['data']['raid'], rec['data']['date'], rec['data']['leader'],
                    rec['data']['dps'],
                    rec['data']['healers'], rec['data']['tanks'],
                    rec['data']['backup_dps'],
                    rec['data']['backup_healers'], rec['data']['backup_tanks'],
                    rec['data']['dps_limit'],
                    rec['data']['healer_limit'], rec['data']['tank_limit'],
                    rec['data']['role_limit'], rec['data']['memo'])
        return raid
    except Exception as e:
        logging.error(f"Load Raid Error: {str(e)}")
        raise IODBError(f"Unable to load Raid from DB")


def update_runs(raid, num=1):
    """Updates the number of runs for people in the raid roster"""
    for i in raid.dps:
        counts = count.find_one({'userID': int(i)})
        if counts is None:
            new_data = {
                "userID": int(i),
                "raidCount": num,
                "lastRaid": raid.raid,
                "lastDate": raid.date,
                "dpsRuns": num,
                "tankRuns": 0,
                "healerRuns": 0
            }
            try:
                count.insert_one(new_data)
            except Exception as e:
                logging.error(f"Update Count Increase Error: {str(e)}")
                raise IODBError("Unable to update runs info")  # Will automatically return from here
        else:
            counts["raidCount"] += num
            counts["lastRaid"] = raid.raid
            counts["lastDate"] = raid.date
            counts["dpsRuns"] += num
            try:
                new_rec = {'$set': counts}
                count.update_one({'userID': int(i)}, new_rec)
            except Exception as e:
                logging.error(f"Update Count Increase Error: {str(e)}")
                raise IODBError("Unable to update runs info")
    for i in raid.healers:
        counts = count.find_one({'userID': int(i)})
        if counts is None:
            new_data = {
                "userID": int(i),
                "raidCount": num,
                "lastRaid": raid.raid,
                "lastDate": raid.date,
                "dpsRuns": 0,
                "tankRuns": 0,
                "healerRuns": num
            }
            try:
                count.insert_one(new_data)
            except Exception as e:
                logging.error(f"Update Count Increase Error: {str(e)}")
                raise IODBError("Unable to update runs info")
        else:
            counts["raidCount"] += num
            counts["lastRaid"] = raid.raid
            counts["lastDate"] = raid.date
            counts["healerRuns"] += num
            try:
                new_rec = {'$set': counts}
                count.update_one({'userID': int(i)}, new_rec)
            except Exception as e:
                logging.error(f"Update Count Error: {str(e)}")
                raise IODBError("Unable to update runs info")
    for i in raid.tanks:
        counts = count.find_one({'userID': int(i)})
        if counts is None:
            new_data = {
                "userID": int(i),
                "raidCount": num,
                "lastRaid": raid.raid,
                "lastDate": raid.date,
                "dpsRuns": 0,
                "tankRuns": num,
                "healerRuns": 0
            }
            try:
                count.insert_one(new_data)
            except Exception as e:
                logging.error(f"Update Count Increase Error: {str(e)}")
                raise IODBError("Unable to update runs info")
        else:
            counts["raidCount"] += num
            counts["lastRaid"] = raid.raid
            counts["lastDate"] = raid.date
            counts["tankRuns"] += num
            try:
                new_rec = {'$set': counts}
                count.update_one({'userID': int(i)}, new_rec)
            except Exception as e:
                logging.error(f"Update Count Error: {str(e)}")
                raise IODBError("Unable to update runs info")

def set_channels(config):
    """Function to set the MongoDB information on cog load"""
    global raids
    global count
    global defaults
    client = MongoClient(config['mongo'])
    database = client['bot']  # Or do it with client.PyTest, accessing collections works the same way.
    raids = database.raids
    count = database.count
    defaults = database.defaults


def suffix(d):
    try:
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')
    except Exception as e:
        logging.error(f"Suffix Failure: {str(e)}")
        raise ValueError("Unable to set suffix value")

def setup_roster_join_information(og_cmd, user: discord.User, raid):
    """Function to handle people joining a roster"""

    use_msg = False
    slotted = Role.NONE
    msg = ""
    og_msg = ""
    use_default = True
    acceptable_roles = ["dps", "tank", "healer", "heals", "heal"]

    cmd_vals = og_cmd.split(" ", 2)
    if len(cmd_vals) > 1 and cmd_vals[1].lower() in acceptable_roles:
        use_default = False
        if len(cmd_vals) > 2:
            use_msg = True
            msg = cmd_vals[2]
    elif len(cmd_vals) >= 2:
        use_msg = True
        if len(cmd_vals) == 2:
            msg = cmd_vals[1]
        else:
            msg = cmd_vals[1] + " " + cmd_vals[2]
    user_id = user.id

    default_error_msg = f"You have no default set, please specify a role (ex: `{cmd_vals[0].lower()} dps`) or set a default "\
                        f"(ex: `!default dps`) then sign up again."

    # Role handling
    selected_role = None
    if use_default is True:
        default = defaults.find_one({'userID': user_id})
        if default is None:
            raise NoDefaultError(default_error_msg)
        selected_role = default['default']
    elif use_default is False:
        selected_role = cmd_vals[1].lower()
    if selected_role == "dps":
        role = Role.DPS
    elif selected_role == "tank":
        role = Role.TANK
    elif selected_role == "heal" or selected_role == "heals" or selected_role == "healer":
        role = Role.HEALER
    else:
        raise NoDefaultError(default_error_msg)

    user_id = str(user_id)

    # Check if the user swapped their role
    if user_id in raid.dps.keys():
        og_msg = raid.dps.get(user_id)
        slotted = Role.DPS
        raid.remove_dps(user_id)

    elif user_id in raid.backup_dps.keys():
        og_msg = raid.backup_dps.get(user_id)
        raid.remove_dps(user_id)
        slotted = Role.DPS

    elif user_id in raid.healers.keys():
        og_msg = raid.healers.get(user_id)
        raid.remove_healer(user_id)
        slotted = Role.HEALER

    elif user_id in raid.backup_healers.keys():
        og_msg = raid.backup_healers.get(user_id)
        raid.remove_healer(user_id)
        slotted = Role.HEALER

    elif user_id in raid.tanks.keys():
        og_msg = raid.tanks.get(user_id)
        raid.remove_tank(user_id)
        slotted = Role.TANK

    elif user_id in raid.backup_tanks.keys():
        og_msg = raid.backup_tanks.get(user_id)
        raid.remove_tank(user_id)
        slotted = Role.TANK

    # Determine if user is doing su or bu (assume su first)
    issu = True
    if cmd_vals[0].lower() == "!bu":
        issu = False

    # Check that the user is switching between two roles or re-signing up with the same role
    if slotted != Role.NONE and og_msg != "" and use_msg is False and slotted == role:
        msg = og_msg

    if issu is True:
        if role == Role.DPS:
            result = raid.add_dps(user_id, msg)
        elif role == Role.TANK:
            result = raid.add_tank(user_id, msg)
        elif role == Role.HEALER:
            result = raid.add_healer(user_id, msg)
        else:
            raise UnknownError(f"Roster Setup Unknown Error: ISSU TRUE ELSE REACHED INPUTS = {og_cmd} FROM {user.display_name}")
    elif issu is False:
        if role == Role.DPS:
            result = raid.add_backup_dps(user_id, msg)
        elif role == Role.TANK:
            result = raid.add_backup_tank(user_id, msg)
        elif role == Role.HEALER:
            result = raid.add_backup_healer(user_id, msg)
        else:
            raise UnknownError(f"Roster Setup Unknown Error: ISSU FALSE ELSE REACHED INPUTS = {og_cmd} FROM {user.display_name}")
    else:
        raise UnknownError(f"Roster Setup Unknown Error: ISSU TRUE OR FALSE ELSE REACHED INPUTS = {og_cmd} FROM {user.display_name}")

    return result, raid

def generate_channel_name(date, raid_name, tz_info):
    """Function to generate channel names on changed information"""
    date = date.strip()
    if date.upper() == "ASAP":
        new_name = f"{raid_name}-ASAP"
        return new_name

    new_time = datetime.datetime.utcfromtimestamp(int(re.sub('[^0-9]', '', date)))
    tz = new_time.replace(tzinfo=datetime.timezone.utc).astimezone(
        tz=timezone(tz_info))
    weekday = tz.strftime("%a")
    day = tz.day
    new_name = f"{raid_name}-{weekday}-{str(day)}{suffix(day)}"
    return new_name


def format_date(date):
    """Formats the timestamp date to the correct version"""
    date = date.strip()
    if date.upper() == "ASAP":
        return date.upper()

    formatted_date = f"<t:{re.sub('[^0-9]', '', date)}:f>"
    return formatted_date


class Raid:
    """Class for handling roster and related information"""

    def __init__(self, raid, date, leader, dps={}, healers={}, tanks={}, backup_dps={}, backup_healers={},
                 backup_tanks={}, dps_limit=0, healer_limit=0, tank_limit=0, role_limit=0, memo="delete"):
        self.raid = raid
        self.date = date
        self.leader = leader
        self.dps = dps
        self.tanks = tanks
        self.healers = healers
        self.backup_dps = backup_dps
        self.backup_tanks = backup_tanks
        self.backup_healers = backup_healers
        self.dps_limit = dps_limit
        self.tank_limit = tank_limit
        self.healer_limit = healer_limit
        self.role_limit = role_limit
        self.memo = memo

    def get_data(self):
        all_data = {
            "raid": self.raid,
            "date": self.date,
            "leader": self.leader,
            "dps": self.dps,
            "healers": self.healers,
            "tanks": self.tanks,
            "backup_dps": self.backup_dps,
            "backup_healers": self.backup_healers,
            "backup_tanks": self.backup_tanks,
            "dps_limit": self.dps_limit,
            "healer_limit": self.healer_limit,
            "tank_limit": self.tank_limit,
            "role_limit": self.role_limit,
            "memo": self.memo
        }
        return all_data

    # Add people into the right spots
    def add_dps(self, n_dps, p_class=""):
        if len(self.dps) < self.dps_limit:
            self.dps[n_dps] = p_class
            return "Added as DPS"
        else:
            self.backup_dps[n_dps] = p_class
            return "DPS spots full, slotted for Backup"

    def add_healer(self, n_healer, p_class=""):
        if len(self.healers) < self.healer_limit:
            self.healers[n_healer] = p_class
            return "Added as Healer"
        else:
            self.backup_healers[n_healer] = p_class
            return "Healer spots full, slotted for Backup"

    def add_tank(self, n_tank, p_class=""):
        if len(self.tanks) < self.tank_limit:
            self.tanks[n_tank] = p_class
            return "Added as Tank"
        else:
            self.backup_tanks[n_tank] = p_class
            return "Tank spots full, slotted for Backup"

    def add_backup_dps(self, n_dps, p_class=""):
        self.backup_dps[n_dps] = p_class
        return "Added for backup as DPS"

    def add_backup_healer(self, n_healer, p_class=""):
        self.backup_healers[n_healer] = p_class
        return "Added for backup as Healer"

    def add_backup_tank(self, n_tank, p_class=""):
        self.backup_tanks[n_tank] = p_class
        return "Added for backup as Tank"

    # remove people from right spots
    def remove_dps(self, n_dps):
        if n_dps in self.dps:
            del self.dps[n_dps]
        else:
            del self.backup_dps[n_dps]

    def remove_healer(self, n_healer):
        if n_healer in self.healers:
            del self.healers[n_healer]
        else:
            del self.backup_healers[n_healer]

    def remove_tank(self, n_tank):
        if n_tank in self.tanks:
            del self.tanks[n_tank]
        else:
            del self.backup_tanks[n_tank]

    def change_role_limit(self, new_role_limit):
        self.role_limit = new_role_limit

    def change_dps_limit(self, new_dps_limit):
        self.dps_limit = new_dps_limit

    def change_healer_limit(self, new_healer_limit):
        self.healer_limit = new_healer_limit

    def change_tank_limit(self, new_tank_limit):
        self.tank_limit = new_tank_limit

    def fill_spots(self, num):
        try:
            loop = True
            while loop:
                if len(self.dps) < self.dps_limit and len(self.backup_dps) > 0:
                    first = list(self.backup_dps.keys())[0]
                    self.dps[first] = self.backup_dps.get(first)
                    del self.backup_dps[first]
                else:
                    loop = False
            loop = True
            while loop:
                if len(self.healers) < self.healer_limit and len(self.backup_healers) > 0:
                    first = list(self.backup_healers.keys())[0]
                    self.healers[first] = self.backup_healers.get(first)
                    del self.backup_healers[first]
                else:
                    loop = False
            loop = True
            while loop:
                if len(self.tanks) < self.tank_limit and len(self.backup_tanks) > 0:
                    first = list(self.backup_tanks.keys())[0]
                    self.tanks[first] = self.backup_tanks.get(first)
                    del self.backup_tanks[first]
                else:
                    loop = False
            logging.info(f"Spots filled in raid id {str(num)}")
        except Exception as e:
            logging.error(f"Fill Spots error: {str(e)}")

class RosterSelect(discord.ui.Select):
    def __init__(self, interaction: discord.Interaction, config, cmd_called):
        self.channels = {}
        self.config = config
        self.cmd_called = cmd_called
        rosters = raids.distinct("channelID")
        options = []
        for i in rosters:
            channel = interaction.guild.get_channel(i)
            if channel is not None:
                name = channel.name
                if name in self.channels.keys():
                    rand = random.randint(1000,9999)
                    name += f"-{str(rand)}"
                options.append(discord.SelectOption(label=name))
                self.channels[name] = i
            else:
                options.append(discord.SelectOption(label=i))
                self.channels[str(i)] = i

        #discord.SelectOption(label="Option 1",emoji="👌",description="This is option 1!"),
        super().__init__(placeholder="Select the roster you wish to use",max_values=1,min_values=1,options=options)

    def update_options_timeout(self):
        # Remove all options and set the placeholder to "Timed out"
        self.options = []
        self.placeholder = "Timed out"

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        raid = get_raid(self.channels[selected])
        if self.cmd_called == "modify":
            await interaction.response.send_modal(TrialModal(raid, interaction, self.config, self.channels[selected]))
        elif self.cmd_called == "call":
            await interaction.response.send_modal(CallModal(raid, interaction, self.config, self.channels[selected]))
        elif self.cmd_called == "close":
            await interaction.response.send_modal(CloseModal(raid, interaction, self.config, self.channels[selected]))
        elif self.cmd_called == "remove":
            await interaction.response.send_modal(RemoveModal(raid, interaction, self.config, self.channels[selected]))
        elif self.cmd_called == "run_count":
            await interaction.response.send_modal(RunCountModal(raid, interaction, self.config, self.channels[selected]))
        elif self.cmd_called == "fill":
            await interaction.response.send_modal(FillModal(raid, interaction, self.config, self.channels[selected]))

class RosterSelectView(discord.ui.View):
    def __init__(self,interaction: discord.Interaction, bot, caller, cmd_called, *, timeout = 30):
        super().__init__(timeout=timeout)
        self.caller = caller
        self.bot = bot
        self.interaction = interaction
        self.new_roster_select = RosterSelect(interaction, bot.config, cmd_called)
        self.add_item(self.new_roster_select)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.caller.id:
            await interaction.response.send_message(f"You need to be the caller of the command to interact with it.", ephemeral=True)
            return False
        return True
    async def on_timeout(self):
        self.new_roster_select.update_options_timeout()
        self.clear_items()
        self.stop()


class TrialModal(discord.ui.Modal):
    def __init__(self, raid: Raid, interaction: discord.Interaction, config, channel=None ):
        self.config = config
        self.leader_trial_val = None
        self.date_val = None
        self.limit_val = None
        self.role_nums_val = "8,2,2"
        self.memo_val = "None"
        self.new_roster = True
        self.map_dict = {
            self.config["raids"]["roles"]["base"]: 0,
            self.config["raids"]["roles"]["first"]: 1,
            self.config["raids"]["roles"]["second"]: 2,
            self.config["raids"]["roles"]["third"]: 3,
            self.config["raids"]["roles"]["fourth"]: 4,
            0: self.config["raids"]["roles"]["base"],
            1: self.config["raids"]["roles"]["first"],
            2: self.config["raids"]["roles"]["second"],
            3: self.config["raids"]["roles"]["third"],
            4: self.config["raids"]["roles"]["fourth"]
        }
        if raid is not None:
            mapped_limit = self.map_dict[raid.role_limit]
            self.channel= channel
            self.new_roster = False
            self.raid = raid
            self.leader_trial_val = f"{raid.leader},{raid.raid}"
            self.date_val = f"{raid.date}"
            self.limit_val = f"{mapped_limit}"
            self.role_nums_val = f"{raid.dps_limit},{raid.healer_limit},{raid.tank_limit}"
            self.memo_val = f"{raid.memo}"
        super().__init__(title='Trial Manager')
        self.initialize()

    def initialize(self):
        # Add all the items here based on what is above
        self.leader_trial =  discord.ui.TextInput(
            label='Raid Lead and Trial',
            placeholder='Format: Raid Lead, Trial',
            default = self.leader_trial_val,
            required=True
        )
        self.date = discord.ui.TextInput(
            label="Date",
            placeholder="Put Timestamp here",
            default = self.date_val,
            required=True
        )
        self.limit = discord.ui.TextInput(
            label="Role Limit",
            placeholder="Put Role Limit here",
            default=self.limit_val,
            required=True,
        )
        self.role_nums = discord.ui.TextInput(
            label="DPS/Healer/Tank Role Nums",
            default=self.role_nums_val,
            required=True
        )
        self.memo = discord.ui.TextInput(
            label="Memo",
            default=self.memo_val,
            placeholder="Type None if you do not want a memo.",
            style=discord.TextStyle.long,
            required=True
        )
        self.add_item(self.leader_trial)
        self.add_item(self.date)
        self.add_item(self.limit)
        self.add_item(self.role_nums)
        self.add_item(self.memo)

    async def on_submit(self, interaction: discord.Interaction):
        # Split the values:
        try:
            role_limit = int(self.limit.value)
            if role_limit < 0 or role_limit > 4:
                await interaction.response.send_message(f"Invalid input, the Role Limit must be between 0 and 4")
                return
            mapped_limit = self.map_dict[role_limit]
        except (NameError, ValueError):
            await interaction.response.send_message(f"Invalid input: Role Limit should be a number. Check with `!limits`\n"
                                                    f"You entered: `{self.limit.value}`")
            return
        try:
            leader, raid = self.leader_trial.value.split(",")
        except (NameError, ValueError):
            await interaction.response.send_message(f"Invalid input: Leader and Trial should look like this: `Leader, Trial`\n"
                                                    f"You entered: `{self.leader_trial.value}`")
            return
        try:
            dps_limit, healer_limit, tank_limit = self.role_nums.value.split(",")
        except (NameError, ValueError):
            await interaction.response.send_message(f"Invalid input: The Role Numbers should be put in order of DPS, Healer, and Tank "
                                                    f"and look like: `8,2,2` for example.\n"
                                                    f"You entered: `{self.role_nums.value}`")
            return
        try:
            dps_limit = int(dps_limit.strip())
        except ValueError:
            await interaction.response.send_message(f"Invalid input: DPS limit should be a number, ex: `8`\n"
                                                    f"You entered: `{dps_limit}`")
            return
        try:
            healer_limit = int(healer_limit.strip())
        except ValueError:
            await interaction.response.send_message(f"Invalid input: Healer limit should be a number, ex: `2`\n"
                                                    f"You entered: `{dps_limit}`")
            return
        try:
            tank_limit = int(tank_limit.strip())
        except ValueError:
            await interaction.response.send_message(f"Invalid input: Tank limit should be a number, ex: `2`\n"
                                                    f"You entered: `{dps_limit}`")
            return
        formatted_date = format_date(self.date.value)

        category = interaction.guild.get_channel(self.config["raids"]["category"])

        def get_sort_key(current_channels):
            current_raid = get_raid(current_channels.id)
            new_position = 0
            if current_raid is None:
                return current_channels.position  # Keep the channel's position unchanged
            elif current_raid.date == "ASAP":
                return 100
            else:
                # Calculate new positioning
                new_time = datetime.datetime.utcfromtimestamp(int(re.sub('[^0-9]', '', current_raid.date)))
                tz = new_time.replace(tzinfo=datetime.timezone.utc).astimezone(
                    tz=timezone(self.config["raids"]["timezone"]))
                day = tz.day
                if day < 10:
                    day = int(f"0{str(day)}")
                weight = int(f"{str(tz.month)}{str(day)}{str(tz.year)}")
            return weight

        if self.new_roster is False:
            # Update all values then update the DB
            self.raid.raid = raid
            self.raid.leader = leader
            self.raid.dps_limit = dps_limit
            self.raid.healer_limit = healer_limit
            self.raid.tank_limit = tank_limit
            self.raid.date = formatted_date
            self.raid.memo = self.memo.value
            self.raid.role_limit = mapped_limit

            try:
                new_name = generate_channel_name(formatted_date, raid, self.config["raids"]["timezone"])
                update_db(self.channel, self.raid)
                modify_channel = interaction.guild.get_channel(int(self.channel))
                await modify_channel.edit(name=new_name)
                await interaction.response.send_message(f"Roster {new_name} and Channel updated.")
            except ValueError:
                await interaction.response.send_message(f"Invalid input, was the Date not formatted right?")
                return


        elif self.new_roster is True:
            def factory(fact_leader, fact_raid, fact_date, fact_dps_limit, fact_healer_limit, fact_tank_limit,
                        fact_role_limit, fact_memo, config):
                if fact_dps_limit is None and fact_healer_limit is None and fact_tank_limit is None:
                    fact_dps_limit = config["raids"]["roster_defaults"]["dps"]
                    fact_healer_limit = config["raids"]["roster_defaults"]["healers"]
                    fact_tank_limit = config["raids"]["roster_defaults"]["tanks"]
                fact_role_limit = self.map_dict[fact_role_limit]
                dps, healers, tanks, backup_dps, backup_healers, backup_tanks = {}, {}, {}, {}, {}, {}
                return Raid(fact_raid, fact_date, fact_leader, dps, healers, tanks, backup_dps, backup_healers,
                            backup_tanks, fact_dps_limit, fact_healer_limit, fact_tank_limit, fact_role_limit,
                            fact_memo)
            try:
                created = factory(leader, raid, formatted_date, dps_limit, healer_limit, tank_limit, role_limit, self.memo.value, self.config)

                logging.info(f"Creating new channel.")
                try:
                    new_name = generate_channel_name(created.date, created.raid, self.config["raids"]["timezone"])
                except ValueError:
                    await interaction.response.send_message(f"Invalid input, was the Date formatted correctly?")
                    return
                channel = await category.create_text_channel(new_name)
                limiter = discord.utils.get(interaction.user.guild.roles, name=created.role_limit)
                embed = discord.Embed(
                    title=f"{created.raid} {created.date}",
                    description=f"Role Required: {limiter.mention}\n\nI hope people sign up for this.",
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Remember to spay or neuter your support!\nAnd mention your sets!")
                embed.set_author(name="Raid Lead: " + leader)
                embed.add_field(name="Calling Healers!", value='To Heal Us!', inline=False)
                embed.add_field(name="Calling Tanks!", value='To Be Stronk!', inline=False)
                embed.add_field(name="Calling DPS!", value='To Stand In Stupid!', inline=False)

                if created.memo != "None":
                    embed_memo = discord.Embed(
                        title=" ",
                        color=discord.Color.dark_gray()
                    )
                    embed_memo.add_field(name=" ", value=created.memo, inline=True)
                    embed_memo.set_footer(text="This is very important!")
                    await channel.send(embed=embed_memo)
                await channel.send(embed=embed)
                logging.info(f"Created Channel: channelID: {str(channel.id)}")
            except Exception as e:
                await interaction.response.send_message(
                    f"Error in creating category channel and sending embed. Please make sure all your inputs are correct.")
                logging.error(f"Raid Creation Channel And Embed Error: {str(e)}")
                return

            # Save raid info to MongoDB
            try:
                logging.info(f"Saving Roster channelID: {str(channel.id)}")
                rec = {
                    'channelID': channel.id,
                    'data': created.get_data()
                }
                raids.insert_one(rec)
                logging.info(f"Saved Roster channelID: {str(channel.id)}")
            except Exception as e:
                await interaction.response.send_message("Error in saving information to MongoDB, roster was not saved.")
                logging.error(f"Raid Creation MongoDB Error: {str(e)}")
                return
            await interaction.response.send_message(f"Created Roster and Channel {channel.name}")
        else:
            await interaction.response.send_message(f"Hey uh, you reached an unreachable part of the code lol.")

        # Refresh category
        category = interaction.guild.get_channel(self.config["raids"]["category"])

        # Sort channels
        for i in category.text_channels:
            i.position = get_sort_key(i)

        for i in category.text_channels:
            if i.position >= 100: # Fix the rate_limit so only adjust channels we want to adjust
                await i.edit(position=i.position)
                time.sleep(1)
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'I was unable to complete the command. Logs have more detail.')
        logging.error(f"Trial Creation/Modify Error: {str(error)}")
        return

class CallModal(discord.ui.Modal):
    def __init__(self, raid: Raid, interaction: discord.Interaction, config, channel=None ):
        self.config = config
        self.channel_id = channel
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        self.raid = raid
        super().__init__(title='Call Roster')
        self.initialize()
    def initialize(self):
        # Add all the items here based on what is above
        self.call = discord.ui.TextInput(
            label=f"Message to send to {self.channel.name}",
            placeholder="Just click cancel if you want to cancel.",
            style=discord.TextStyle.long,
            required=True
        )
        self.add_item(self.call)

    async def on_submit(self, interaction: discord.Interaction):
        names = "\nHealers \n"
        for i in self.raid.healers:
            for j in interaction.guild.members:
                if int(i) == j.id:
                    names += j.mention + "\n"
        if len(self.raid.healers) == 0:
            names += "None " + "\n"

        names += "\nTanks \n"
        for i in self.raid.tanks:
            for j in interaction.guild.members:
                if int(i) == j.id:
                    names += j.mention + "\n"
        if len(self.raid.tanks) == 0:
            names += "None" + "\n"
        names += "\nDPS \n"
        for i in self.raid.dps:
            for j in interaction.guild.members:
                if int(i) == j.id:
                    names += j.mention + "\n"
        if len(self.raid.dps) == 0:
            names += "None" + "\n"
        await self.channel.send(f"A MESSAGE FOR:\n{names}\n{self.call.value}")
        await interaction.response.send_message(f"{self.channel.name} Message sent.")
        return
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'I was unable to complete the command. Logs have more detail.')
        logging.error(f"Roster Call Error: {str(error)}")
        return


class CloseModal(discord.ui.Modal):
    def __init__(self, raid: Raid, interaction: discord.Interaction, config, channel=None ):
        self.config = config
        self.channel_id = channel
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        if self.channel is None:
            self.name = self.channel_id
        else:
            self.name = self.channel.name
        self.raid = raid
        super().__init__(title='Close Roster')
        self.initialize()
    def initialize(self):
        # Add all the items here based on what is above
        self.confirm = discord.ui.TextInput(
            label=f"Close {self.name}",
            placeholder="Y or N? Click cancel to close this",
            style=discord.TextStyle.short,
            required=True
        )
        self.runs = discord.ui.TextInput(
            label=f"Increase Run Count?",
            placeholder="Y or N? Click cancel to close this",
            style=discord.TextStyle.short,
            required=True
        )
        self.runscount = discord.ui.TextInput(
            label=f"If Yes enter number of runs",
            placeholder="I mean it defaults to 1...",
            default="1",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.confirm)
        self.add_item(self.runs)
        self.add_item(self.runscount)

    async def on_submit(self, interaction: discord.Interaction):
        confirm_value = self.confirm.value.strip().lower()
        runs_inc = self.runs.value.strip().lower()
        if confirm_value != "n" and confirm_value != "y" and runs_inc != "n" and runs_inc != "y":
            await interaction.response.send_message(f"You must enter a `y` or an `n` in the Confirmation fields")
            return
        if confirm_value != "y":
            await interaction.response.send_message(f"Wait why did you do that instead of just clicking cancel?")
            return
        runs_increased = "Runs not increased"
        if runs_inc == "y":
            try:
                inc_val = int(self.runscount.value)
                update_runs(self.raid, inc_val)
                runs_increased = "Runs increased"
            except ValueError:
                await interaction.response.send_message(f"Runs Count Increase must be a number only.")
                return
        to_delete = {"channelID": self.channel_id}
        raids.delete_one(to_delete)
        if self.channel is not None:
            await self.channel.delete()
        await interaction.response.send_message(f"Roster {self.name} Closed and {runs_increased}")

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'I was unable to complete the command. Logs have more detail.')
        logging.error(f"Roster Close Error: {str(error)}")
        return

class FillModal(discord.ui.Modal):
    def __init__(self, raid: Raid, interaction: discord.Interaction, config, channel=None ):
        self.config = config
        self.channel_id = channel
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        self.raid = raid
        super().__init__(title='Fill Roster')
        self.initialize()
    def initialize(self):
        # Add all the items here based on what is above
        self.confirm = discord.ui.TextInput(
            label=f"Fill {self.channel.name}",
            placeholder="Y or N? Click cancel to close this",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.confirm)

    async def on_submit(self, interaction: discord.Interaction):
        val = self.confirm.value.strip().lower()
        if val != 'y' and val != 'n':
            await interaction.response.send_message(f"Only `y` or `n` input is allowed for this.")
            return
        if val != "y":
            await interaction.response.send_message(f"Wait why did you do that instead of just clicking cancel?")
            return
        self.raid.fill_spots(self.channel_id)
        update_db(self.channel_id, self.raid)
        await interaction.response.send_message(f"{self.channel.name} Roles filled")

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'I was unable to complete the command. Logs have more detail.')
        logging.error(f"Roster Fill Error: {str(error)}")
        return

class RunCountModal(discord.ui.Modal):
    def __init__(self, raid: Raid, interaction: discord.Interaction, config, channel=None ):
        self.config = config
        self.channel_id = channel
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        self.raid = raid
        super().__init__(title='Update Run Count')
        self.initialize()
    def initialize(self):
        # Add all the items here based on what is above
        self.num = discord.ui.TextInput(
            label=f"Number of runs for {self.channel.name}",
            default = "1",
            placeholder="Just click cancel if you want to cancel.",
            style=discord.TextStyle.short,
            required=True
        )
        self.date = discord.ui.TextInput(
            label=f"New Date for {self.channel.name}",
            placeholder="put an `n` (no quotes) if you don't want to change it.",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.num)
        self.add_item(self.date)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = int(self.num.value)
        except ValueError:
            await interaction.response.send_message(f"Run Count Increase must be an integer value.")
            return
        update_runs(self.raid, val)
        if self.date.value.strip().lower() != "n":
                try:
                    formatted_date = format_date(self.date.value)
                    self.raid.date = formatted_date
                    update_db(self.channel_id, self.raid)
                    new_name = generate_channel_name(self.raid.date, self.raid.raid,
                                                     self.config["raids"]["timezone"])
                    await self.channel.edit(name=new_name)
                    await interaction.response.send_message(f"{self.channel.name} Runs and Date updated")
                    return
                except ValueError:
                    await interaction.response.send_message(f"Invalid input, you gave me letters when I expected numbers.")
                    return
        await interaction.response.send_message(f"{self.channel.name} Runs updated")
        return

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'I was unable to complete the command. Logs have more detail.')
        logging.error(f"Run Count Error: {str(error)}")
        return

class RemoveModal(discord.ui.Modal):
    def __init__(self, raid: Raid, interaction: discord.Interaction, config, channel=None ):
        self.config = config
        self.channel_id = channel
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        self.raid = raid
        self.roster = []
        super().__init__(title='Remove From Roster')
        self.initialize(interaction)
    def initialize(self, interaction):
        counter = 1
        total = ""
        # Print out everyone and put them in a list to get from
        for i in self.raid.dps.keys():
            self.roster.append(i)
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        for i in self.raid.healers.keys():
            self.roster.append(i)
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        for i in self.raid.tanks.keys():
            self.roster.append(i)
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        for i in self.raid.backup_dps.keys():
            self.roster.append(i)
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        for i in self.raid.backup_healers.keys():
            self.roster.append(i)
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        for i in self.raid.backup_tanks.keys():
            self.roster.append(i)
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        self.users = discord.ui.TextInput(
            label=f"{self.channel.name}",
            default=f"{total}",
            style=discord.TextStyle.long,
            required=False
        )
        self.options = discord.ui.TextInput(
            label=f" ",
            placeholder="Enter your choices as a comma for multiple ex: 1,5,12",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.users)
        self.add_item(self.options)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            to_remove = [int(i)-1 for i in self.options.value.split(',')]
            to_remove_keys = []
            names = ""
            for i in range(len(self.roster)):
                if i in to_remove:
                    to_remove_keys.append(self.roster[i])
            for i in to_remove_keys:
                if i in self.raid.dps.keys() or i in self.raid.backup_dps.keys():
                    self.raid.remove_dps(i)
                    names += f"{interaction.guild.get_member(int(i)).display_name}\n"
                elif i in self.raid.healers.keys() or \
                        i in self.raid.backup_healers.keys():
                    self.raid.remove_healer(i)
                    names += f"{interaction.guild.get_member(int(i)).display_name}\n"
                elif i in self.raid.tanks.keys() or \
                        i in self.raid.backup_tanks.keys():
                    self.raid.remove_tank(i)
                    names += f"{interaction.guild.get_member(int(i)).display_name}\n"
            update_db(self.channel_id, self.raid)
            await interaction.response.send_message(f"User(s) have been removed from roster {self.channel.name}.\n{names}")
        except ValueError:
            await interaction.response.send_message(f"Use the numbers only, no other values are allowed.\n"
                                                    f"ex: `1,2,3,4`")
            return

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'I was unable to complete the command. Logs have more detail.')
        logging.error(f"Remove From Roster Error: {str(error)}")
        return

class Raids(commands.Cog, name="Trials"):
    """Commands related to Raids/Trials"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        set_channels(self.bot.config)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Event listener for when someone leaves the server to remove them from all rosters they are on."""
        try:
            was_on = False
            user_id = str(member.id)
            rosters = raids.distinct("channelID")
            private_channel = member.guild.get_channel(self.bot.config['administration']['private'])
            await private_channel.send(f"{member.name} - {member.display_name} has left the server")
            for i in rosters:
                raid = get_raid(i)
                channel = member.guild.get_channel(i)
                if user_id in raid.dps.keys():
                    raid.remove_dps(user_id)
                    await private_channel.send(f"Traitor was removed as a DPS from {channel.name}")
                    was_on = True
                    update_db(i, raid)
                elif user_id in raid.backup_dps.keys():
                    raid.remove_dps(user_id)
                    await private_channel.send(f"Traitor was removed as a backup DPS from {channel.name}")
                    was_on = True
                    update_db(i, raid)
                elif user_id in raid.healers.keys():
                    raid.remove_healer(user_id)
                    await private_channel.send(f"Traitor was removed as a Healer from {channel.name}")
                    was_on = True
                    update_db(i, raid)
                elif user_id in raid.backup_healers.keys():
                    raid.remove_healer(user_id)
                    await private_channel.send(f"Traitor was removed as a backup Healer from {channel.name}")
                    was_on = True
                    update_db(i, raid)
                elif user_id in raid.tanks.keys():
                    raid.remove_tank(user_id)
                    await private_channel.send(f"Traitor was removed as a Tank from {channel.name}")
                    was_on = True
                    update_db(i, raid)
                elif user_id in raid.backup_tanks.keys():
                    raid.remove_tank(user_id)
                    await private_channel.send(f"Traitor was removed as a backup Tank from {channel.name}")
                    was_on = True
                    update_db(i, raid)
            if was_on:
                await private_channel.send(f"The Traitor has been removed from all active rosters.")
            else:
                await private_channel.send(f"The Traitor was not on any active rosters.")
        except Exception as e:
            logging.error(f"User Roster Exit Removal Error: {str(e)}")
            raise OSError(f"Unable to remove user on exit from rosters.")

    @app_commands.command(name="trial", description="For Raid Leads: Opens Trial Creation Modal")
    @permissions.application_has_raid_lead()
    async def create_roster(self, interaction: discord.Interaction) -> None:
        raid = None
        await interaction.response.send_modal(TrialModal(raid, interaction, self.bot.config))

    @app_commands.command(name="modify", description="For Raid Leads: Modify your Trial Roster Details")
    @permissions.application_has_raid_lead()
    async def modify_roster(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Select the roster", view=RosterSelectView(interaction, self.bot, interaction.user, "modify"))

    @commands.command(name="trial", hidden=True)
    async def old_trial_alert(self, ctx: commands.Context):
        await ctx.reply(f"This command has moved to an application command, look for /trial instead!")

    @commands.command(name="modify", aliases=["date", "datetime", "time", "leader", "change", "rolenum", "memo", "limit"], hidden=True)
    async def modify_alert(self, ctx: commands.Context):
        await ctx.reply(f"This command has moved to an application command, look for /modify instead!")

    @app_commands.command(name="call", description="For Raid Leads: Send a message to all on a roster")
    @permissions.application_has_raid_lead()
    async def call_roster(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Select the roster", view=RosterSelectView(interaction, self.bot, interaction.user, "call"))

    @commands.command(name="call", hidden=True)
    @permissions.has_raid_lead()
    async def send_message_to_everyone(self, ctx: commands.Context):
        """For Raid Leads: A way to send a ping to everyone in a roster."""
        try:
            await ctx.reply(f"This command has moved to an application command, use /call instead!")
        except Exception as e:
            logging.error(f"Call error: {str(e)}")
            return
    @app_commands.command(name="fill", description="For Raid Leads: Fill a roster from backup")
    @permissions.application_has_raid_lead()
    async def fill_roster(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Select the roster", view=RosterSelectView(interaction, self.bot, interaction.user, "fill"))
    @commands.command(name="fill", hidden="true")
    @permissions.has_raid_lead()
    async def roster_fill_old(self, ctx: commands.Context):
        """ For Raid Leads: Lets you select the raid to fill the main list from backups."""
        try:
            await ctx.reply(f"This command has moved to an application command, use /fill instead!")
        except Exception as e:
            await ctx.send(f"Unable to process the command")
            logging.error(f"Fill Roster Error: {str(e)}")
            return

    @app_commands.command(name="close", description="For Raid Leads: Close a roster")
    @permissions.application_has_raid_lead()
    async def close_roster(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Select the roster", view=RosterSelectView(interaction, self.bot, interaction.user, "close"))

    @commands.command(name="close", hidden=True)
    @permissions.has_raid_lead()
    async def close_roster_old(self, ctx: commands.Context):
        """For Raid Leads: Closes out a roster"""
        try:
            await ctx.reply(f"This command has moved to an application command, use /close instead!")
        except Exception as e:
            logging.error(f"Close error: {str(e)}")
            await ctx.send("An error has occurred in the command.")

    @app_commands.command(name="runcount", description="For Raid Leads: Increase a rosters runcount")
    @permissions.application_has_raid_lead()
    async def increase_run_count(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Select the roster", view=RosterSelectView(interaction, self.bot, interaction.user, "run_count"))

    @commands.command(name="runcount", hidden=True)
    @permissions.has_raid_lead()
    async def increase_run_count_old(self, ctx: commands.Context):
        """For Raid Leads: Increase rosters run count"""
        try:
            await ctx.reply(f"This command has moved to an application command, use /runcount instead!")
        except Exception as e:
            logging.error(f"Run Count error: {str(e)}")
            await ctx.send("An error has occurred in the command.")
            return

    @app_commands.command(name="remove", description="For Raid Leads: Remove people from a roster")
    @permissions.application_has_raid_lead()
    async def remove_people_from_roster(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Select the roster", view=RosterSelectView(interaction, self.bot, interaction.user, "remove"))

    @commands.command(name="remove", hidden=True)
    @permissions.has_raid_lead()
    async def remove_from_roster(self, ctx: commands.Context):
        """For Raid Leads: Removes someone from the roster"""
        try:
            await ctx.reply(f"This command has moved to an application command, use /remove instead!")
        except Exception as e:
            logging.error(f"Remove error: {str(e)}")
            await ctx.send("An error has occurred in the command.")



    @commands.command(name="su")
    async def su(self, ctx: commands.Context):
        """Signs you up to a roster | `!su [optional role] [optional message]`"""
        try:
            channel_id = ctx.message.channel.id
            try:
                raid = get_raid(channel_id)
                if raid is None:
                    await ctx.send(f"Sorry! This command only works in a roster channel!")
                    return
            except Exception as e:
                await ctx.send("Unable to load raid.")
                logging.error(f"SU Load Raid Error: {str(e)}")
                return

            limiter = discord.utils.get(ctx.message.author.guild.roles, name=raid.role_limit)
            if ctx.message.author not in limiter.members:
                if raid.role_limit == self.bot.config["raids"]["roles"]["base"]:
                    await ctx.reply(f"Hey wait, you should have {raid.role_limit} in order to see this channel!")
                elif raid.role_limit == self.bot.config["raids"]["roles"]["first"]:
                    await ctx.reply(
                        f"You need to be CP 160 to join this roster, if you are CP 160 then go to <#1102081398136909854> "
                        f"and select the **Kyne's Follower** role from the Misc Roles section.")
                else:
                    await ctx.reply(
                        f"You do not have the role to join this roster, please check <#933821777149329468> "
                        f"to see what you need to do to get the {raid.role_limit} role")
                return

            result, raid = setup_roster_join_information(ctx.message.content, ctx.author, raid)

            try:
                update_db(channel_id, raid)
            except Exception as e:
                await ctx.send("I was unable to save the updated roster.")
                logging.error(f"SU Error saving new roster: {str(e)}")
                return
            await ctx.reply(f"{result}")
        except (UnknownError, NoDefaultError) as e:
            raise e
        except Exception as e:
            await ctx.send(f"I was was unable to sign you up due to processing errors.")
            logging.error(f"SU Error: {str(e)}")
            return

    @commands.command(name="bu")
    async def bu(self, ctx: commands.Context):
        """Signs you up as a backup | `!bu [optional role] [optional message]`"""
        try:
            channel_id = ctx.message.channel.id
            try:
                raid = get_raid(channel_id)
                if raid is None:
                    await ctx.send(f"Sorry! This command only works in a roster channel!")
                    return
            except Exception as e:
                await ctx.send("Unable to load raid.")
                logging.error(f"BU Load Raid Error: {str(e)}")
                return

            limiter = discord.utils.get(ctx.message.author.guild.roles, name=raid.role_limit)
            if ctx.message.author not in limiter.members:
                if raid.role_limit == self.bot.config["raids"]["roles"]["base"]:
                    await ctx.reply(f"Hey wait, you should have {raid.role_limit} in order to see this channel!")
                elif raid.role_limit == self.bot.config["raids"]["roles"]["first"]:
                    await ctx.reply(
                        f"You need to be CP 160 to join this roster, if you are CP 160 then go to <#1102081398136909854> "
                        f"and select the **Kyne's Follower** role from the Misc Roles section.")
                else:
                    await ctx.reply(
                        f"You do not have the role to join this roster, please check <#933821777149329468> "
                        f"to see what you need to do to get the {raid.role_limit} role")
                return

            result, raid = setup_roster_join_information(ctx.message.content, ctx.author, raid)

            try:
                update_db(channel_id, raid)
            except Exception as e:
                await ctx.send("I was unable to save the updated roster.")
                logging.error(f"BU Error saving new roster: {str(e)}")
                return
            await ctx.reply(f"{result}")
        except (UnknownError, NoDefaultError) as e:
            raise e
        except Exception as e:
            await ctx.send(f"I was was unable to sign you up due to processing errors.")
            logging.error(f"BU Error: {str(e)}")
            return

    @commands.command(name="wd")
    async def wd(self, ctx: commands.Context):
        """Will remove you from both BU and Main rosters"""
        try:
            worked = False
            channel_id = ctx.message.channel.id
            user_id = str(ctx.message.author.id)
            try:
                raid = get_raid(channel_id)
                if raid is None:
                    await ctx.send(f"Sorry! This command only works in a roster channel!")
                    return
            except Exception as e:
                await ctx.send("Unable to load raid.")
                logging.error(f"WD Load Raid Error: {str(e)}")
                return

            if user_id in raid.dps.keys() or \
                    user_id in raid.backup_dps.keys():
                raid.remove_dps(user_id)
                worked = True

            elif user_id in raid.healers.keys() or \
                    user_id in raid.backup_healers.keys():
                raid.remove_healer(user_id)
                worked = True

            elif user_id in raid.tanks.keys() or \
                    user_id in raid.backup_tanks.keys():
                raid.remove_tank(user_id)
                worked = True
            else:
                if not worked:
                    await ctx.send("You are not signed up for this roster")
            if worked:
                try:
                    if worked is True:
                        update_db(channel_id, raid)
                except Exception as e:
                    await ctx.send("I was unable to save the updated roster.")
                    logging.error(f"WD Error saving new roster: {str(e)}")
                    return
                await ctx.reply("Removed :(")
        except Exception as e:
            await ctx.send("Unable to withdraw you from the roster")
            logging.error(f"WD error: {str(e)}")
            return

    @commands.command(name="status")
    async def send_status_embed(self, ctx: commands.Context):
        """Posts the current roster information"""
        try:
            channel_id = ctx.message.channel.id
            try:
                raid = get_raid(channel_id)
                if raid is None:
                    await ctx.send(f"Sorry! This command only works in a roster channel!")
                    return
            except Exception as e:
                await ctx.send("Unable to load raid.")
                logging.error(f"Status Load Raid Error: {str(e)}")
                return

            dps_count = 0
            healer_count = 0
            tank_count = 0
            guild = self.bot.get_guild(self.bot.config['guild'])
            modified = False
            limiter = discord.utils.get(ctx.message.author.guild.roles, name=raid.role_limit)
            embed = discord.Embed(
                title=f"{raid.raid} {raid.date}",
                description=f"Role Required: {limiter.mention}",
                color=discord.Color.green()
            )
            embed.set_footer(text="Remember to spay or neuter your support!\nAnd mention your sets!")
            embed.set_author(name="Raid Lead: " + raid.leader)
            names = ""
            if not len(raid.healers) == 0:
                to_remove = []
                for i in raid.healers:
                    member_name = guild.get_member(int(i))
                    if member_name is None:
                        to_remove.append(i)
                        # Check if there are no healers left, if so then set names to None
                        if len(to_remove) == len(raid.healers):
                            names = "None"
                    else:
                        names += f"{self.bot.config['raids']['healer_emoji']}{member_name.display_name} {raid.healers[i]}\n"
                        healer_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        raid.remove_healer(i)
                    modified = True
            # TANKS
            if not len(raid.tanks) == 0:
                to_remove = []
                tanks = raid.tanks
                for i in tanks:
                    member_name = guild.get_member(int(i))
                    if member_name is None:
                        to_remove.append(i)
                        if len(to_remove) == len(raid.tanks):
                            names = "None"
                    else:
                        names += f"{self.bot.config['raids']['tank_emoji']}{member_name.display_name} {raid.tanks[i]}\n"
                        tank_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        raid.remove_tank(i)
                    modified = True
            # DPS
            if not len(raid.dps) == 0:
                to_remove = []
                dps = raid.dps
                for i in dps:
                    member_name = guild.get_member(int(i))
                    if member_name is None:
                        to_remove.append(i)
                        if len(to_remove) == len(raid.dps):
                            names = "None"
                    else:
                        names += f"{self.bot.config['raids']['dps_emoji']}{member_name.display_name} {raid.dps[i]}\n"
                        dps_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        raid.remove_dps(i)
                    modified = True
            if not names == "":
                embed.add_field(name="Roster", value=names, inline=False)
                names = f"Healers: {str(healer_count)}/{str(raid.healer_limit)}\nTanks: {str(tank_count)}/{str(raid.tank_limit)}\nDPS: {str(dps_count)}/{str(raid.dps_limit)}"
                embed.add_field(name="Total", value=names, inline=False)
            names = ""

            # Show Backup/Overflow Roster
            dps_count = 0
            healer_count = 0
            tank_count = 0
            # BACKUP HEALERS
            if not len(raid.backup_healers) == 0:
                to_remove = []
                backup_healers = raid.backup_healers
                for i in backup_healers:
                    member_name = guild.get_member(int(i))
                    if member_name is None:
                        to_remove.append(i)
                        if len(to_remove) == len(raid.backup_healers):
                            names = "None"
                    else:
                        names += f"{self.bot.config['raids']['healer_emoji']}{member_name.display_name} {raid.backup_healers[i]}\n"
                        healer_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        raid.remove_healer(i)
                    modified = True

            # BACKUP TANKS
            if not len(raid.backup_tanks) == 0:
                to_remove = []
                tanks = raid.backup_tanks
                for i in tanks:
                    member_name = guild.get_member(int(i))
                    if member_name is None:
                        to_remove.append(i)
                        if len(to_remove) == len(raid.backup_tanks):
                            names = "None"
                    else:
                        names += f"{self.bot.config['raids']['tank_emoji']}{member_name.display_name} {raid.backup_tanks[i]}\n"
                        tank_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        raid.remove_tank(i)
                    modified = True
            # BACKUP DPS
            if not len(raid.backup_dps) == 0:
                to_remove = []
                dps = raid.backup_dps
                for i in dps:
                    member_name = guild.get_member(int(i))
                    if member_name is None:
                        to_remove.append(i)
                        if len(to_remove) == len(raid.backup_dps):
                            names = "None"
                    else:
                        names += f"{self.bot.config['raids']['dps_emoji']}{member_name.display_name} {raid.backup_dps[i]}\n"
                        dps_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        raid.remove_dps(i)
                    modified = True

            if not names == "":
                embed.add_field(name="Backups", value=names, inline=False)
                names = f"Healers: {str(healer_count)}\nTanks: {str(tank_count)}\nDPS: {str(dps_count)}"
                embed.add_field(name="Total Backups", value=names, inline=False)

            if raid.memo != "None":
                embed_memo = discord.Embed(
                    title=" ",
                    color=discord.Color.dark_gray()
                )
                embed_memo.add_field(name=" ", value=raid.memo, inline=True)
                embed_memo.set_footer(text="This is very important!")
                await ctx.send(embed=embed_memo)
            await ctx.send(embed=embed)
            if modified:
                try:
                    update_db(channel_id, raid)
                except Exception as e:
                    await ctx.send("I was unable to save the updated roster.")
                    logging.error(f"Status Error saving new roster: {str(e)}")
                    return
        except Exception as e:
            logging.error(f"Status check error: {str(e)}")
            await ctx.send("Unable to send status.")
            return

    @commands.command(name="msg", aliases=["message"])
    async def set_message(self, ctx: commands.Context):
        """Modifies your message in the roster | `!msg [message]`"""
        try:
            try:
                channel_id = ctx.message.channel.id
                raid = get_raid(channel_id)
                if raid is None:
                    await ctx.send(f"Sorry! This command only works in a roster channel!")
                    return
            except Exception as e:
                await ctx.send("Unable to load raid.")
                logging.error(f"MSG Load Raid Error: {str(e)}")
                return
            msg = ctx.message.content
            msg = msg.split(" ", 1)
            if len(msg) == 1:
                msg = ""
            else:
                msg = msg[1]
            user_id = str(ctx.message.author.id)
            found = True
            if user_id in raid.dps.keys():
                raid.dps[user_id] = msg
            elif user_id in raid.backup_dps:
                raid.backup_dps[user_id] = msg
            elif user_id in raid.healers:
                raid.healers[user_id] = msg
            elif user_id in raid.backup_healers:
                raid.backup_healers[user_id] = msg
            elif user_id in raid.tanks:
                raid.tanks[user_id] = msg
            elif user_id in raid.backup_tanks:
                raid.backup_tanks[user_id] = msg
            else:
                await ctx.send("You are not signed up to the roster.")
                found = False
            if found:
                try:
                    update_db(channel_id, raid)
                except Exception as e:
                    await ctx.send("I was unable to save the updated roster.")
                    logging.error(f"Message Update Error saving new roster: {str(e)}")
                    return
                await ctx.reply("Updated!")
        except Exception as e:
            await ctx.send("Unable to update the roster message.")
            logging.error(f"Message Update Error: {str(e)}")
            return

    @commands.command(name="count")
    async def check_own_count(self, ctx: commands.Context):
        """A way for people to check their number of raid runs"""
        try:
            user = ctx.message.author
            counts = count.find_one({'userID': user.id})
            if counts is not None:
                embed = discord.Embed(
                    title=user.display_name,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Thank you for coming! Come again!")
                embed.set_author(name=f"Runs with {ctx.guild.name}")
                embed.add_field(name="Total Runs:", value=counts["raidCount"], inline=True)
                embed.add_field(name="Last Ran:", value=counts["lastRaid"], inline=True)
                embed.add_field(name="Last Date:", value=counts["lastDate"], inline=True)
                embed.add_field(name="Stats", value="Role Runs", inline=False)
                embed.add_field(name="DPS Runs:", value=counts["dpsRuns"], inline=True)
                embed.add_field(name="Tank Runs:", value=counts["tankRuns"], inline=True)
                embed.add_field(name="Healer Runs:", value=counts["healerRuns"], inline=True)
                await ctx.send(embed=embed)
            else:
                new_data = {
                    "userID": user.id,
                    "raidCount": 0,
                    "lastRaid": "none",
                    "lastDate": "<t:0:f>",
                    "dpsRuns": 0,
                    "tankRuns": 0,
                    "healerRuns": 0
                }
                try:
                    count.insert_one(new_data)
                except Exception as e:
                    logging.error(f"Count empty initialization error: {str(e)}")
                    await ctx.send("I was unable to initialize a count.")
                    return
                embed = discord.Embed(
                    title=user.display_name,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Thank you for coming! Come again!")
                embed.set_author(name=f"Runs with {ctx.guild.name}")
                embed.add_field(name="Total Runs:", value=0, inline=True)
                embed.add_field(name="Last Ran:", value="None", inline=True)
                embed.add_field(name="Last Date:", value="<t:0:f>", inline=True)
                embed.add_field(name="Stats", value="Role Runs", inline=False)
                embed.add_field(name="DPS Runs:", value="0", inline=True)
                embed.add_field(name="Tank Runs:", value="0", inline=True)
                embed.add_field(name="Healer Runs:", value="0", inline=True)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Unable to check count")
            logging.error(f"Count check error: {str(e)}")

    @commands.command(name="add")
    @permissions.has_raid_lead()
    async def add_to_roster(self, ctx: commands.Context, p_type, member: discord.Member):
        """For Raid Leads: Manually add to roster | `!add [role] [@ the user]`"""
        try:
            channel_id = ctx.message.channel.id  # Get channel id, use it to grab trial, and add user into the trial
            raid = get_raid(channel_id)
            if raid is None:
                await ctx.send(f"Sorry! This command only works in a roster channel!")
                return

            def remove_for_add(member_id):
                if member_id in raid.dps.keys() or \
                        member_id in raid.backup_dps.keys():
                    raid.remove_dps(member_id)

                elif member_id in raid.healers.keys() or \
                        member_id in raid.backup_healers.keys():
                    raid.remove_healer(member_id)

                elif member_id in raid.tanks.keys() or \
                        member_id in raid.backup_tanks.keys():
                    raid.remove_tank(member_id)

            added_member_id = str(member.id)

            worked = False
            if p_type.lower() == "dps":
                remove_for_add(added_member_id)
                result = raid.add_dps(added_member_id, "")
                worked = True
            elif p_type.lower() == "healer":
                remove_for_add(added_member_id)
                result = raid.add_healer(added_member_id, "")
                worked = True
            elif p_type.lower() == "tank":
                remove_for_add(added_member_id)
                result = raid.add_tank(added_member_id, "")
                worked = True
            else:
                await ctx.send(f"Please specify a valid role. dps, healer, or tank.")
            if worked:  # If True
                update_db(channel_id, raid)
                await ctx.reply(f"{result}")
        except OSError as e:
            await ctx.send(f"Unable to get process information.")
            logging.error(f"Add To Roster Raid Get Error: {str(e)}")
        except Exception as e:
            await ctx.send("Something has gone wrong.")
            logging.error(f"Add To Roster Error: {str(e)}")

    @commands.command(name="pin", aliases=["unpin"])
    @permissions.has_raid_lead()
    async def pin_message(self, ctx: commands.Context):
        """For Raid Leads: Allows pinning of a message"""
        try:
            ref = ctx.message.reference
            if ref is not None:
                # Is a reply - pin or unpin the reply message
                message = await ctx.fetch_message(ref.message_id)
                if message.pinned is True:
                    await message.unpin()
                    await ctx.reply(f"Message unpinned")
                    return
                else:
                    await message.pin()
                    return
            else:
                # Is not a reply - pin the command message
                await ctx.message.pin()
                return
        except Exception as e:
            await ctx.send("An unknown error has occurred with the command")
            logging.error(f"Pin Error: {str(e)}")


    @commands.command(name="limits")
    @permissions.has_raid_lead()
    async def print_limits(self, ctx: commands.Context):
        """Prints a list of the role limits and their values for making a roster."""
        try:
            limits = f"Roles and Values:\n" \
                     f"0: Kyne's Founded\n" \
                     f"1: Kyne's Follower\n" \
                     f"2: Kyne's Hunters\n" \
                     f"3: Storm Chasers\n" \
                     f"4: Storm Riders"
            await ctx.send(f"{limits}")
        except Exception as e:
            await ctx.send(f"I was unable to print the limits")
            logging.error(f"Print Limits Error: {str(e)}")

    #TODO: Improve increase and decrease with template factories for building data.
    #   Really only need one up above for use in the two functions.
    @commands.command(name="increase")
    @permissions.has_raid_lead()
    async def increase_raid_count(self, ctx: commands.Context, member: discord.Member = None):
        """Officer command to increase someone's ran count by 1"""
        try:
            if member is None:
                member = ctx.message.author
            counts = count.find_one({'userID': member.id})

            if counts is not None:
                counts["raidCount"] += 1
                try:
                    new_rec = {'$set': counts}
                    count.update_one({'userID': member.id}, new_rec)
                except Exception as e:
                    logging.error(f"Update Count Increase Error: {str(e)}")
                    await ctx.send("Unable to update the count")
                    return

                embed = discord.Embed(
                    title=member.display_name,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Thank you for coming! Come again!")
                embed.set_author(name=f"Runs with {ctx.guild.name}")
                embed.add_field(name="Total Runs:", value=counts["raidCount"], inline=True)
                embed.add_field(name="Last Ran:", value=counts["lastRaid"], inline=True)
                embed.add_field(name="Last Date:", value=counts["lastDate"], inline=True)
                embed.add_field(name="Stats", value="Role Runs", inline=False)
                embed.add_field(name="DPS Runs:", value=counts["dpsRuns"], inline=True)
                embed.add_field(name="Tank Runs:", value=counts["tankRuns"], inline=True)
                embed.add_field(name="Healer Runs:", value=counts["healerRuns"], inline=True)
                await ctx.send(embed=embed)
            else:
                new_data = {
                    "userID": member.id,
                    "raidCount": 1,
                    "lastRaid": "none",
                    "lastDate": "<t:0:f>",
                    "dpsRuns": 0,
                    "tankRuns": 0,
                    "healerRuns": 0
                }
                try:
                    count.insert_one(new_data)
                except Exception as e:
                    logging.error(f"Update Count Increase Error: {str(e)}")
                    await ctx.send("Unable to update the count")
                    return
                embed = discord.Embed(
                    title=member.display_name,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Thank you for coming! Come again!")
                embed.set_author(name=f"Runs with {ctx.guild.name}")
                embed.add_field(name="Total Runs:", value=1, inline=True)
                embed.add_field(name="Last Ran:", value="None", inline=True)
                embed.add_field(name="Last Date:", value="<t:0:f>", inline=True)
                embed.add_field(name="Stats", value="Role Runs", inline=False)
                embed.add_field(name="DPS Runs:", value="0", inline=True)
                embed.add_field(name="Tank Runs:", value="0", inline=True)
                embed.add_field(name="Healer Runs:", value="0", inline=True)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send("Unable to increase count")
            logging.error(f"Increase Count Error: {str(e)}")

    @commands.command(name="decrease")
    @permissions.has_raid_lead()
    async def decrease_raid_count(self, ctx: commands.Context, member: discord.Member = None):
        """Officer command to decrease someone's ran count by 1"""
        try:
            if member is None:
                member = ctx.message.author
            counts = count.find_one({'userID': member.id})
            if counts is not None:
                counts["raidCount"] -= 1
                if counts["raidCount"] < 0:
                    counts["raidCount"] = 1
                try:
                    new_rec = {'$set': counts}
                    count.update_one({'userID': member.id}, new_rec)
                except Exception as e:
                    logging.error(f"Update Count Decrease Error: {str(e)}")
                    await ctx.send("Unable to update the count")
                    return
                embed = discord.Embed(
                    title=member.display_name,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Thank you for coming! Come again!")
                embed.set_author(name=f"Runs with {ctx.guild.name}")
                embed.add_field(name="Total Runs:", value=counts["raidCount"], inline=True)
                embed.add_field(name="Last Ran:", value=counts["lastRaid"], inline=True)
                embed.add_field(name="Last Date:", value=counts["lastDate"], inline=True)
                embed.add_field(name="Stats", value="Role Runs", inline=False)
                embed.add_field(name="DPS Runs:", value=counts["dpsRuns"], inline=True)
                embed.add_field(name="Tanks Runs:", value=counts["tankRuns"], inline=True)
                embed.add_field(name="Healer Runs:", value=counts["healerRuns"], inline=True)
                await ctx.send(embed=embed)
            else:
                new_data = {
                    "userID": member.id,
                    "raidCount": 1,
                    "lastRaid": "none",
                    "lastDate": "<t:0:f>",
                    "dpsRuns": 0,
                    "tankRuns": 0,
                    "healerRuns": 0
                }
                try:
                    count.insert_one(new_data)
                except Exception as e:
                    logging.error(f"Update Count Decrease Error: {str(e)}")
                    await ctx.send("Unable to update the count")
                    return
                embed = discord.Embed(
                    title=member.display_name,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Thank you for coming! Come again!")
                embed.set_author(name=f"Runs with {ctx.guild.name}")
                embed.add_field(name="Total Runs:", value=1, inline=True)
                embed.add_field(name="Last Ran:", value="None", inline=True)
                embed.add_field(name="Last Date:", value="<t:0:f>", inline=True)
                embed.add_field(name="Stats", value="Role Runs", inline=False)
                embed.add_field(name="DPS Runs:", value="0", inline=True)
                embed.add_field(name="Tank Runs:", value="0", inline=True)
                embed.add_field(name="Healer Runs:", value="0", inline=True)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send("Unable to decrease count")
            logging.error(f"Decrease Count Error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Raids(bot))
