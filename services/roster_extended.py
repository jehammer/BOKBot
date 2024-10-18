from services import Utilities
from re import sub
from aws import Dynamo
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from models import Roster, Count

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


def generate_time_from_timestamp(timestamp, tz):
    """Generates the time according to the bots default timezone in config from a timestamp"""
    return datetime.utcfromtimestamp(int(sub('[^0-9]', '', timestamp))).replace(tzinfo=ZoneInfo(tz))


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
    def get_limits(table_config, roles_config, creds_config):
        """Create list of roles with nested lists for 1-3 indexes"""

        from services import Librarian

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

        prog_roles = Librarian.get_progs(table_config, creds_config)

        if prog_roles is not None and prog_roles[0] != "None":
            for i in prog_roles:
                list_roles.append(i)
        return list_roles

    @staticmethod
    def increase_roster_count(roster: Roster, count, table_config, creds_config):
        """Increase run count of all users in a roster."""
        try:
            from services import Librarian

            for i in roster.dps:
                db_count = Librarian.get_count(i, table_config, creds_config)
                if db_count is None:
                    db_count = Count(runs=count, dps=count, trial=roster.trial, date=roster.date)
                else:
                    db_count.increase_data(runs=count, dps=count, trial=roster.trial, date=roster.date)
                Librarian.put_count(i, db_count, table_config, creds_config)

            for i in roster.tanks:
                db_count = Librarian.get_count(i, table_config, creds_config)
                if db_count is None:
                    db_count = Count(runs=count, tank=count, trial=roster.trial, date=roster.date)
                else:
                    db_count.increase_data(runs=count, tank=count, trial=roster.trial, date=roster.date)
                Librarian.put_count(i, db_count, table_config, creds_config)

            for i in roster.healers:
                db_count = Librarian.get_count(i, table_config, creds_config)
                if db_count is None:
                    db_count = Count(runs=count, healer=count, trial=roster.trial, date=roster.date)
                else:
                    db_count.increase_data(runs=count, healer=count, trial=roster.trial, date=roster.date)
                Librarian.put_count(i, db_count, table_config, creds_config)

        except Exception as e:
            logging.error(f"Increase Roster Run Count Error: {str(e)}")
            raise e

