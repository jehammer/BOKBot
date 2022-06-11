import asyncio
from nextcord.ext import commands
import nextcord
import logging
import pickle

logging.basicConfig(level=logging.INFO)

reports = {}


class Reports:
    """A class to store reports"""

    def __init__(self, rep_id, user_id, message):
        self.rep_id = rep_id
        self.user_id = int(user_id)
        self.message = message

    def get_data(self):
        all_data = [self.rep_id, self.user_id, self.message]
        return all_data


def save_reports():
    """Saves reports to a pickle"""
    try:
        logging.info("Started picking Reports")
        global reports
        to_dump = []
        for key in reports:
            to_dump.append(reports[key].get_data())
        with open('reportStorage.pkl', 'wb') as file:
            pickle.dump(to_dump, file, protocol=pickle.HIGHEST_PROTOCOL)
        logging.info("Finished picking Reports")
    except IOError as e:
        logging.error("Error on saving report pickle: " + str(e))


def load_reports():
    """Loads the dictionary that saves reports from BOK"""
    try:
        logging.info("Started loading Reports")
        global reports
        global report_ids
        all_data = []
        with open('reportStorage.pkl', 'rb') as file:
            all_data = pickle.load(file)
        for i in range(len(all_data)):
            # 0 : rep_id, 1: user_id, 2: message
            reports[all_data[i][0]] = Reports(all_data[i][0], all_data[i][1], all_data[i][2])
            # 0: rep_id, 1: user_id
            #report_ids[all_data[i][0]] = all_data[i][1]
        logging.info("Finished loading Reports")
    except IOError as e:
        logging.error("Error on loading report pickle: " + str(e))


class Admin(commands.Cog, name="Admin"):
    """Special Admin only stuff"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_reports()
        logging.info("Admin cog loaded")

    @commands.command()
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

    # Start of Report Commands

    @commands.command(name="report")
    async def create_report(self, ctx: commands.Context):
        """Create a report to an officer of an issue in DMs"""
        try:
            if not isinstance(ctx.channel, nextcord.channel.DMChannel):
                await ctx.reply(
                    "To use the report function send me a message in DMs using `!report [message]`")
            else:
                # Is sent in a DM
                guild = self.bot.get_guild(574095793414209556)
                channel = guild.get_channel(985054618985840662)
                message = ctx.message.content
                message = message.split(' ', 1)
                message = message[1]
                # And save into Pickle
                global reports
                nums = []
                for i in range(1, 20):
                    nums.append(i)
                next_num = [i for i in range(1, 20) if i not in reports.keys()]
                next_num = next_num[0]
                reports[next_num] = Reports(next_num, ctx.author.id, message)
                save_reports()
                await channel.send(f"New Report\n"
                                   f"Report ID: {next_num}\n"
                                   f"{message}")
                await ctx.author.send(
                    f"Report has been created and sent to the Officers. If you attached any media please "
                    f"note that it wont work please use !update and send an imgur or other service link.\n"
                    f"Please note that at the moment you can only open one report at a time.")
        except Exception as e:
            await ctx.author.send("I was unable to create a report for you.")
            logging.error(str(e))

    @commands.command(name="update")
    async def update_report(self, ctx: commands.Context):
        """Update a Report in the DMs"""
        try:
            if not isinstance(ctx.channel, nextcord.channel.DMChannel):
                await ctx.reply("To update the report send me a message in DMs using `!update [message]`")
            else:
                # Is sent in a DM
                guild = self.bot.get_guild(574095793414209556)
                channel = guild.get_channel(985054618985840662)
                message = ctx.message.content
                message = message.split(' ', 1)
                message = message[1]
                global reports
                report = None
                found = False
                for i in reports.keys():
                    if ctx.message.author.id == reports[i].user_id:
                        report = reports[i]
                        found = True
                report.message += f"\nUpdated Report:\n{message}"
                reports[report.rep_id] = report
                await channel.send(f"A report has been updated:\nID: {report.rep_id}\n{report.message}")
                # And save into Pickle
                save_reports()
                await ctx.author.send(f"Your report has been updated.")
                if not found:
                    await ctx.author.send("You do not have a report I can update.")
        except Exception as e:
            logging.error(str(e))

    @commands.command(name="next")
    async def get_next_report(self, ctx: commands.Context):
        """Command for an Officer to get the oldest report to do"""
        try:
            officer = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in officer.members:
                global reports
                keys = list(reports.keys())
                if len(keys) != 0:
                    report = reports[keys[0]]  # Get the next one up
                    await ctx.send(f"Report {report.rep_id}:\n{report.message}")
                else:
                    await ctx.send("There are no reports right now.")
            else:
                await ctx.reply("You do not have permission to do this.")
        except Exception as e:
            await ctx.send("Unable to get report")
            logging.error("Next report error: " + str(e))

    @commands.command(name="handle")
    async def handle_report(self, ctx: commands.Context):
        """Closes a report"""
        # TODO: Improve this.
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in role.members:
                def check(m: nextcord.Message):  # m = discord.Message.
                    return user == m.author
                global reports
                try:
                    counter = 1
                    total = ""
                    key_list = []
                    for i in reports.keys():
                        total += f"{str(counter)}\n"
                        counter += 1
                        key_list.append(i)
                    total += "0: Exit \n"
                    await ctx.reply("Enter a number from the list below to close the report")
                    await ctx.send(total)
                    #                        event = on_message without on_
                    msg = await self.bot.wait_for(event='message', check=check, timeout=15.0)
                    # msg = nextcord.Message
                except asyncio.TimeoutError:
                    # at this point, the check didn't become True, let's handle it.
                    await ctx.send(f"{ctx.author.mention}, report handle has timed out")
                    return
                else:
                    # at this point the check has become True and the wait_for has done its work now we can do ours
                    try:
                        choice = int(msg.content)
                        if choice == 0:
                            await ctx.send("Exiting command")
                            return
                        try:
                            report = reports[choice]
                            reporter = ctx.message.author.guild.get_member(report.user_id)
                            try:
                                run = True
                                while run:
                                    await ctx.send(f"Do you want to send a message? Type up your message or type "
                                                   f"'no' to not send a message or type 'cancel' to cancel closing this "
                                                   f"report. This will timeout in 60 seconds")
                                    msg = await self.bot.wait_for(event="message", check=check, timeout=60.0)
                                    msg = msg.content
                                    if msg.lower() == "no":
                                        del reports[choice]
                                        save_reports()
                                        await reporter.send("Your report has been handled.")
                                        run = False
                                        await ctx.send("Report handled.")
                                    elif msg.lower() == "cancel":
                                        await ctx.send("Exiting command.")
                                        return
                                    else:
                                        confirmation_message = f"Send this message:\n{msg}\n\ny/n?"
                                        await ctx.send(confirmation_message)
                                        confirm = await self.bot.wait_for(event="message", check=check, timeout=15.0)
                                        confirm = confirm.content
                                        if confirm.lower() == "y":
                                            del reports[choice]
                                            save_reports()
                                            await reporter.send(msg)
                                            run = False
                                            await ctx.send("Report closed, message sent.")
                                        elif confirm.lower() == "n":
                                            await ctx.send("Returning to start of section.")
                                        else:
                                            await ctx.send("Not a valid input, returning to start of section.")
                            except asyncio.TimeoutError:
                                await ctx.send(f"{ctx.author.mention}, handle has timed out")
                                return
                        except Exception as e:
                            await ctx.send("That is not a valid number, exiting command.")
                            logging.error(f"Handle error: {str(e)}")
                    except ValueError:
                        await ctx.send("The input was not a valid number!")
            else:
                await ctx.send("You do not have permission to use this command")
        except Exception as e:
            await ctx.send("Unable to handle report")
            logging.error(f"Handle error: {str(e)}")

    @commands.command(name="reply")
    async def reply_to_report(self, ctx: commands.Context):
        """Lets an officer reply to a report to communicate"""
        # TODO: Improve this
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in role.members:
                def check(m: nextcord.Message):  # m = discord.Message.
                    return user == m.author

                global reports
                try:
                    counter = 1
                    total = ""
                    key_list = []
                    for i in reports.keys():
                        total += f"{str(counter)}\n"
                        counter += 1
                        key_list.append(i)
                    total += "0: Exit \n"
                    await ctx.reply("Enter a number from the list below to reply to the report")
                    await ctx.send(total)
                    #                        event = on_message without on_
                    msg = await self.bot.wait_for(event='message', check=check, timeout=15.0)
                    # msg = nextcord.Message
                except asyncio.TimeoutError:
                    # at this point, the check didn't become True, let's handle it.
                    await ctx.send(f"{ctx.author.mention}, reply has timed out")
                    return
                else:
                    try:
                        choice = int(msg.content)
                        if choice == 0:
                            await ctx.send("Exiting command")
                            return
                        try:
                            report = reports[choice]
                            reporter = ctx.message.author.guild.get_member(report.user_id)
                            try:
                                run = True
                                while run:
                                    await ctx.send(f"Please type the message you want to send.\n"
                                                   f"You have 1 minute to complete this. Type 'cancel' to exit.")
                                    msg = await self.bot.wait_for(event="message", check=check, timeout=60.0)
                                    msg = msg.content
                                    if msg.lower() == "cancel":
                                        await ctx.send("Exiting command.")
                                        return
                                    else:
                                        confirmation_message = f"Send this message:\n{msg}\n\ny/n?"
                                        await ctx.send(confirmation_message)
                                        confirm = await self.bot.wait_for(event="message", check=check, timeout=15.0)
                                        confirm = confirm.content
                                        if confirm.lower() == "y":
                                            await reporter.send(msg)
                                            run = False
                                            await ctx.send("Message sent.")
                                        elif confirm.lower() == "n":
                                            await ctx.send("Returning to start of section.")
                                        else:
                                            await ctx.send("Not a valid input, returning to start of section.")
                            except asyncio.TimeoutError:
                                await ctx.send(f"{ctx.author.mention}, reply has timed out")
                                return
                        except Exception as e:
                            await ctx.send("Unable to complete the request.")
                            logging.error(f"Reply error: {str(e)}")
                    except Exception as e:
                        await ctx.send("Unable to complete the request.")
                        logging.error(f"Reply error: {str(e)}")
            else:
                await ctx.send("You do not have permission to use this command.")
        except Exception as e:
            await ctx.send("Unable to continue.")
            logging.error(f"Reply error: {str(e)}")

    @commands.command(name="reports")
    async def list_all_reports(self, ctx: commands.Context):
        """Lists all reports for an officer"""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in role.members:
                def check(m: nextcord.Message):  # m = discord.Message.
                    return user == m.author
                global reports
                nums = ""
                for i in reports.keys():
                    nums += f"{str(i)}\n"

                nums += "All\n0: Exit"
                await ctx.send(f"{nums}\nEnter a number to see that report, all to see all reports, 0 to exit.")
                try:
                    choice = await self.bot.wait_for(event="message", check=check, timeout=15.0)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention}, reports has timed out")
                    return
                choice = choice.content
                if choice.lower() == "all":
                    all_reports = ""
                    for i in reports.keys():
                        report = reports[i]
                        all_reports += f"Report {report.rep_id}:\n{report.message}\n\n"
                    await ctx.send(all_reports)
                else:
                    choice = int(choice)
                    if choice == 0:
                        await ctx.send("Exiting command")
                        return
                    else:
                        report = reports[choice]
                        await ctx.send(f"Report {report.rep_id}:\n{report.message}")
            else:
                await ctx.send("You do not have permission to do this.")
        except IndexError:
            await ctx.send("That was not an acceptable value")
        except ValueError:
            await ctx.send("That was not an acceptable value")
        except Exception as e:
            await ctx.send("Unable to list reports.")
            logging.error(f"Reports error: {str(e)}")

    # End of Report Commands


def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
