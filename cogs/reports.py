import discord
from discord.ext import commands
import logging
from pymongo import MongoClient
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
client = MongoClient(MONGODB_HOST, MONGODB_PORT)
database = client['bot']  # Or do it with client.PyTest, accessing collections works the same way.
reps = database.reports


class Reports(commands.Cog, name="Reports"):
    """Receives reports commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Start of Report Commands

    @commands.command(name="report")
    async def create_report(self, ctx: commands.Context):
        """Create a report to an officer of an issue in DMs"""
        try:
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.reply("To use the report function send me a message in DMs using `!report [message]`")
            else:
                # Is sent in a DM
                guild = self.bot.get_guild(self.bot.config['guild'])
                channel = guild.get_channel(self.bot.config['administration']['private'])
                message = ctx.message.content
                message = message.split(' ', 1)
                message = message[1]
                existing = reps.distinct("localID")
                next_num = [i for i in range(1, 100) if str(i) not in existing]
                next_num = next_num[0]
                # Save report info to MongoDB
                try:
                    logging.info(f"Saving Report: {next_num}")
                    rec = {
                        'localID': str(next_num),
                        'reporterID': ctx.author.id,
                        'message': message
                    }
                    reps.insert_one(rec)
                    logging.info(f"Saved Report: {next_num}")
                except Exception as e:
                    await ctx.send("Error in saving information to MongoDB, roster was not saved.")
                    logging.error(f"Report Creation MongoDB Error: {str(e)}")
                    return

                await channel.send(f"New Report\n"
                                   f"Report ID: {next_num}\n"
                                   f"From: {ctx.message.author.display_name}\n"
                                   f"{message}")
                await ctx.author.send(
                    f"Report has been created and sent to the Admins. If you attached any media please "
                    f"note that it wont work please use !update [id] and send an imgur or other service link.\n"
                    f"The ID for this report is: {next_num}")
        except Exception as e:
            await ctx.author.send("I was unable to create a report for you.")
            logging.error(str(e))

    @commands.command(name="update")
    async def update_report(self, ctx: commands.Context):
        """Update a Report in the DMs"""
        try:
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.reply("To update the report send me a message in DMs using `!update [message]`")
            else:
                # Is sent in a DM
                guild = self.bot.get_guild(self.bot.config['guild'])
                channel = guild.get_channel(self.bot.config['administration']['private'])
                message = ctx.message.content
                message = message.split(' ', 2)
                rep_id = message[1]
                message = message[2]
                report = reps.find_one({'localID': rep_id})
                if report is None:
                    await ctx.send(f"Report with id {str(rep_id)} not found.")
                    return
                report['message'] += f"\nUpdated Report:\n{message}"
                await channel.send(f"A report has been updated:\nID: {rep_id}\n{report['message']}")
                # And save into Mongo
                try:
                    logging.info(f"Updating Report Report ID: {rep_id}")
                    new_rec = {'$set': report}
                    reps.update_one({'reportID': rep_id}, new_rec)
                    logging.info(f"Report updated")
                except Exception as e:
                    logging.error(f"Save Report to Mongo Error: {str(e)}")
                    await ctx.send("I was unable to save the report. Report not updated. Please notify an Admin.")
                    return
                await ctx.author.send(f"Your report has been updated.")
        except Exception as e:
            logging.error(str(e))

    @commands.command(name="next")
    async def get_next_report(self, ctx: commands.Context):
        """Command for an Officer to get the oldest report to do"""
        try:
            officer = discord.utils.get(ctx.author.guild.roles, name=self.bot.config['roles']['admin'])
            user = ctx.message.author
            if user in officer.members:
                rep_ids = reps.distinct("localID")
                if len(rep_ids) != 0:
                    next_rep = rep_ids[0]  # Get the next one up
                    report = reps.find_one({'localID': next_rep})
                    await ctx.send(f"Report\n"
                                   f"Report ID: {report['localID']}\n"
                                   f"From: {ctx.author.guild.get_member(report['reporterID']).display_name}\n"
                                   f"{report['message']}")
                else:
                    await ctx.send("There are no reports right now.")
                    return
            else:
                await ctx.reply("You do not have permission to do this.")
                return
        except Exception as e:
            await ctx.send("Unable to get report")
            logging.error("Next report error: " + str(e))

    @commands.command(name="handle")
    async def handle_report(self, ctx: commands.Context):
        """Closes a report"""
        try:
            role = discord.utils.get(ctx.message.author.guild.roles, name=self.bot.config['roles']['admin'])
            user = ctx.message.author
            if user in role.members:
                def check(m: discord.Message):  # m = discord.Message.
                    return user == m.author

                message = ctx.message.content
                message = message.split(' ', 2)
                rep_id = message[1]
                message = message[2]
                report = reps.find_one({'localID': rep_id})
                reporter = ctx.author.guild.get_member(report['reporterID'])
                await ctx.send(f"Send:\n{message}\nto:{reporter.display_name} (y/n)")
                confirm = await self.bot.wait_for("message", check=check, timeout=30.0)
                confirm = confirm.content.lower()
                if confirm == 'y':
                    await reporter.send(f"From the Admins/Officers: {message}")
                    try:
                        to_delete = {"localID": rep_id}
                        reps.delete_one(to_delete)
                    except Exception as e:
                        await ctx.send("I was unable to delete the report.")
                        logging.error(f"Mongo Report Delete Error: {str(e)}")
                        return
                    await ctx.send("Report handled.")
                    await reporter.send(f"Report ID: {rep_id} is now closed.")
                else:
                    await ctx.send("Exiting command")
                    return
            else:
                await ctx.send("You do not have permission to use this command")
                return
        except Exception as e:
            await ctx.send("Unable to handle report")
            logging.error(f"Handle error: {str(e)}")

    @commands.command(name="reply")
    async def reply_to_report(self, ctx: commands.Context):
        """Lets an officer reply to a report to communicate"""
        try:
            role = discord.utils.get(ctx.message.author.guild.roles, name=self.bot.config['roles']['admin'])
            user = ctx.message.author
            if user in role.members:
                def check(m: discord.Message):  # m = discord.Message.
                    return user == m.author

                message = ctx.message.content
                message = message.split(' ', 2)
                rep_id = message[1]
                message = message[2]
                report = reps.find_one({'localID': rep_id})
                reporter = ctx.author.guild.get_member(report['reporterID'])
                await ctx.send(f"Send:\n{message}\nto:{reporter.display_name} (y/n)")
                confirm = await self.bot.wait_for("message", check=check, timeout=30.0)
                confirm = confirm.content.lower()
                if confirm == 'y':
                    await reporter.send(f"From the Admins/Officers: {message}")
                    await ctx.send("Message sent.")
                else:
                    await ctx.send("Exiting command")
                    return
            else:
                await ctx.send("You do not have permission to use this command.")
        except Exception as e:
            await ctx.send("Unable to continue.")
            logging.error(f"Reply error: {str(e)}")

    @commands.command(name="reports")
    async def list_all_reports(self, ctx: commands.Context, num=None):
        """Lists all reports for an officer"""
        try:
            role = discord.utils.get(ctx.message.author.guild.roles, name=self.bot.config['roles']['admin'])
            user = ctx.message.author
            if user in role.members:
                def check(m: discord.Message):  # m = discord.Message.
                    return user == m.author

                if num is None:
                    # Print out EVERY report
                    rep_ids = reps.distinct("localID")
                    if rep_ids is None:
                        await ctx.send("There are no reports.")
                        return
                    total = ""
                    for i in rep_ids:
                        report = reps.find_one({"localID": i})
                        total += f"Report ID: {report['localID']}\n" \
                                 f"From: {ctx.author.guild.get_member(report['reporterID']).display_name}\n" \
                                 f"{report['message']}\n\n"
                    await ctx.send(total)
                else:
                    # print out a specific report.
                    report = reps.find_one({"localID": num})
                    if report is None:
                        await ctx.send("There is no report with that id")
                        return
                    await ctx.send(f"Report ID: {report['localID']}\n"
                                   f"From: {ctx.author.guild.get_member(report['reporterID']).display_name}\n"
                                   f"{report['message']}")
            else:
                await ctx.send("You do not have permission to do this.")
        except Exception as e:
            await ctx.send("Unable to list reports.")
            logging.error(f"Reports error: {str(e)}")

    # End of Report Commands


async def setup(bot: commands.Bot):
    await bot.add_cog(Reports(bot))
