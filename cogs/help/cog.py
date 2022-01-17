from nextcord.ext import commands

class Help(commands.Cog, name="Help"):
    """Shows help info about commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #@commands.command()
    #async def gif(self, ctx: commands.Context):
    #    """Checks for a response from the bot"""
    #    await ctx.send("Here is a gif")


    


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
    