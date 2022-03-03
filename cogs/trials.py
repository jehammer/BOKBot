import nextcord
from nextcord.ext import commands
import pickle
import logging

# TODO: Actually comment through this stuff.

logging.basicConfig(level=logging.INFO)

# Dictionary to store different embeds
storage = {}


# Special class to store trial in
class EsoTrial:
    """Class to hold trial information"""

    def __init__(self, trial, date, time, leader, trial_dps={}, trial_healers={}, trial_tanks={}, backup_dps={},
                 backup_healers={}, backup_tanks={}):
        self.trial = trial
        self.date = date
        self.time = time
        self.leader = leader
        self.trial_dps = trial_dps
        self.trial_healers = trial_healers
        self.trial_tanks = trial_tanks
        self.backup_dps = backup_dps
        self.backup_healers = backup_healers
        self.backup_tanks = backup_tanks

    def get_data(self):
        all_data = [self.trial, self.date, self.time, self.leader, self.trial_dps, self.trial_healers, self.trial_tanks,
                    self.backup_dps, self.backup_healers, self.backup_tanks]
        return all_data

    # Add people into the right spots
    def add_dps(self, n_dps, p_class="will be sadistic"):
        if len(self.trial_dps) < 8:
            self.trial_dps[n_dps] = p_class
        else:
            self.backup_dps[n_dps] = p_class

    def add_healer(self, n_healer, p_class="will be soft mommy dom"):
        if len(self.trial_healers) < 2:
            self.trial_healers[n_healer] = p_class
        else:
            self.backup_healers[n_healer] = p_class

    def add_tank(self, n_tank, p_class="will be masochistic"):
        if len(self.trial_tanks) < 2:
            self.trial_tanks[n_tank] = p_class
        else:
            self.backup_tanks[n_tank] = p_class

    def add_backup_dps(self, n_dps, p_class="could be sadistic"):
        self.backup_dps[n_dps] = p_class

    def add_backup_healer(self, n_healer, p_class="could be soft mommy dom"):
        self.backup_healers[n_healer] = p_class

    def add_backup_tank(self, n_tank, p_class="could be masochistic"):
        self.backup_tanks[n_tank] = p_class

    # remove people from right spots
    def remove_dps(self, n_dps):
        if n_dps in self.trial_dps:
            del self.trial_dps[n_dps]
        else:
            del self.backup_dps[n_dps]

    def remove_healer(self, n_healer):
        if n_healer in self.trial_healers:
            del self.trial_healers[n_healer]
        else:
            del self.backup_healers[n_healer]

    def remove_tank(self, n_tank):
        if n_tank in self.trial_tanks:
            del self.trial_tanks[n_tank]
        else:
            del self.backup_tanks[n_tank]

    # Fill the roster with overflow people
    def fill_spots(self, num):
        loop = True
        # TODO Plan for change:
        # If user is in bu AND primary, remove from primary and slot them in as the bu role
        #   IF there is not enough of that type
        while loop:
            if len(self.trial_dps) < 8 and len(self.backup_dps) > 0:
                first = list(self.backup_dps.keys())[0]
                self.trial_dps[first] = self.backup_dps.get(first)
                del self.backup_dps[first]
            else:
                loop = False
        loop = True
        while loop:
            if len(self.trial_healers) < 2 and len(self.backup_healers) > 0:
                first = list(self.backup_healers.keys())[0]
                self.trial_healers[first] = self.backup_healers.get(first)
                del self.backup_healers[first]
            else:
                loop = False
        loop = True
        while loop:
            if len(self.trial_tanks) < 2 and len(self.backup_tanks) > 0:
                first = list(self.backup_tanks.keys())[0]
                self.trial_tanks[first] = self.backup_tanks.get(first)
                del self.backup_tanks[first]
            else:
                loop = False
        logging.info("Spots filled in trial id " + str(num))


def save_to_doc():
    try:
        global storage
        db_file = open('trialStorage.pkl', 'wb')
        to_dump = []
        for key in storage:
            to_dump.append([key, storage[key].get_data()])
        pickle.dump(to_dump, db_file)
        db_file.close()
    except Exception as e:
        logging.error("Error on saving pickle: " + str(e))


class Trial(commands.Cog, name="Trials"):
    """Receives trial commands"""

    def __init__(self, bot: commands.Bot):
        try:
            global storage
            db_file = open('trialStorage.pkl', 'rb')
            all_data = pickle.load(db_file)
            for i in range(len(all_data)):
                # 0: trial, 1: date, 2: time, 3: leader, 4: trial_dps = {},
                # 5: trial_healers = {}, 6: trial_tanks = {}, 7: backup_dps = {},
                # 8: backup_healers = {}, 9: backup_tanks = {}
                storage[all_data[i][0]] = EsoTrial(all_data[i][1][0], all_data[i][1][1], all_data[i][1][2],
                                                   all_data[i][1][3], all_data[i][1][4], all_data[i][1][5],
                                                   all_data[i][1][6], all_data[i][1][7],
                                                   all_data[i][1][8], all_data[i][1][9])

            db_file.close()
            logging.info("Loaded Trials and Trial Cog!")
        except Exception as e:
            logging.error("Error, unable to load:" + str(e))
        self.bot = bot

    @commands.command()
    async def trial(self, ctx: commands.Context):
        """Creates a new trial for BOK | format: !trial [leader],[trial],[date info],[time]"""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in role.members:
                msg = ctx.message.content
                msg = msg.split(" ", 1)  # Split into 2 parts of a list, the first space then the rest
                msg = msg[1]  # drop the !trial part
                leader, trial, date, time = msg.split(",")

                ran = ctx.message.channel.id  # use the id of the text channel to make a channel-specific trial listing
                embed = nextcord.Embed(
                    title=trial + " " + date + " " + time,
                    description="I hope people sign up for this.",
                    color=nextcord.Color.blue()
                )
                embed.set_footer(text="Remember to spay or neuter your support!")
                embed.set_author(name=leader)
                embed.add_field(name="Healers", value='To Heal Us', inline=False)
                embed.add_field(name="Tanks", value='To Be Stronk', inline=False)
                embed.add_field(name="DPS", value='To Stand In Stupid', inline=False)
                await ctx.send(embed=embed)

                # create new trial and put it in storage for later use
                new_trial = EsoTrial(trial, date, time, leader, trial_dps={}, trial_healers={},
                                     trial_tanks={}, backup_dps={}, backup_healers={}, backup_tanks={})
                storage[ran] = new_trial
                save_to_doc()
                logging.info("New Trial created: " + trial + " " + date + " " + time)
            else:
                await ctx.send("You do not have permission to do this.")
        except Exception as e:
            await ctx.send("Please use !help trial if you are having problems or notify Drak")
            logging.error("Trial creation error: " + str(e))

    @commands.command()
    async def su(self, ctx: commands.Context):
        """Use !su [role] [optional message]"""
        worked = True
        global storage
        try:
            try:

                # Plan for implementation:
                # If already in main roster, say they cannot su twice
                # IF in BU roster under the same role, swap from backup to primary
                # IF in BU roster under a different role, allow for sign up
                num = ctx.message.channel.id
                trial = storage.get(num)
                if ctx.message.author.name in trial.trial_dps.keys():
                    await ctx.send("You are already signed up as DPS!")
                    worked = False
                elif ctx.message.author.name in trial.backup_dps.keys():
                    await ctx.send("You are already signed up as backup DPS!")
                    worked = False
                elif ctx.message.author.name in trial.trial_healers.keys():
                    await ctx.send("You are already signed up as a Healer!")
                    worked = False
                elif ctx.message.author.name in trial.backup_healers.keys():
                    await ctx.send("You are already signed up as a backup Healer!")
                    worked = False
                elif ctx.message.author.name in trial.trial_tanks.keys():
                    await ctx.send("You are already signed up as a Tank!")
                    worked = False
                elif ctx.message.author.name in trial.backup_tanks.keys():
                    await ctx.send("You are already signed up as a backup Tank!")
                    worked = False
                else:
                    # Works if there is the optional message
                    msg = ctx.message.content
                    msg = msg.split(" ", 2)  # Split into 2 parts of a list
                    if msg[1].lower() == "dps":
                        trial.add_dps(ctx.message.author.name, msg[2])
                    elif msg[1].lower() == "healer":
                        trial.add_healer(ctx.message.author.name, msg[2])
                    elif msg[1].lower() == "tank":
                        trial.add_tank(ctx.message.author.name, msg[2])
                    else:
                        await ctx.send("Please type it as !su [type] [optional message]")
                        worked = False
            except:  # TODO: work a way around the lack of an optional message without throwing an error
                # Works without optional message.
                msg = ctx.message.content
                msg = msg.split(" ", 1)  # Split into 2 parts of a list
                num = ctx.message.channel.id
                trial = storage.get(num)
                if msg[1].lower() == "dps":
                    trial.add_dps(ctx.message.author.name)
                elif msg[1].lower() == "healer":
                    trial.add_healer(ctx.message.author.name)
                elif msg[1].lower() == "tank":
                    trial.add_tank(ctx.message.author.name)
                else:
                    await ctx.send("Please type it as !su [type] [optional message]")
                    worked = False
            if worked:
                # Update trial
                storage[num] = trial
                await ctx.send(ctx.message.author.mention + " Added!")
                save_to_doc()
        except Exception as e:
            await ctx.send("Please type it as !su [type] [optional message]. If you did this please notify Drak")
            logging.error("SU error:" + str(e))

    @commands.command()
    async def bu(self, ctx: commands.Context):
        """Use !bu [role] [optional message]"""
        worked = True
        try:
            try:
                # TODO Plan for implementation:
                # If already in bu roster, say they cannot bu twice
                # IF in primary roster under the same role, swap from primary to bu
                # IF in primary roster under a different role, allow for sign up
                num = ctx.message.channel.id
                trial = storage.get(num)
                if ctx.message.author.name in trial.trial_dps.keys():
                    await ctx.send("You are already signed up as DPS!")
                    worked = False
                elif ctx.message.author.name in trial.backup_dps.keys():
                    await ctx.send("You are already signed up as backup DPS!")
                    worked = False
                elif ctx.message.author.name in trial.trial_healers.keys():
                    await ctx.send("You are already signed up as a Healer!")
                    worked = False
                elif ctx.message.author.name in trial.backup_healers.keys():
                    await ctx.send("You are already signed up as a backup Healer!")
                    worked = False
                elif ctx.message.author.name in trial.trial_tanks.keys():
                    await ctx.send("You are already signed up as a Tank!")
                    worked = False
                elif ctx.message.author.name in trial.backup_tanks.keys():
                    await ctx.send("You are already signed up as a backup Tank!")
                    worked = False
                else:
                    msg = ctx.message.content
                    msg = msg.split(" ", 2)  # Split into 2 parts of a list
                    if msg[1].lower() == "dps":
                        trial.add_backup_dps(ctx.message.author.name, msg[2])
                    elif msg[1].lower() == "healer":
                        trial.add_backup_healer(ctx.message.author.name, msg[2])
                    elif msg[1].lower() == "tank":
                        trial.add_backup_tank(ctx.message.author.name, msg[2])
                    else:
                        await ctx.send("Please type it as !bu [type] [optional message]")
                        worked = False
            except:
                msg = ctx.message.content
                msg = msg.split(" ", 2)  # Split into 2 parts of a list
                num = ctx.message.channel.id
                trial = storage.get(num)
                if msg[1].lower() == "dps":
                    trial.add_backup_dps(ctx.message.author.name)
                elif msg[1].lower() == "healer":
                    trial.add_backup_healer(ctx.message.author.name)
                elif msg[1].lower() == "tank":
                    trial.add_backup_tank(ctx.message.author.name)
                else:
                    await ctx.send("Please type it as !bu [type] [optional message]")
                    worked = False
            if worked:
                # Update trial
                storage[num] = trial
                save_to_doc()
                await ctx.send(ctx.author.mention + " Added for Backup!")
        except Exception as e:
            await ctx.send("Please type it as !bu [type] [optional message]. If you did this please notify Drak")
            logging.error("BU error:" + str(e))

    @commands.command()
    async def wd(self, ctx: commands.Context):
        """Use !wd to remove yourself from the roster. This will remove you from both BU and Main rosters"""
        try:
            worked = False
            num = ctx.message.channel.id
            trial = storage.get(num)
            if ctx.message.author.name in trial.trial_dps.keys() or \
                    ctx.message.author.name in trial.backup_dps.keys():
                trial.remove_dps(ctx.message.author.name)
                worked = True

            if ctx.message.author.name in trial.trial_healers.keys() or \
                    ctx.message.author.name in trial.backup_healers.keys():
                trial.remove_healer(ctx.message.author.name)
                worked = True

            if ctx.message.author.name in trial.trial_tanks.keys() or \
                    ctx.message.author.name in trial.backup_tanks.keys():
                trial.remove_tank(ctx.message.author.name)
                worked = True
            else:
                if not worked:
                    await ctx.send("You are not signed up for this Trial")
            if worked:
                for i in ctx.guild.members:
                    if i.name == ctx.message.author.name:
                        await ctx.send(ctx.message.author.mention + " removed :(")
                storage[num] = trial
                save_to_doc()
        except Exception as e:
            await ctx.send("Something has gone wrong! Consult Drak!")
            logging.error("WD error: " + str(e))

    @commands.command()
    async def fill(self, ctx: commands.Context):
        """For trial leaders to fill the roster from the backup roster"""
        role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
        user = ctx.message.author
        if user in role.members:
            try:
                num = ctx.message.channel.id
                trial = storage.get(num)
                trial.fill_spots(num)
                storage[num] = trial
                save_to_doc()
                await ctx.send("Spots filled!")
            except Exception as e:
                await ctx.send("Something has gone wrong! Consult Drak!")
                logging.error("Fill error: " + str(e))
        else:
            await ctx.send("You must be a Storm Bringer to fill a roster.")

    @commands.command()
    async def status(self, ctx: commands.Context):
        """Prints out a list of all who are signed up as main and backups"""
        num = ctx.message.channel.id
        primary_embed, backup_embed = await self.print_roster(num)

        await ctx.send(embed=primary_embed)
        await ctx.send(embed=backup_embed)

    @commands.command()
    async def msg(self, ctx: commands.Context):
        """!msg [message] to modify your message in the embed"""
        trial = storage.get(ctx.message.channel.id)
        found = True
        msg = ctx.message.content
        msg = msg.split(" ", 1)
        msg = msg[1]
        if ctx.message.author.name in trial.trial_dps.keys():
            trial.trial_dps[ctx.message.author.name] = msg
        elif ctx.message.author.name in trial.backup_dps:
            trial.backup_dps[ctx.message.author.name] = msg
        elif ctx.message.author.name in trial.trial_healers:
            trial.trial_healers[ctx.message.author.name] = msg
        elif ctx.message.author.name in trial.backup_healers:
            trial.backup_healers[ctx.message.author.name] = msg
        elif ctx.message.author.name in trial.trial_tanks:
            trial.trial_tanks[ctx.message.author.name] = msg
        elif ctx.message.author.name in trial.backup_tanks:
            trial.backup_tanks[ctx.message.author.name] = msg
        else:
            await ctx.send("Error, are you in the trial?")
            found = False
        if found:
            await ctx.send("Updated!")

    @commands.command(name="listtrials")
    async def list_trials(self, ctx: commands.Context):
        """For debugging purposes, prints out IDs of trials"""
        if ctx.message.author.id == 212634819190849536:
            msg = ""
            if len(storage) > 0:
                for i in storage:
                    msg += str(i) + "\n"
            else:
                msg = "None"
            await ctx.send(msg)
        else:
            await ctx.send("You do not have permission.")

    @commands.command()
    async def end(self, ctx: commands.Context):
        """For raid leads, ends the trial."""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in role.members:
                num = ctx.message.channel.id
                del storage[num]
                await ctx.send("Trial Closed!")
            else:
                await ctx.send("You do not have permission for that.")
        except:
            await ctx.send("Trial not deleted! Something has gone wrong.")

    @commands.command()
    async def gather(self, ctx: commands.Context):
        """for raid leads, closes the roster and notifies everyone to come."""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in role.members:
                num = ctx.message.channel.id
                await self.call_everyone(num, ctx)
                await ctx.send("It is go time!")
                del storage[num]
                save_to_doc()
            else:
                await ctx.send("You do not have permission for that.")
        except Exception as e:
            await ctx.send("Something went wrong.")
            logging.error("Gather error: " + str(e))

    @commands.command()
    async def summon(self, ctx: commands.Context):
        """for raid leads, closes the roster and notifies everyone to come."""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in role.members:
                num = ctx.message.channel.id
                await self.call_everyone(num, ctx)
                await ctx.send("It is time to do the thing!")
            else:
                await ctx.send("You do not have permission for that.")
        except Exception as e:
            await ctx.send("Idk something went wrong!")
            logging.error("Summon error: " + str(e))

    @commands.command()
    async def save(self, ctx: commands.Context):
        """Saves roster data to storage"""
        if ctx.message.author.id == 212634819190849536:
            try:
                save_to_doc()
                await ctx.send("Saved!")
            except Exception as e:
                await ctx.send("Issue saving. Have Drak try to fix.")
                print("Error when saving data: " + str(e))
        else:
            await ctx.send("You do not have permission to do that.")

    @commands.command()
    async def load(self, ctx: commands.Context):
        """Loads the trials from storage into the bot"""
        if ctx.message.author.id == 212634819190849536:
            try:
                global storage
                db_file = open('trialStorage.pkl', 'rb')
                all_data = pickle.load(db_file)
                for i in range(len(all_data)):
                    # 0: trial, 1: date, 2: time, 3: leader, 4: trial_dps = {},
                    # 5: trial_healers = {}, 6: trial_tanks = {}, 7: backup_dps = {},
                    # 8: backup_healers = {}, 9: backup_tanks = {}
                    storage[all_data[i][0]] = EsoTrial(all_data[i][1][0], all_data[i][1][1], all_data[i][1][2],
                                                       all_data[i][1][3],
                                                       all_data[i][1][4], all_data[i][1][5], all_data[i][1][6],
                                                       all_data[i][1][7], all_data[i][1][8], all_data[i][1][9])

                db_file.close()
                await ctx.send("Loaded!")
            except Exception as e:
                await ctx.send("Data not loaded. Have Drak check code.")
                logging.error("Load error: " + str(e))
        else:
            await ctx.send("You do not have permission to do that.")

    # Commands for adding, removing, and modifying the roster

    @commands.command()
    async def remove(self, ctx: commands.Context):
        """Removes someone from the roster"""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            # check if user has perms
            user = ctx.message.author
            if user in role.members:
                found = False
                worked = True
                msg = ctx.message.content
                msg = msg.split(" ", 1)
                msg = msg[1]
                num = ctx.message.channel.id
                trial = storage.get(num)
                if msg in trial.trial_dps.keys() or msg in trial.backup_dps.keys():
                    trial.remove_dps(msg)
                    found = True
                if msg in trial.trial_healers.keys() or msg in trial.backup_healers.keys():
                    trial.remove_healer(msg)
                    found = True
                if msg in trial.trial_tanks.keys() or msg in trial.backup_tanks.keys():
                    trial.remove_tank(msg)
                else:
                    if not found:
                        worked = False
                        await ctx.send("Person not found")
                if worked:
                    for i in ctx.guild.members:
                        if i.name == ctx.message.author.name:
                            await ctx.send(ctx.message.author.mention + " removed " + msg)
                    storage[num] = trial
                    save_to_doc()
        except Exception as e:
            logging.error("Remove error: " + str(e))

    @commands.command()
    async def add(self, ctx: commands.Context, p_type, member: nextcord.Member):
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")  # check if user has perms
            user = ctx.message.author
            if user in role.members:
                num = ctx.message.channel.id # Get channel id, use it to grab trial, and add user into the trial
                trial = storage.get(num)
                if p_type.lower() == "dps":
                    trial.add_dps(member.name)
                elif p_type.lower() == "healer":
                    trial.add_healer(member.name)
                elif p_type.lower() == "tank":
                    trial.add_tank(member.name)
                else:
                    await ctx.send("could not find role")
                storage[num] = trial # save trial and save back to storage
                save_to_doc()
                await ctx.send("Player added!")
            else:
                await ctx.send("You do not have permission to do that.")
        except Exception as e:
            await ctx.send("Something has gone wrong.")
            logging.error("Add user error: " + str(e))

    @commands.command()
    async def leader(self, ctx: commands.Context, leader):
        """Replaces the leader of a trial"""
        role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
        user = ctx.message.author
        if user in role.members:
            try:
                num = ctx.message.channel.id
                trial = storage.get(num)
                old_leader = trial.leader
                trial.leader = leader
                storage[num] = trial
                save_to_doc()
                await ctx.send("Trial leader has been changed from " + old_leader + " to " + trial.leader)
            except Exception as e:
                logging.error("Leader replacement error: " + str(e))
                await ctx.send("Something has gone wrong")
        else:
            await ctx.send("You do not have permission to do this")

    @commands.command(name="changetrial")
    async def change_trial(self, ctx: commands.Context):
        """Replaces the trial of a trial"""
        role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
        user = ctx.message.author
        if user in role.members:
            try:
                num = ctx.message.channel.id
                msg = ctx.message.content
                msg = msg.split(" ", 1)
                msg = msg[1]
                trial = storage.get(num)
                old_trial = trial.trial
                trial.trial = msg
                storage[num] = trial
                save_to_doc()
                await ctx.send("Trial has been changed from " + old_trial + " to " + trial.trial)
            except Exception as e:
                logging.error("Trial replacement error: " + str(e))
                await ctx.send("Something has gone wrong")
        else:
            await ctx.send("You do not have permission to do this")

    @commands.command(name="date")
    async def change_date(self, ctx: commands.Context):
        """Replaces the date of a trial"""
        role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
        user = ctx.message.author
        if user in role.members:
            try:
                num = ctx.message.channel.id
                msg = ctx.message.content
                msg = msg.split(" ", 1)
                msg = msg[1]
                trial = storage.get(num)
                old_date = trial.date
                trial.date = msg
                storage[num] = trial
                save_to_doc()
                await ctx.send("Trial date has been changed from " + old_date + " to " + trial.date)
            except Exception as e:
                logging.error("Trial date replacement error: " + str(e))
                await ctx.send("Something has gone wrong")
        else:
            await ctx.send("You do not have permission to do this")

    @commands.command()
    async def time(self, ctx: commands.Context):
        """Replaces the time of a trial"""
        role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
        user = ctx.message.author
        if user in role.members:
            try:
                num = ctx.message.channel.id
                msg = ctx.message.content
                msg = msg.split(" ", 1)
                msg = msg[1]
                trial = storage.get(num)
                old_time = trial.time
                trial.time = msg
                storage[num] = trial
                save_to_doc()
                await ctx.send("Trial time has been changed from " + old_time + " to " + trial.time)
            except Exception as e:
                logging.error("Trial time replacement error: " + str(e))
                await ctx.send("Something has gone wrong")
        else:
            await ctx.send("You do not have permission to do this")

        # TODO: Implement this and functions for manually adding people to roster

    @commands.command()
    async def clean(self, ctx: commands.Context, num):
        """For Drak when someone doesnt end a trial"""
        if ctx.message.author.id == 212634819190849536:
            try:
                num = int(num)
                global storage
                del storage[num]
                save_to_doc()
                await ctx.send("The butt has been wiped.")
            except Exception as e:
                await ctx.send("Error, data not cleaned.")
                logging.error("Clean error: " + str(e))
        else:
            await ctx.send("You do not have permission to do that.")

    async def print_roster(self, num):
        try:
            global storage
            trial = storage.get(num)
            dps_count = 0
            healer_count = 0
            tank_count = 0
            embed = nextcord.Embed(
                title=trial.trial + " " + trial.date + " " + trial.time,
                description="This battle will be legendary!",  # trial.time,
                color=nextcord.Color.green()
            )
            embed.set_footer(text="Remember to spay or neuter your support!")
            embed.set_author(name=trial.leader)

            # HEALERS
            names = ""
            for i in trial.trial_healers:
                names += "<:Healer:933835785352904864>" + i + " " + trial.trial_healers[i] + " " + "\r\n"
                healer_count += 1
            if len(names) == 0:
                names = "None"
            embed.add_field(name="Healers", value=names, inline=False)

            # TANKS
            names = ""
            for i in trial.trial_tanks:
                names += "<:Tank:933835838951948339>" + i + " " + trial.trial_tanks[i] + " " + "\r\n"
                tank_count += 1
            if len(names) == 0:
                names = "None"
            embed.add_field(name="Tanks", value=names, inline=False)

            # DPS
            names = ""
            for i in trial.trial_dps:
                names += "<:DPS:933835811684757514>" + i + " " + trial.trial_dps[i] + " " + "\r\n"
                dps_count += 1
            if len(names) == 0:
                names = "None"

            embed.add_field(name="DPS", value=names, inline=False)
            names = "Healers: " + str(healer_count) + " \nTanks: " + str(tank_count) + " \nDPS: " + str(dps_count)
            embed.add_field(name="Total", value=names, inline=False)

            # Show Backup/Overflow Roster
            dps_count = 0
            healer_count = 0
            tank_count = 0
            embed2 = nextcord.Embed(
                title="Backups",
                # description = " ",
                color=nextcord.Color.orange()
            )
            embed2.set_footer(text="Remember to beep when backing up that dump truck")
            # embed.set_author(name=trial.leader)
            # BACKUP HEALERS
            names = ""
            for i in trial.backup_healers:
                names += "<:Healer:933835785352904864>" + i + " " + trial.backup_healers[i] + "\r\n"
                healer_count += 1
            if len(names) == 0:
                names = "None"
            embed2.add_field(name="Healers", value=names, inline=False)

            # BACKUP TANKS
            names = ""

            for i in trial.backup_tanks:
                names += "<:Tank:933835838951948339>" + i + " " + trial.backup_tanks[i] + "\r\n"
                tank_count += 1
            if len(names) == 0:
                names = "None"
            embed2.add_field(name="Tanks", value=names, inline=False)

            # BACKUP DPS
            names = ""
            for i in trial.backup_dps:
                names += "<:DPS:933835811684757514>" + i + " " + trial.backup_dps[i] + "\r\n"
                dps_count += 1
            if len(names) == 0:
                names = "None"
            embed2.add_field(name="DPS", value=names, inline=False)

            names = "Healers: " + str(healer_count) + "\nTanks: " + str(tank_count) + "\nDPS: " + str(dps_count)
            embed2.add_field(name="Total", value=names, inline=False)

            return embed, embed2
        except Exception as e:
            logging.error("Print roster error: " + str(e))

    async def call_everyone(self, num, ctx):
        # TODO: Finish and test this
        try:
            trial = storage.get(num)
            names = "\nHealers \n"
            for i in trial.trial_healers:
                for j in ctx.guild.members:
                    if i == j.name:
                        names += j.mention + "\n"
            if len(trial.trial_healers) == 0:
                names += "None " + "\n"

            names += "\nTanks \n"
            for i in trial.trial_tanks:
                for j in ctx.guild.members:
                    if i == j.name:
                        names += j.mention + "\n"
            if len(trial.trial_tanks) == 0:
                names += "None" + "\n"

            names += "\nDPS \n"
            for i in trial.trial_dps:
                for j in ctx.guild.members:
                    if i == j.name:
                        names += j.mention + "\n"
            if len(trial.trial_dps) == 0:
                names += "None" + "\n"

            await ctx.send(names)
        except Exception as e:
            await ctx.send("Error! Idk something went wrong!")
            logging.error("Summon error: " + str(e))

    @commands.command()
    async def check(self, ctx: commands.Context, num):
        """To see the info of an orphan"""
        if ctx.message.author.id == 212634819190849536:
            try:
                num = int(num)
                primary_embed, backup_embed = await self.print_roster(num)

                await ctx.send(embed=primary_embed)
                await ctx.send(embed=backup_embed)

            except Exception as e:
                logging.error("Check Error: " + str(e))
        else:
            await ctx.send("You do not have permission to do that.")


def setup(bot: commands.Bot):
    bot.add_cog(Trial(bot))
