import discord.role
from discord import member
from pytz import timezone
import datetime
import time
from re import sub

languages = ["Spanish", "French"]

class Utilities:
    """Class to store one-off functions that don't otherwise have a home"""

    @staticmethod
    def get_language(m: member):
        """Static Method to return a language based on a users Discord Roles"""
        for lang in languages:
            for role in m.roles:
                if lang == role.name:
                    return lang.lower()
        return "english"
    @staticmethod
    def suffix(d):
        try:
            return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')
        except Exception as e:
            logging.error(f"Suffix Failure: {str(e)}")
            raise ValueError("Unable to set suffix value")

    @staticmethod
    def list_to_dict(data):
        """DynamoDB, converts a List to a Dict for DB Storage"""
        count = 0
        mapped = {}
        for i in data:
            mapped[f'r{str(count)}'] = {'S': i }
            count+=1
        return mapped

    @staticmethod
    def dict_to_list(obj):
        mapped = []
        data = obj['data']['M']
        for key, value in data.items():
            mapped.append(value['S'])
        return mapped
