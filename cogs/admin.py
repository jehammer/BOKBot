import asyncio
from nextcord.ext import commands
import nextcord
import logging


class Admin(commands.Cog, name="Admin"):
    """Special Admin only stuff"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logging.info("Admin cog loaded")

    @commands.command()
    async def servers(self, ctx: commands.context):
        """Check the servers the bot is active in, Owner only"""
        if ctx.message.author.id == 212634819190849536:
            try:
                all_servers = list(self.bot.guilds)
                await ctx.send(f"Connected on {str(len(all_servers))} servers:")
                await ctx.send('\n'.join(guild.name for guild in all_servers))
            except Exception as e:
                logging.error("Server Check Error: " + str(e))
        else:
            await ctx.send("You do not have permission to do that.")

    @commands.command(name="getarma")
    async def get_arma(self, ctx: commands.Context):
        """Gets Arma with a series of DMs and pings in case he forgets again"""
        role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
        user = ctx.message.author
        if user in role.members:
            try:
                arma = ctx.message.guild.get_member(152077378317844480)
                if arma:
                    for i in range(4):
                        await arma.send("It is time for your regularly scheduled event")
                        await ctx.send(arma.mention + " it is time for you to get on!")
                        await asyncio.sleep(.5)

                else:
                    await ctx.send("Cannot find Arma")
            except Exception as e:
                await ctx.send("I cannot call Arma")
                logging.error("Call Arma error: " + str(e))
        else:
            await ctx.send("You do not have permission to use this command.")


def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
