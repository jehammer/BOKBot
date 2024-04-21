import discord.role
from discord import member

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
