import discord.role
from discord import member
from pytz import timezone
import datetime
import time
from re import sub
import logging

languages = ['English', 'Spanish', 'French']

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")

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
    def format_error(lang, error):
        identifier = languages.index(lang.capitalize()) + 1
        return f"{identifier}{error}"

    @staticmethod
    def get_language_from_number(num):
        return languages[num-1].lower()