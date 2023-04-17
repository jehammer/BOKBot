import discord
from discord.ext import commands
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


class Admin(commands.Cog, name="Admin"):
    """Receives Administration commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="servers", hidden=True)
    async def servers(self, ctx: commands.Context):
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
        role = discord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
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

    @commands.command(name="sr", hidden=True)
    async def send_message_into_chat(self, ctx: commands.Context):
        """Just a fun little thing"""
        try:
            if ctx.message.author.id == 212634819190849536:
                msg = ctx.message.content
                msg = msg.split(" ", 2)
                guild = self.bot.get_guild(574095793414209556)
                channel = guild.get_channel(int(msg[1]))
                await channel.send(msg[2])
            else:
                await ctx.send(f"You do not have permission to do this.")
        except Exception as e:
            await ctx.send("Unable to send the message")
            logging.error("sr error:" + str(e))


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
