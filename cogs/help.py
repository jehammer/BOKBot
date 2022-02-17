from nextcord.ext import commands
import logging


class Help(commands.Cog, name="Help"):
    """Shows help info about commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logging.info("Help cog loaded")


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
