from bot.services import Utilities
from re import sub
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from bot.models import Roster, Count
from discord import Member, Guild
from discord.utils import get


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


def generate_time_from_timestamp(timestamp, tz):
    """Generates the time according to the bots default timezone in config from a timestamp"""
    return datetime.fromtimestamp(int(sub('[^0-9]', '', timestamp)), ZoneInfo(tz))


def create_pingable_role(trial, date, tz, guild: Guild):
    new_name = False
    name = ''
    inc = 0
    while not new_name:
        second_part = ''
        if date.upper() == 'ASAP':
            second_part = f"{date} {inc if inc > 0 else ''}"
        else:
            timestamp = generate_time_from_timestamp(date, tz)
            second_part = f"{timestamp.strftime('%a')} {timestamp.day}{Utilities.suffix(timestamp.day)} {inc if inc > 0 else ''}"
        name = f"{trial} {second_part}"
        if len(name) > 20:
            chars_to_remove = len(name) - 20
            name = f"{trial[:-chars_to_remove]} {second_part}"
        checker = get(guild.roles, name=name.strip())
        if checker is None:
            new_name = True
        else:
            inc += 1
    return name


class RosterExtended:
    """Class of static methods for trial operations."""

    @staticmethod
    def factory(fact_leader, fact_raid, fact_date, fact_dps_limit, fact_healer_limit, fact_tank_limit,
                fact_role_limit, fact_memo, config):
        if fact_dps_limit is None and fact_healer_limit is None and fact_tank_limit is None:
            fact_dps_limit = config["raids"]["roster_defaults"]["dps"]
            fact_healer_limit = config["raids"]["roster_defaults"]["healers"]
            fact_tank_limit = config["raids"]["roster_defaults"]["tanks"]
        dps, healers, tanks, backup_dps, backup_healers, backup_tanks = {}, {}, {}, {}, {}, {}
        return Roster(fact_raid, fact_date, fact_leader, dps, healers, tanks, backup_dps, backup_healers,
                      backup_tanks, fact_dps_limit, fact_healer_limit, fact_tank_limit, fact_role_limit,
                      fact_memo)

    @staticmethod
    def get_channel_position(roster: Roster, tz):
        try:
            if roster.date == "ASAP":
                weight = 50
            else:
                formatted_time = generate_time_from_timestamp(roster.date, tz)
                day = formatted_time.timetuple().tm_yday
                if day < 30:
                    day += 360
                weight = day
            return weight
        except Exception as e:
            logging.error(f"Sort Key Error: {str(e)}")
            raise Exception(e)

    @staticmethod
    def generate_channel_name(date, raid_name, tz):
        """Function to generate channel names on changed information"""
        date = date.strip()
        if date.upper() == "ASAP":
            new_name = f"{raid_name}-ASAP"
            if len(new_name) > 19:
                max_char = len(new_name) - 19
                new_name = f"{raid_name[:-max_char]}-ASAP"
            return new_name
        formatted_time = generate_time_from_timestamp(date, tz)
        weekday = formatted_time.strftime("%a")
        day = formatted_time.day
        suffix = Utilities.suffix(day)
        new_name = f"{raid_name}-{weekday}-{day}{suffix}"
        # Max channel name has to be 26 because modal max characters is 45, and 19 are already used
        if len(new_name) > 19:
            max_char = len(new_name) - 19
            new_name = f"{raid_name[:-max_char]}-{weekday}-{day}{suffix}"
        return new_name

    @staticmethod
    def format_date(date):
        """Formats the timestamp date to the correct version"""
        date = date.strip()
        if date.upper() == 'ASAP':
            return date.upper()

        formatted_date = f"<t:{sub('[^0-9]', '', date)}:f>"
        return formatted_date

    @staticmethod
    def did_day_change(original_date, new_date, tz):
        """Returns Boolean Value if a passed in Timestamp has changed from the Day it was set at, but not the hour"""

        # Check the ASAP dates
        if original_date == 'ASAP' or new_date == 'ASAP':
            if original_date == new_date:
                return False
            return True

        og_timestamp = generate_time_from_timestamp(original_date.strip(), tz)
        new_timestamp = generate_time_from_timestamp(new_date.strip(), tz)

        if (og_timestamp.day != new_timestamp.day or
                og_timestamp.month != new_timestamp.month or
                og_timestamp.year != new_timestamp.year):
            return True
        return False

    @staticmethod
    def did_trial_change(old_trial, new_trial):
        """Returns if a value changed that requires a roster name change not counting timestamp"""
        return old_trial != new_trial

    @staticmethod
    def get_limits(librarian, roles_config):
        """Create list of roles with nested lists for 1-3 indexes"""

        list_roles = [
            roles_config['base'],
            [
                roles_config['first']['dps'], roles_config['first']['tank'], roles_config['first']['healer']
            ],
            [
                roles_config['second']['dps'], roles_config['second']['tank'], roles_config['second']['healer']
            ],
            [
                roles_config['third']['dps'], roles_config['third']['tank'], roles_config['third']['healer']
            ]
        ]

        prog_roles = librarian.get_progs()

        if prog_roles is not None and prog_roles[0] != "None":
            for i in prog_roles:
                list_roles.append(i)
        return list_roles

    @staticmethod
    def increase_individual_count(user_id, trial, role, date, runs, librarian):
        """Increases count of a user."""
        try:
            count: Count = librarian.get_count(user_id=user_id)

            if role == "dps":
                count.increase_data(runs=runs, trial=trial, date=date, dps=runs)
            elif role == "tank":
                count.increase_data(runs=runs, trial=trial, date=date, tank=runs)
            elif role == "healer":
                count.increase_data(runs=runs, trial=trial, date=date, dps=runs)
            else:
                raise Exception(f"Increase Individual Count Error: Unknown Role Input: {role}")

            librarian.put_count(user_id=user_id, count=count)

        except Exception as e:
            logging.error(f"Increase Individual Run Count Error: {str(e)}")
            raise e

    @staticmethod
    def increase_roster_count(roster: Roster, count, librarian):
        """Increase run count of all users in a roster."""
        try:
            for i in roster.dps:
                db_count = librarian.get_count(i)
                if db_count is None:
                    db_count = Count(runs=count, dps=count, trial=roster.trial, date=roster.date)
                else:
                    db_count.increase_data(runs=count, dps=count, trial=roster.trial, date=roster.date)
                librarian.put_count(i, db_count)

            for i in roster.tanks:
                db_count = librarian.get_count(i)
                if db_count is None:
                    db_count = Count(runs=count, tank=count, trial=roster.trial, date=roster.date)
                else:
                    db_count.increase_data(runs=count, tank=count, trial=roster.trial, date=roster.date)
                librarian.put_count(i, db_count)

            for i in roster.healers:
                db_count = librarian.get_count(i)
                if db_count is None:
                    db_count = Count(runs=count, healer=count, trial=roster.trial, date=roster.date)
                else:
                    db_count.increase_data(runs=count, healer=count, trial=roster.trial, date=roster.date)
                librarian.put_count(i, db_count)

        except Exception as e:
            logging.error(f"Increase Roster Run Count Error: {str(e)}")
            raise e

    @staticmethod
    def validate_join_roster(roster_req, limits, user: Member, roster_role):
        try:
            role_to_limit_num = {
                'dps': 0,
                'tank': 1,
                'healer': 2
            }
            limit = limits[roster_req]

            # If someone has the Raid Leads role, they can bypass requirements.
            if isinstance(limit, list):
                limit = limit[role_to_limit_num[roster_role]]
            if any(limit == role.name for role in user.roles):
                return True
            elif any('Raid Leads' == role.name for role in user.roles):
                return True
            return False
        except Exception as e:
            logging.error(f"Add User To Roster Validation Error: {str(e)}")

    @staticmethod
    def create_pingable_role_name(trial, date, tz, guild: Guild):
        name = create_pingable_role(trial=trial, date=date, tz=tz, guild=guild)
        return name
