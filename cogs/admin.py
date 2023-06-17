import discord
from discord.ext import commands
import logging
import asyncio
import decor.perms as permissions
import os
from datetime import datetime
import shutil
import re
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


class Admin(commands.Cog, name="Admin"):
    """Receives Administration commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="servers", hidden=True)
    @permissions.creator_only()
    async def servers(self, ctx: commands.Context):
        """Check the servers the bot is active in, Owner only"""
        if ctx.message.author.id == self.bot.config["creator"]:
            try:
                all_servers = list(self.bot.guilds)
                await ctx.send(f"Connected on {str(len(all_servers))} servers:")
                await ctx.send('\n'.join(guild.name for guild in all_servers))
            except Exception as e:
                logging.error(f"Server Check Error: {str(e)}")
        else:
            await ctx.send("You do not have permission to do that.")

    @commands.command(name="shutdown")
    @permissions.creator_only()
    async def shutdown(self, ctx: commands.Context):
        """Shut down the bot, Owner only"""
        try:
            log_name = "log.log"
            date = datetime.now().strftime("%m-%d-%Y")
            time = datetime.now().strftime("%I:%M:%S %p")
            logging.info(f"Shutdown command received - {time} on {date}")
            logging.shutdown()
            if os.path.exists(log_name):
                file_name = f"log-{date}.log"
                os.makedirs("logs", exist_ok=True)
                version = 1
                while os.path.exists(os.path.join("logs", file_name)):
                    base_name, extension = os.path.splitext(file_name)
                    base_name = re.sub(r'\(\d{1,2}\)', '', base_name)
                    file_name = f"{base_name}({version}){extension}"
                    version += 1
                path = os.path.join("logs", file_name)
                shutil.move(log_name, path)
            await self.bot.close()
        except Exception as e:
            logging.error(f"Shutdown Error: {str(e)}")

    @commands.command(name="getarma")
    @permissions.has_officer()
    async def get_arma(self, ctx: commands.Context):
        """Gets Arma with a series of DMs and pings in case he forgets again"""
        try:
            arma = ctx.message.guild.get_member(self.bot.config["arma"])
            if arma:
                for i in range(4):
                    await arma.send("It is time for your regularly scheduled event")
                    await ctx.send(arma.mention + " it is time for you to get on!")
                    await asyncio.sleep(.5)

            else:
                await ctx.send("Cannot find Arma")
        except Exception as e:
            await ctx.send("I cannot call Arma")
            logging.error(f"Call Arma error: {str(e)}")

    @commands.command(name="sr", hidden=True)
    @permissions.creator_only()
    async def send_message_into_chat(self, ctx: commands.Context):
        """Just a fun little thing"""
        try:
            msg = ctx.message.content
            msg = msg.split(" ", 2)
            guild = self.bot.get_guild(self.bot.config["guild"])
            channel = guild.get_channel(int(msg[1]))
            await channel.send(msg[2])
        except Exception as e:
            await ctx.send("Unable to send the message")
            logging.error(f"sr error: {str(e)}")

    @commands.command(name="cogreload")
    @permissions.creator_only()
    async def reload_cogs(self, ctx: commands.Context):
        """Owner Only: Reloads the cogs following an update"""
        try:
            logging.info("Preparing to reload cogs.")
            for filename in os.listdir("cogs"):
                if filename.endswith(".py") and not filename.startswith("_"):
                    try:
                        await self.bot.unload_extension(f"cogs.{filename[:-3]}")
                        logging.info(f"Successfully unloaded {filename}")

                    except Exception as e:
                        logging.info(f"Failed to unload {filename}")
                        logging.error(f"Cog Unload error: {str(e)}")

            logging.info(f"Reloading Cogs after unload")
            for filename in os.listdir("cogs"):
                if filename.endswith(".py") and not filename.startswith("_"):
                    try:
                        await self.bot.load_extension(f"cogs.{filename[:-3]}")
                        logging.info(f"Successfully loaded {filename}")

                    except Exception as e:
                        logging.info(f"Failed to load {filename}")
                        logging.error(f"Cog Load error: {str(e)}")
            logging.info(f"Cog Reload completed.")
        except Exception as e:
            logging.error(f"Cog Reload Error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
