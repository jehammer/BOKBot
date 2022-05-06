import nextcord
from nextcord.ext import commands
import pickle
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

# Dictionary to store different trial info
storage = {}
trial_counter = {}

# TODO: Implement local time functionality for trial embeds


# Special class to store trial in'
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

    # Fill the roster with backup people
    #   If there is less than max spots in main roster ,and more than 0 people in backup roster, then go ahead and move
    #   people from the backup roster to the primary roster until all slots are filled or backups are used up
    def fill_spots(self, num):
        try:
            loop = True
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
            save_to_doc()
            logging.info("Spots filled in trial id " + str(num))
        except Exception as e:
            logging.error("Fill_Spots error: " + str(e))


def save_trial_count():
    """Saves the dictionary that counts peoples trials in BOK"""
    try:
        logging.info("Started picking Trial Count")
        global trial_counter
        with open('trialCountStorage.pkl', 'wb') as file:
            pickle.dump(trial_counter, file, protocol=pickle.HIGHEST_PROTOCOL)
        logging.info("Finished picking Trial Count")
    except IOError as e:
        logging.error("Error on saving trial count pickle: " + str(e))


def load_trial_count():
    """Loads the dictionary that counts peoples trials in BOK"""
    try:
        logging.info("Started loading Trial Count")
        global trial_counter
        with open('trialCountStorage.pkl', 'rb') as file:
            trial_counter = pickle.load(file)
        logging.info("Finished loading Trial Count")
    except IOError as e:
        logging.error("Error on loading trial count pickle: " + str(e))


def save_to_doc():
    """Saves the trials to a pickle"""
    try:
        logging.info("Started pickling Trials")
        global storage
        db_file = open('trialStorage.pkl', 'wb')
        to_dump = []
        # get_data returns a list of the information in the trial, so the key and info is kep together in one list
        for key in storage:
            to_dump.append([key, storage[key].get_data()])
        pickle.dump(to_dump, db_file)
        db_file.close()
        logging.info("Finished pickling Trials")
    except Exception as e:
        logging.error("Error on saving trials pickle: " + str(e))


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
                # This is disgusting. There has to be a better way to write this.
                # It looks like this because the pickle file saves the object into a list, the list has to be unpacked
                #   back into the EsoTrial object, with another list inside it that must be unpacked into the object
                storage[all_data[i][0]] = EsoTrial(all_data[i][1][0], all_data[i][1][1], all_data[i][1][2],
                                                   all_data[i][1][3], all_data[i][1][4], all_data[i][1][5],
                                                   all_data[i][1][6], all_data[i][1][7],
                                                   all_data[i][1][8], all_data[i][1][9])

            db_file.close()
            load_trial_count()
            self.bot = bot
            logging.info("Loaded Trials and Trial Cog!")
        except Exception as e:
            logging.error("Error, unable to load:" + str(e))

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

                # Get user ID and add them into the roster

                num = ctx.message.channel.id
                user_id = ctx.message.author.id
                trial = storage.get(num)
                if user_id in trial.trial_dps.keys():
                    await ctx.send("You are already signed up as DPS!")
                    worked = False
                elif user_id in trial.backup_dps.keys():
                    await ctx.send("You are already signed up as backup DPS!")
                    worked = False
                elif user_id in trial.trial_healers.keys():
                    await ctx.send("You are already signed up as a Healer!")
                    worked = False
                elif user_id in trial.backup_healers.keys():
                    await ctx.send("You are already signed up as a backup Healer!")
                    worked = False
                elif user_id in trial.trial_tanks.keys():
                    await ctx.send("You are already signed up as a Tank!")
                    worked = False
                elif user_id in trial.backup_tanks.keys():
                    await ctx.send("You are already signed up as a backup Tank!")
                    worked = False
                else:
                    # Works if there is the optional message
                    msg = ctx.message.content
                    msg = msg.split(" ", 2)  # Split into 2 parts of a list
                    if msg[1].lower() == "dps":
                        trial.add_dps(user_id, msg[2])
                    elif msg[1].lower() == "healer":
                        trial.add_healer(user_id, msg[2])
                    elif msg[1].lower() == "tank":
                        trial.add_tank(user_id, msg[2])
                    else:
                        await ctx.send("Please type it as !su [type] [optional message]")
                        worked = False
            except:  # TODO: work a way around the lack of an optional message without throwing an error
                # Works without optional message.
                msg = ctx.message.content
                msg = msg.split(" ", 1)  # Split into 2 parts of a list
                num = ctx.message.channel.id
                user_id = ctx.message.author.id
                trial = storage.get(num)
                if msg[1].lower() == "dps":
                    trial.add_dps(user_id)
                elif msg[1].lower() == "healer":
                    trial.add_healer(user_id)
                elif msg[1].lower() == "tank":
                    trial.add_tank(user_id)
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
                num = ctx.message.channel.id
                trial = storage.get(num)
                user_id = ctx.message.author.id
                if user_id in trial.trial_dps.keys():
                    await ctx.send("You are already signed up as DPS!")
                    worked = False
                elif user_id in trial.backup_dps.keys():
                    await ctx.send("You are already signed up as backup DPS!")
                    worked = False
                elif user_id in trial.trial_healers.keys():
                    await ctx.send("You are already signed up as a Healer!")
                    worked = False
                elif user_id in trial.backup_healers.keys():
                    await ctx.send("You are already signed up as a backup Healer!")
                    worked = False
                elif user_id in trial.trial_tanks.keys():
                    await ctx.send("You are already signed up as a Tank!")
                    worked = False
                elif user_id in trial.backup_tanks.keys():
                    await ctx.send("You are already signed up as a backup Tank!")
                    worked = False
                else:
                    msg = ctx.message.content
                    msg = msg.split(" ", 2)  # Split into 2 parts of a list
                    if msg[1].lower() == "dps":
                        trial.add_backup_dps(user_id, msg[2])
                    elif msg[1].lower() == "healer":
                        trial.add_backup_healer(user_id, msg[2])
                    elif msg[1].lower() == "tank":
                        trial.add_backup_tank(user_id, msg[2])
                    else:
                        await ctx.send("Please type it as !bu [type] [optional message]")
                        worked = False
            except:  # Another area where I need to handle this better
                msg = ctx.message.content
                msg = msg.split(" ", 2)  # Split into 2 parts of a list
                num = ctx.message.channel.id
                trial = storage.get(num)
                user_id = ctx.message.author.id
                if msg[1].lower() == "dps":
                    trial.add_backup_dps(user_id)
                elif msg[1].lower() == "healer":
                    trial.add_backup_healer(user_id)
                elif msg[1].lower() == "tank":
                    trial.add_backup_tank(user_id)
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
            user_id = ctx.message.author.id
            if user_id in trial.trial_dps.keys() or \
                    user_id in trial.backup_dps.keys():
                trial.remove_dps(user_id)
                worked = True

            if user_id in trial.trial_healers.keys() or \
                    user_id in trial.backup_healers.keys():
                trial.remove_healer(user_id)
                worked = True

            if user_id in trial.trial_tanks.keys() or \
                    user_id in trial.backup_tanks.keys():
                trial.remove_tank(user_id)
                worked = True
            else:
                if not worked:
                    await ctx.send("You are not signed up for this Trial")
            if worked:
                for i in ctx.guild.members:
                    if i.id == user_id:
                        await ctx.reply("Removed :(")
                storage[num] = trial
                save_to_doc()
        except Exception as e:
            await ctx.send("Unable to withdraw you from the roster")
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
                await ctx.send("Unable to fill the roster")
                logging.error("Fill error: " + str(e))
        else:
            await ctx.send("You must be a Storm Bringer to fill a roster.")

    @commands.command()
    async def status(self, ctx: commands.Context):
        """Prints out a list of all who are signed up as main and backups"""
        try:
            num = ctx.message.channel.id
            primary_embed, backup_embed = await self.print_roster(num, ctx.guild.id)

            await ctx.send(embed=primary_embed)
            await ctx.send(embed=backup_embed)
        except Exception as e:
            logging.error("Status check error: " + str(e))
            await ctx.send("Unable to send status, have Drak check the bot.")

    @commands.command()
    async def msg(self, ctx: commands.Context):
        """!msg [message] to modify your message in the embed"""
        trial = storage.get(ctx.message.channel.id)
        found = True
        msg = ctx.message.content
        msg = msg.split(" ", 1)
        msg = msg[1]
        user_id = ctx.message.author.id
        if user_id in trial.trial_dps.keys():
            trial.trial_dps[user_id] = msg
        elif user_id in trial.backup_dps:
            trial.backup_dps[user_id] = msg
        elif user_id in trial.trial_healers:
            trial.trial_healers[user_id] = msg
        elif user_id in trial.backup_healers:
            trial.backup_healers[user_id] = msg
        elif user_id in trial.trial_tanks:
            trial.trial_tanks[user_id] = msg
        elif user_id in trial.backup_tanks:
            trial.backup_tanks[user_id] = msg
        else:
            await ctx.send("You are not signed up for the trial.")
            found = False
        if found:
            await ctx.send("Updated!")

    @commands.command(name="listtrials")
    async def list_trials(self, ctx: commands.Context):
        """Owners way of checking the active trials list by id"""
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
                save_to_doc()
                await ctx.send("Trial Closed!")
            else:
                await ctx.send("You do not have permission for that.")
        except Exception as e:
            await ctx.send("Trial not deleted! Something has gone wrong.")
            logging.error("End Trial error: " + str(e))

    @commands.command()
    async def gather(self, ctx: commands.Context):
        """for raid leads, notifies everyone to come."""
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
            await ctx.send("Unable to summon everyone")
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
            user = ctx.message.author
            if user in role.members:
                found = False
                worked = True
                msg = ctx.message.content
                msg = msg.split(" ", 2)
                num = int(msg[1])  # stores the channel id for the trial

                # reusing msg because there is no way this will be confusing down the line. It stores the persons id
                msg = int(msg[2])
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
                        await ctx.send("Person not found, remember to copy the persons ID number.")
                if worked:
                    # How to get the display name of a user, when using the bot gets the code angry at you
                    removed = ctx.channel.guild.get_member(msg).display_name
                    await ctx.reply("Removed " + removed)
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
                num = ctx.message.channel.id  # Get channel id, use it to grab trial, and add user into the trial
                trial = storage.get(num)
                added_member_id = member.id
                worked = False
                if p_type.lower() == "dps":
                    trial.add_dps(added_member_id)
                    worked = True
                elif p_type.lower() == "healer":
                    trial.add_healer(added_member_id)
                    worked = True
                elif p_type.lower() == "tank":
                    trial.add_tank(added_member_id)
                    worked = True
                else:
                    await ctx.send("could not find role")
                if worked:  # If True
                    storage[num] = trial  # save trial and save back to storage
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
                await ctx.send("Unable to replace leader")
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
                await ctx.send("Unable to change trial")
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
                await ctx.send("unable to change date")
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
                await ctx.send("Unable to change time")
        else:
            await ctx.send("You do not have permission to do this")

    @commands.command()
    async def clean(self, ctx: commands.Context, num):
        """For Drak when someone doesn't end a trial"""
        if ctx.message.author.id == 212634819190849536:
            try:
                num = int(num)
                global storage
                del storage[num]
                save_to_doc()
                await ctx.send("The butt has been wiped.")
            except Exception as e:
                await ctx.send("Unable to wipe the butt, the wipes are dry.")
                logging.error("Clean error: " + str(e))
        else:
            await ctx.send("You do not have permission to do that.")

    async def print_roster(self, num, guild_id):
        try:
            global storage
            trial = storage.get(num)
            dps_count = 0
            healer_count = 0
            tank_count = 0
            guild = self.bot.get_guild(guild_id)
            embed = nextcord.Embed(
                title=trial.trial + " " + trial.date + " " + trial.time,
                description="This battle will be legendary!",
                color=nextcord.Color.green()
            )
            embed.set_footer(text="Remember to spay or neuter your support!")
            embed.set_author(name=trial.leader)

            # HEALERS
            names = ""
            if len(trial.trial_healers) == 0:
                names = "None"
            else:
                to_remove = []
                for i in trial.trial_healers:
                    member_name = guild.get_member(i)
                    if member_name is None:
                        to_remove.append(i)
                        # Check if there are no healers left, if so then set names to None
                        if len(to_remove) == len(trial.trial_healers):
                            names = "None"
                    else:
                        names += "<:Healer:933835785352904864>" + member_name.display_name + " " + \
                                 trial.trial_healers[i] + " " + "\r\n"
                        healer_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        trial.remove_healer(i)
                    save_to_doc()

            embed.add_field(name="Healers", value=names, inline=False)
            # TANKS
            names = ""
            if len(trial.trial_tanks) == 0:
                names = "None"
            else:
                to_remove = []
                tanks = trial.trial_tanks
                for i in tanks:
                    member_name = guild.get_member(i)
                    if member_name is None:
                        to_remove.append(i)
                        if len(to_remove) == len(trial.trial_tanks):
                            names = "None"
                    else:
                        names += "<:Tank:933835838951948339>" + member_name.display_name + " " + trial.trial_tanks[i] \
                                 + " " + "\r\n"
                        tank_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        trial.remove_tank(i)
                    save_to_doc()
            embed.add_field(name="Tanks", value=names, inline=False)

            # DPS
            names = ""
            if len(trial.trial_dps) == 0:
                names = "None"
            else:
                to_remove = []
                dps = trial.trial_dps
                for i in dps:
                    member_name = guild.get_member(i)
                    if member_name is None:
                        to_remove.append(i)
                        if len(to_remove) == len(trial.trial_dps):
                            names = "None"
                    else:
                        names += "<:DPS:933835811684757514>" + member_name.display_name + " " \
                                 + trial.trial_dps[i] + " " + "\r\n"
                        dps_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        trial.remove_dps(i)
                    save_to_doc()

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
            # BACKUP HEALERS
            names = ""
            if len(trial.backup_healers) == 0:
                names = "None"
            else:
                to_remove = []
                backup_healers = trial.backup_healers
                for i in backup_healers:
                    member_name = guild.get_member(i)
                    if member_name is None:
                        to_remove.append(i)
                        if len(to_remove) == len(trial.backup_healers):
                            names = "None"
                    else:
                        names += "<:Healer:933835785352904864>" + member_name.display_name + " " + \
                                 trial.backup_healers[i] + "\r\n"
                        healer_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        trial.remove_healer(i)
                    save_to_doc()

            embed2.add_field(name="Healers", value=names, inline=False)

            # BACKUP TANKS
            names = ""
            if len(trial.backup_tanks) == 0:
                names = "None"
            else:
                to_remove = []
                tanks = trial.backup_tanks
                for i in tanks:
                    member_name = guild.get_member(i)
                    if member_name is None:
                        to_remove.append(i)
                        if len(to_remove) == len(trial.backup_tanks):
                            names = "None"
                    else:
                        names += "<:Tank:933835838951948339>" + member_name.display_name + " " + trial.backup_tanks[i] \
                                 + "\r\n"
                        tank_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        trial.remove_tank(i)
                    save_to_doc()

            embed2.add_field(name="Tanks", value=names, inline=False)

            # BACKUP DPS
            names = ""
            if len(trial.backup_dps) == 0:
                names = "None"
            else:
                to_remove = []
                dps = trial.backup_dps
                for i in dps:
                    member_name = guild.get_member(i)
                    if member_name is None:
                        to_remove.append(i)
                        if len(to_remove) == len(trial.backup_dps):
                            names = "None"
                    else:
                        names += "<:DPS:933835811684757514>" + member_name.display_name + " " + trial.backup_dps[i] \
                                 + "\r\n"
                        dps_count += 1
                if len(to_remove) > 0:
                    for i in to_remove:
                        trial.remove_dps(i)
                    save_to_doc()

            embed2.add_field(name="DPS", value=names, inline=False)

            names = "Healers: " + str(healer_count) + "\nTanks: " + str(tank_count) + "\nDPS: " + str(dps_count)
            embed2.add_field(name="Total", value=names, inline=False)

            return embed, embed2
        except Exception as e:
            logging.error("Print roster error: " + str(e))

    async def call_everyone(self, num, ctx):
        try:
            trial = storage.get(num)
            names = "\nHealers \n"
            for i in trial.trial_healers:
                for j in ctx.guild.members:
                    if i == j.id:
                        names += j.mention + "\n"
            if len(trial.trial_healers) == 0:
                names += "None " + "\n"

            names += "\nTanks \n"
            for i in trial.trial_tanks:
                for j in ctx.guild.members:
                    if i == j.id:
                        names += j.mention + "\n"
            if len(trial.trial_tanks) == 0:
                names += "None" + "\n"

            names += "\nDPS \n"
            for i in trial.trial_dps:
                for j in ctx.guild.members:
                    if i == j.id:
                        names += j.mention + "\n"
            if len(trial.trial_dps) == 0:
                names += "None" + "\n"

            await ctx.send(names)
        except Exception as e:
            await ctx.send("Error printing roster")
            logging.error("Summon error: " + str(e))

    @commands.command()
    async def check(self, ctx: commands.Context, num):
        """To see the info of an orphan"""
        if ctx.message.author.id == 212634819190849536:
            try:
                num = int(num)
                primary_embed, backup_embed = await self.print_roster(num, ctx.guild.id)

                await ctx.send(embed=primary_embed)
                await ctx.send(embed=backup_embed)

            except Exception as e:
                logging.error("Check Error: " + str(e))
        else:
            await ctx.send("You do not have permission to do that.")

    @commands.command()
    async def close(self, ctx: commands.Context):
        """Closes a roster and deletes a channel for a trial"""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in role.members:
                def check(m: nextcord.Message):  # m = discord.Message.
                    return user == m.author
                #  checking author and channel, you could add a line to check the content.
                # and m.content == "xxx"
                # the check won't become True until it detects (in the example case): xxx
                # but that's not what we want here.

                # Not using this but keeping it in comments for later development
                run = True
                while run:
                    try:
                        counter = 1
                        total = ""
                        key_list = []
                        for i in storage.keys():
                            channel = ctx.guild.get_channel(i)
                            if channel is not None:
                                total += str(counter) + ": " + channel.name + "\n"
                            else:
                                total += str(counter) + ": " + str(i) + "\n"
                            counter += 1
                            key_list.append(i)
                        total += "0: Exit \n"
                        await ctx.reply("Enter a number from the list below to have the roster closed and "
                                        "the channel deleted")
                        await ctx.send(total)

                        #                        event = on_message without on_
                        msg = await self.bot.wait_for(event='message', check=check, timeout=15.0)
                        # msg = nextcord.Message
                    except asyncio.TimeoutError:
                        # at this point, the check didn't become True, let's handle it.
                        await ctx.send(f"{ctx.author.mention}, close has timed out")
                        return

                    else:
                        # at this point the check has become True and the wait_for has done its work now we can do ours
                        # we could also do things based on the message content here, like so
                        # if msg.content == "this is cool":
                        #    return await ctx.send("wait_for is indeed a cool method")

                        try:
                            # Since the bot uses python 3.10, dictionaries are indexed by the order of insertion.
                            #   However, I already wrote it like this. Oh well.
                            choice = int(msg.content)
                            choice -= 1  # Need to lower it by one for the right number to get
                            if choice == -1:
                                await ctx.send("Exiting command")
                                return
                            try:
                                num = key_list[choice]
                                try:
                                    channel = ctx.guild.get_channel(num)
                                    trial = storage.get(num)
                                    # Arma is likely to delete the channel but not the trial, best to account for that
                                    if channel is None:
                                        await ctx.send("Delete trial: " + trial.trial + " - " + str(num) + " (y/n)?")
                                    else:
                                        await ctx.send("Delete trial and channel: " + trial.trial + " - " + channel.name
                                                       + " (y/n)?")
                                    confirm = await self.bot.wait_for(event="message", check=check, timeout=15.0)
                                    confirm = confirm.content.lower()
                                except asyncio.TimeoutError:
                                    await ctx.send(f"{ctx.author.mention}, close has timed out")
                                    return
                                else:
                                    # Verify that the trial did happen, and if so then add a +1 to each person's count
                                    if confirm == "y":
                                        if num in storage.keys():
                                            # Todo: Finish this
                                            try:
                                                await ctx.send("Did the trial happen (y/n)?")
                                                confirm = await self.bot.wait_for(event="message", check=check,
                                                                                  timeout=15.0)
                                                confirm = confirm.content.lower()

                                                if confirm == "y":
                                                    trial = storage.get(num)
                                                    global trial_counter
                                                    for i in trial.trial_dps:
                                                        if i in trial_counter.keys():
                                                            trial_counter[i] += 1
                                                        else:
                                                            trial_counter[i] = 1
                                                    for i in trial.trial_healers:
                                                        if i in trial_counter.keys():
                                                            trial_counter[i] += 1
                                                        else:
                                                            trial_counter[i] = 1
                                                    for i in trial.trial_tanks:
                                                        if i in trial_counter.keys():
                                                            trial_counter[i] += 1
                                                        else:
                                                            trial_counter[i] = 1
                                                    save_trial_count()
                                            except asyncio.TimeoutError:
                                                await ctx.send(f"{ctx.author.mention}, close has timed out")
                                                return
                                            del storage[num]
                                            save_to_doc()
                                            channel = ctx.guild.get_channel(num)
                                            if channel is not None:
                                                await ctx.guild.get_channel(num).delete()
                                            await ctx.send("Channel deleted, roster closed")
                                            logging.info("Deleted channel and closed roster ID: " + str(num))
                                            run = False
                                        else:
                                            await ctx.send("Unable to find trial.")
                                    else:
                                        if confirm == 'n':
                                            await ctx.send("Returning to menu.")
                                        else:
                                            await ctx.send("Invalid response, returning to menu.")
                            except IndexError:
                                await ctx.send("That is not a valid number, returning to menu.")
                        except ValueError:
                            await ctx.send("The input was not a valid number!")
            else:
                await ctx.send("You do not have permission to use this command")
        except Exception as e:
            logging.error("Close error: " + str(e))
            await ctx.send("An error has occurred in the command.")

    # TODO: Create swap command to swap role easily

    # TODO: Add new functions for officers to add 1 or remove 1 from a persons trial count, and one for people to check

    @commands.command(name="increase")
    async def increase_trial_count(self, ctx: commands.Context, member: nextcord.Member):
        """Officer command to increase someone's trial count by 1"""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in role.members:
                global trial_counter
                if member.id in trial_counter.keys():
                    trial_counter[member.id] += 1
                    save_trial_count()
                    await ctx.send(f"Trial count for {member.display_name} is now {trial_counter.get(member.id)}")
                else:
                    trial_counter[member.id] = 1
                    save_trial_count()
                    await ctx.send(f"Trial count for {member.display_name} is now {trial_counter.get(member.id)}")
            else:
                await ctx.send("You do not have the permissions for this.")
        except Exception as e:
            await ctx.send("Unable to increase trial count")
            logging.error("Increase Trial Count Error: " + str(e))

    @commands.command(name="decrease")
    async def decrease_trial_count(self, ctx: commands.Context, member: nextcord.Member):
        """Officer command to decrease someone's trial count by 1"""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            user = ctx.message.author
            if user in role.members:
                global trial_counter
                if member.id in trial_counter.keys():
                    if trial_counter[member.id] == 0:
                        await ctx.send("Trial Count cannot be less than 0")
                    else:
                        trial_counter[member.id] -= 1
                        save_trial_count()
                        await ctx.send(f"Trial count for {member.display_name} is now {trial_counter.get(member.id)}")
                else:
                    await ctx.send("You do not have the permissions for this.")
        except Exception as e:
            await ctx.send("Unable to decrease trial count")
            logging.error("Decrease Trial Count Error: " + str(e))

    @commands.command(name="count")
    async def check_trial_count(self, ctx: commands.Context):
        """Check how many BOK trials you have been in since the bot started counting"""
        try:
            global trial_counter
            if ctx.author.id in trial_counter.keys():
                await ctx.reply(f"Total runs for {ctx.author.display_name}: {trial_counter.get(ctx.author.id)}")
            else:
                trial_counter[ctx.author.id] = 0
                await ctx.reply(f"Total runs for {ctx.author.display_name}: {trial_counter.get(ctx.author.id)}")
                save_trial_count()
        except Exception as e:
            await ctx.send("Unable to check your trial runs")
            logging.error("Check Trial Count Error: " + str(e))


def setup(bot: commands.Bot):
    bot.add_cog(Trial(bot))
