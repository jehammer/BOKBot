import nextcord
from nextcord.ext import commands
import logging


class Raffle(commands.Cog, name="Raffle"):
    """Receives Raffle commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


def setup(bot: commands.Bot):
    bot.add_cog(Raffle(bot))
