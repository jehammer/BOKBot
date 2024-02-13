import discord
from discord.ext import commands, tasks
import logging
import asyncio
import decor.perms as permissions
import os
import datetime
import shutil
import re
import yaml
from pymongo import MongoClient
import os
import time

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")

scheduled_time = datetime.time(13, 0, 0, 0) # UTC Time, remember to convert and use a 24 hour-clock CDT: 13, CST: 14.


def save_members_list(config, member_dict):
    client = MongoClient(config['mongo'])
    database = client['bot']
    misc = database.misc
    rec = {
        'members': 'list',
        'data': member_dict
    }
    misc.update_one({'members': 'list'},  {'$set': rec})

class Admin(commands.Cog, name="Admin"):
    """Receives Administration commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduled_good_morning.start()
        self.update_name_mapping.start()

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
            date = datetime.datetime.now().strftime("%m-%d-%Y")
            time = datetime.datetime.now().strftime("%I:%M:%S %p")
            logging.info(f"Shutdown command received - {time} on {date}")
            logging.shutdown()
            self.scheduled_good_morning.stop()
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

    @commands.command(name="cogreload", aliases=["reload", "reloadcog"])
    @permissions.creator_only()
    async def reload_cogs(self, ctx: commands.Context):
        """Owner Only: Reloads the cogs following an update"""
        try:
            logging.info(f"Stopping tasks")
            self.scheduled_good_morning.cancel()
            self.update_name_mapping.cancel()
            logging.info(f"Stopped tasks")
            logging.info("Preparing to reload cogs")
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
            logging.info(f"Cog Reload completed")
            self.bot.dispatch("load_on_ready", self.bot)
            await ctx.send(f"Cog Reload completed")
        except Exception as e:
            logging.error(f"Cog Reload Error: {str(e)}")
            await ctx.send(f"There was an issue reloading the cogs, check the logs for more info.")

    @commands.command(name="config", aliases=["configreload", "reset", "configreset", "resetconfig", "reloadconfig"])
    @permissions.creator_only()
    async def reload_config(self, ctx: commands.Context):
        """Owner Only: Reloads the config following an update"""
        try:
            logging.info(f"Loading new config")
            with open("config.yaml", 'r') as stream:
                data_loaded = yaml.safe_load(stream)
            self.bot.config = data_loaded
            logging.info(f"New config loaded")
            await ctx.send(f"Config loaded")
        except Exception as e:
            logging.error(f"Config Reload Error: {str(e)}")
            await ctx.send(f"There was an issue reloading the config, check the logs for more info.")

    @commands.command(name="sync", aliases=["resync", "synchronize", "rescynchronize"])
    @permissions.creator_only()
    async def sync_application_commands(self, ctx: commands.Context):
        """Owner Only: Force Syncs Application Commands"""
        try:
            synced = await self.bot.tree.sync()
            logging.info(f"Synced {len(synced)} command(s)")
            await ctx.send(f"Sync Complete. Synced {len(synced)} Application Commands.")
        except Exception as e:
            logging.error(f"Sync Error: {str(e)}")
            await ctx.send(f"There was an issue syncing, check the logs for more info.")

    @commands.command(name="data")
    async def dm_users_date(self, ctx: commands.Context):
        """Get a DM of all Information BOKBot has on you"""
        try:
            await ctx.author.send(f"Hello! Just a moment as I gather up all your information. Please note this only includes "
                                  f"saved information that is permanent, so any rosters you are on right now "
                                  f"will not be included in the data sent to you.")

            client = MongoClient(self.bot.config['mongo'])
            database = client['bot']
            ranks = database.ranks
            defaults = database.defaults
            counts = database.count

            user_id = ctx.message.author.id

            rec = defaults.find_one({'userID': user_id})
            if rec is None:
                default = "No Default Set"
            else:
                default = f"Default is set to: {rec['default']}"

            rec = ranks.find_one({'userID': user_id})
            if rec is None:
                rank = "No Rankings Done"
            else:
                rec = rec['data']
                rank = f"Total Times Ranked: {rec['count']}\n" \
                       f"Last Ranked: {rec['last_called']}\n" \
                       f"Lowest Rank: {rec['lowest']}\n" \
                       f"Highest Rank: {rec['highest']}\n" \
                       f"Doubles: {rec['doubles']}\n" \
                       f"Singles: {rec['singles']}\n" \
                       f"69 Count: {rec['six_nine']}\n" \
                       f"420 Count: {rec['four_twenty']}\n" \
                       f"Boob Count: {rec['boob']}"

            rec = counts.find_one({'userID': user_id})
            if rec is None:
                count = "No Raid Counts Recorded"
            else:
                count = f"Total Runs: {rec['raidCount']}\n" \
                        f"Last Ran: {rec['lastRaid']}\n" \
                        f"Last Date: {rec['lastDate']}\n" \
                        f"DPS Runs: {rec['dpsRuns']}\n" \
                        f"Tank Runs: {rec['tankRuns']}\n" \
                        f"Healer Runs: {rec['healerRuns']}"

            today = datetime.datetime.today()
            name = ctx.message.author.display_name

            text_lines = f"Data Request for {name} as of {today}\n\n" \
                         f"Discord User ID: {user_id}\n\n" \
                         f"##ROSTER DEFAULT INFORMATION##\n" \
                         f"{default}\n\n" \
                         f"##RANKING INFORMATION##\n" \
                         f"{rank}\n\n" \
                         f"##RUN COUNT INFORMATION##\n" \
                         f"{count}\n\n"

            # write to file
            with open(f"{name}.txt", "w") as file:
                file.write(text_lines)

            logging.info(f"Sending data request file to: {name}")

            # send file to Discord in message
            with open(f"{name}.txt", "rb") as file:
                await ctx.author.send("Your data has arrived:", file=discord.File(file, f"{name}.txt"))

            if os.path.exists(f"{name}.txt"):
                os.remove(f"{name}.txt")
            else:
                logging.error(f"Unable to find created file for the user")

            return

        except discord.Forbidden:
            await ctx.reply(f"For privacy reasons (not that I store anything not publicly available, but just to keep anyone's concern down) "
                            "this function requires you to have DMs available to me, please enable DMs on this server from non-friends so "
                            "I can send you this data.")
        except Exception as e:
            logging.error(f"GET ALL USER DATA COMMAND ERROR: {str(e)}")
            raise Exception(e)

    # AUTOMATED TASKS
    @tasks.loop(time=scheduled_time)
    async def scheduled_good_morning(self):
        try:
            if time.localtime().tm_isdst == 0:
                await asyncio.sleep(3600)
            guild = self.bot.get_guild(self.bot.config['guild'])
            channel = guild.get_channel(self.bot.config['morning_channel'])
            await channel.send(self.bot.config['morning'])
            try:
                today = datetime.datetime.today()
                today_month = today.month
                today_day = today.day
                today_year = today.year
                for member in guild.members:
                    joined = member.joined_at
                    joined_month = joined.month
                    joined_day = joined.day
                    joined_year = joined.year
                    if today_month == joined_month and today_day == joined_day and today_year > joined_year:
                        await channel.send(f"{member.mention} Happy Anniversary!")
            except Exception as e:
                await channel.send("Unable to get the Anniversaries.")
                logging.error(f"Good Morning Task Anniversary Error: {str(e)}")
        except Exception as e:
            logging.error(f"Good Morning Task Error: {str(e)}")

    @tasks.loop(time=scheduled_time)
    async def update_name_mapping(self):
        try:
            guild = self.bot.get_guild(self.bot.config['guild'])
            members_dict = {}
            for member in guild.members:
                members_dict[str(member.id)] = member.display_name
            save_members_list(self.bot.config, members_dict)

        except Exception as e:
            logging.error(f"Members Dict Update Task Error: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
