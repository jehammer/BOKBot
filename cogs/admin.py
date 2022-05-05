from nextcord.ext import commands
import logging


class Admin(commands.Cog, name="Admin"):
    """Special Admin only stuff"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logging.info("Admin cog loaded")

        # Needs to be bot.command() here
        @bot.command()
        async def servers(ctx):
            """Check the servers the bot is active in, Owner only"""
            if ctx.message.author.id == 212634819190849536:
                try:
                    all_servers = list(bot.guilds)
                    await ctx.send(f"Connected on {str(len(all_servers))} servers:")
                    await ctx.send('\n'.join(guild.name for guild in all_servers))
                except Exception as e:
                    logging.error("Server Check Error: " + str(e))
            else:
                await ctx.send("You do not have permission to do that.")


def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
