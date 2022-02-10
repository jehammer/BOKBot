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
        # Plan for change:
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
        logging.info("Spots filled in trial id " + num)


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
            logging.info("Loaded Trials!")
        except Exception as e:
            logging.error("Error, unable to load:" + str(e))
        self.bot = bot

    # @commands.command()
    # async def gif(self, ctx: commands.Context):
    #    """Checks for a response from the bot"""
    #    await ctx.send("Here is a gif")

    @commands.command()
    async def trial(self, ctx: commands.Context):
        """Creates a new trial for BOK | format: !trial [leader],[trial],[date info],[time]"""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            role2 = nextcord.utils.get(ctx.message.author.guild.roles, name="Raid Lead")
            user = ctx.message.author
            if user in role.members or user in role2.members:
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
            else:
                await ctx.send("You do not have permission to do this.")
        except Exception as e:
            await ctx.send("Error, please use !help trial if you are having problems or notify Drak")
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
                        await ctx.send("Error, please type it as !su [type] [optional message]")
                        worked = False
            except Exception as e:  # TODO: work a way around the lack of an optional message
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
                    await ctx.send("Error, please type it as !su [type] [optional message]")
                    worked = False
            if worked:
                # Update trial
                storage[num] = trial
                await ctx.send(ctx.message.author.mention + " Added!")
                save_to_doc()
        except Exception as e:
            await ctx.send("Error, please type it as !su [type] [optional message]. If you did this please notify Drak")
            print("SU error:" + str(e))

    @commands.command()
    async def bu(self, ctx: commands.Context):
        """Use !bu [role] [optional message]"""
        worked = True
        try:
            try:
                # Plan for implementation:
                # If already in bu roster, say they cannot bu twice
                # IF in primary roster under the same role, swap from primary to bu
                # IF in primary roster under a different role, allow for sign up
                num = ctx.message.channel.id
                trial = storage.get(num)
                if ctx.message.author.name in trial.tDps.keys():
                    await ctx.send("You are already signed up as DPS!")
                    worked = False
                elif ctx.message.author.name in trial.oDps.keys():
                    await ctx.send("You are already signed up as backup DPS!")
                    worked = False
                elif ctx.message.author.name in trial.tHealers.keys():
                    await ctx.send("You are already signed up as a Healer!")
                    worked = False
                elif ctx.message.author.name in trial.oHealers.keys():
                    await ctx.send("You are already signed up as a backup Healer!")
                    worked = False
                elif ctx.message.author.name in trial.tTanks.keys():
                    await ctx.send("You are already signed up as a Tank!")
                    worked = False
                elif ctx.message.author.name in trial.oTanks.keys():
                    await ctx.send("You are already signed up as a backup Tank!")
                    worked = False
                else:
                    msg = ctx.message.content
                    msg = msg.split(" ", 2)  # Split into 2 parts of a list
                    if msg[1].lower() == "dps":
                        trial.bDPS(ctx.message.author.name, msg[2])
                    elif msg[1].lower() == "healer":
                        trial.bHealer(ctx.message.author.name, msg[2])
                    elif msg[1].lower() == "tank":
                        trial.bTank(ctx.message.author.name, msg[2])
                    else:
                        await ctx.send("Error, please type it as !bu [type] [optional message]")
                        worked = False
            except:
                msg = ctx.message.content
                msg = msg.split(" ", 2)  # Split into 2 parts of a list
                num = ctx.message.channel.id
                trial = storage.get(num)
                if msg[1].lower() == "dps":
                    trial.bDPS(ctx.message.author.name)
                elif msg[1].lower() == "healer":
                    trial.bHealer(ctx.message.author.name)
                elif msg[1].lower() == "tank":
                    trial.bTank(ctx.message.author.name)
                else:
                    await ctx.send("Error, please type it as !bu [type] [optional message]")
                    worked = False
            if worked:
                # Update trial
                storage[num] = trial
                save_to_doc()
                await ctx.send(ctx.author.mention + " Added for Backup!")
        except Exception as e:
            await ctx.send("Error, please type it as !bu [type] [optional message]. If you did this please notify Drak")
            print("Backup Error: " + str(e))

    @commands.command()
    async def wd(self, ctx: commands.Context):
        """Use !wd to remove yourself from the roster. This will remove you from both BU and Main rosters"""
        try:
            worked = False
            num = ctx.message.channel.id
            trial = storage.get(num)
            if ctx.message.author.name in trial.tDps.keys() or ctx.message.author.name in trial.oDps.keys():
                trial.remove_dps(ctx.message.author.name)
                worked = True
            if ctx.message.author.name in trial.tHealers.keys() or ctx.message.author.name in trial.oHealers.keys():
                trial.remove_healer(ctx.message.author.name)
                worked = True
            if ctx.message.author.name in trial.tTanks.keys() or ctx.message.author.name in trial.oTanks.keys():
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
        except:
            await ctx.send("Something has gone wrong! Consult Drak!")

    @commands.command()
    async def fill(self, ctx: commands.Context):
        """For trial leaders to fill the roster from the backup roster"""
        role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
        user = ctx.message.author
        if user in role.members:
            try:
                num = ctx.message.channel.id
                trial = storage.get(num)
                trial.fill_spots()
                storage[num] = trial
                save_to_doc()
                await ctx.send("Spots filled!")
            except:
                await ctx.send("Something has gone wrong! Consult Drak!")
        else:
            await ctx.send("You must be a Storm Bringer or Raid Lead to fill a roster.")

    @commands.command()
    async def status(self, ctx: commands.Context):
        """Prints out a list of all who are signed up as main and backups"""
        num = ctx.message.channel.id
        primary_embed, backup_embed = self.print_roster(num)

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
        if ctx.message.author.name in trial.tDps.keys():
            trial.tDps[ctx.message.author.name] = msg
        elif ctx.message.author.name in trial.oDps:
            trial.oDps[ctx.message.author.name] = msg
        elif ctx.message.author.name in trial.tHealers:
            trial.tHealers[ctx.message.author.name] = msg
        elif ctx.message.author.name in trial.oHealers:
            trial.oHealers[ctx.message.author.name] = msg
        elif ctx.message.author.name in trial.tTanks:
            trial.tTanks[ctx.message.author.name] = msg
        elif ctx.message.author.name in trial.oTanks:
            trial.oTanks[ctx.message.author.name] = msg
        else:
            await ctx.send("Error, are you in the trial?")
            found = False
        if found == True:
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
            await ctx.send("Error! Trial not deleted!")

    @commands.command()
    async def gather(self, ctx: commands.Context):
        """for raid leads, closes the roster and notifies everyone to come."""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            role2 = nextcord.utils.get(ctx.message.author.guild.roles, name="Raid Lead")
            user = ctx.message.author
            if user in role.members or user in role2.members:
                num = ctx.message.channel.id
                trial = storage.get(num)
                names = "\nHealers \n"
                for i in trial.trial_healers:
                    for j in ctx.guild.members:
                        if i == j.name:
                            names += j.mention + "\n"
                if len(trial.trial_ealers) == 0:
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
                await ctx.send("It is go time!")
                del storage[num]
                save_to_doc()
            else:
                await ctx.send("You do not have permission for that.")
        except:
            await ctx.send("Error! Idk something went wrong!")

    @commands.command()
    async def save(self, ctx: commands.Context):
        """Saves roster data to storage"""
        if ctx.message.author.id == 212634819190849536:
            try:
                save_to_doc()
                await ctx.send("Saved!")
            except Exception as e:
                await ctx.send("Error, issue saving. Have Drak try to fix.")
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
                    # 0: trial, 1: date, 2: time, 3: leader, 4: tDps = {}, 
                    # 5: tHealers = {}, 6: tTanks = {}, 7: oDps = {}, 8: oHealers = {}, 9: oTanks = {}
                    storage[all_data[i][0]] = EsoTrial(all_data[i][1][0], all_data[i][1][1], all_data[i][1][2],
                                                       all_data[i][1][3],
                                                       all_data[i][1][4], all_data[i][1][5], all_data[i][1][6],
                                                       all_data[i][1][7], all_data[i][1][8], all_data[i][1][9])

                db_file.close()
                await ctx.send("Loaded!")
            except Exception as e:
                await ctx.send("Error, data not loaded. Have Drak check code.")
        else:
            await ctx.send("You do not have permission to do that.")

    @commands.command()
    async def remove(self, ctx: commands.Context):
        """Removes someone from the roster"""
        try:
            role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
            role2 = nextcord.utils.get(ctx.message.author.guild.roles, name="Raid Lead")
            user = ctx.message.author
            if user in role.members or user in role2.members:
                found = False
                worked = True
                msg = ctx.message.content
                msg = msg.split(" ", 1)
                msg = msg[1]
                num = ctx.message.channel.id
                trial = storage.get(num)
                if msg in trial.tDps.keys() or msg in trial.oDps.keys():
                    trial.removeDPS(msg)
                    found = True
                if msg in trial.tHealers.keys() or msg in trial.oHealers.keys():
                    trial.removeHealer(msg)
                    found = True
                if msg in trial.tTanks.keys() or msg in trial.oTanks.keys():
                    trial.removeTank(msg)
                    found = True
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
            print(e)

    @commands.command()
    async def leader(self, ctx: commands.Context):
        """Replaces the leader of a trial"""
        role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
        role2 = nextcord.utils.get(ctx.message.author.guild.roles, name="Raid Lead")
        user = ctx.message.author
        if user in role.members or user in role2.members:
            pass

    @commands.command()
    async def check(self, ctx: commands.Context):
        """Check the status of the pickle"""
        if ctx.message.author.id == 212634819190849536:
            try:
                global storage
                db_file = open('trialStorage.pkl', 'rb')
                all_data = pickle.load(db_file)
                print(all_data)
                db_file.close()
            except Exception as e:
                await ctx.send("Error, data not loaded. Have Drak check code.")
                print("Check error: " + str(e))
        else:
            await ctx.send("You do not have permission to do that.")

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
                print(e)
        else:
            await ctx.send("You do not have permission to do that.")

    async def gather_people(self, num):
        trial = storage.get(num)
        names = "\nHealers \n"
        for i in trial.trial_healers:
            for j in ctx.guild.members:
                if i == j.name:
                    names += j.mention + "\n"
        if len(trial.trial_ealers) == 0:
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

    async def print_roster(self, num):
        num = int(num)
        global storage
        trial = storage.get(num)
        # TODO: Make a single function for all this stuff.
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
        for i in trial.tHealers:
            names += "<:Healer:933835785352904864>" + i + " " + trial.tHealers[i] + " " + "\r\n"
            # names += "\r\n"
            healer_count += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Healers", value=names, inline=False)

        # TANKS
        names = ""
        for i in trial.tTanks:
            names += "<:Tank:933835838951948339>" + i + " " + trial.tTanks[i] + " " + "\r\n"
            # names += "\r\n"
            tank_count += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Tanks", value=names, inline=False)

        # DPS
        names = ""
        for i in trial.tDps:
            names += "<:DPS:933835811684757514>" + i + " " + trial.tDps[i] + " " + "\r\n"
            # names += "\r\n"
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
        embed.set_footer(text="Remember to beep when backing up that dump truck")
        # embed.set_author(name=trial.leader)
        # BACKUP HEALERS
        names = ""
        for i in trial.oHealers:
            names += "<:Healer:933835785352904864>" + i + " " + trial.oHealers[i] + "\r\n"
            healer_count += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Healers", value=names, inline=False)

        # BACKUP TANKS
        names = ""

        for i in trial.oTanks:
            names += "<:Tank:933835838951948339>" + i + " " + trial.oTanks[i] + "\r\n"
            tank_count += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Tanks", value=names, inline=False)

        # BACKUP DPS
        names = ""
        for i in trial.oDps:
            names += "<:DPS:933835811684757514>" + i + " " + trial.oDps[i] + "\r\n"
            dps_count += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="DPS", value=names, inline=False)

        names = "Healers: " + str(healer_count) + "\nTanks: " + str(tank_count) + "\nDPS: " + str(dps_count)
        embed.add_field(name="Total", value=names, inline=False)

        return embed, embed2

    @commands.command()
    async def check(self, ctx: commands.Context, num):
        """To see the status of an orphan"""
        if ctx.message.author.id == 212634819190849536:
            try:
                num = int(num)
                # TODO: Make a single function for all this stuff.
                primary_embed, backup_embed = self.print_roster(num)

                await ctx.send(embed=primary_embed)
                await ctx.send(embed=backup_embed)

            except Exception as e:
                await ctx.send(e)
        else:
            await ctx.send("You do not have permission to do that.")


def setup(bot: commands.Bot):
    bot.add_cog(Trial(bot))
