from pytz import timezone
import datetime
import time
import re
class Naming:
    """Contains functions for text adjustment"""

    @staticmethod
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

    @staticmethod
    def format_date(date):
        """Formats the timestamp date to the correct version"""
        date = date.strip()
        if date.upper() == "ASAP":
            return date.upper()

        formatted_date = f"<t:{re.sub('[^0-9]', '', date)}:f>"
        return formatted_date

    @staticmethod
    def suffix(d):
        try:
            return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')
        except Exception as e:
            logging.error(f"Suffix Failure: {str(e)}")
            raise ValueError("Unable to set suffix value")