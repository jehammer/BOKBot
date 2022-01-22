import nextcord
from nextcord.ext import commands
import pickle

#TODO: Actually comment through this stuff. 

# Dictionary to store different embeds
storage = {}

#Special class to store trial in
class EsoTrial():
    """Class to hold trial information"""

    def __init__(self, trial, date, time, leader, tDps = {}, tHealers = {}, tTanks = {}, oDps = {}, oHealers = {}, oTanks = {}):
        self.trial = trial
        self.date = date
        self.time = time
        self.leader = leader
        self.tDps = tDps
        self.tHealers = tHealers
        self.tTanks = tTanks
        self.oDps = oDps
        self.oHealers  = oHealers
        self.oTanks = oTanks


    def getData(self):
        allData = [self.trial, self.date, self.time, self.leader, self.tDps, self.tHealers, self.tTanks,
            self.oDps, self.oHealers, self.oTanks]
        return allData
    #Add people into the right spots
    def addDPS(self, nDps, pClass = "will be sadistic"):
        if len(self.tDps) < 8:
            self.tDps[nDps] = pClass
        else:
            self.oDps[nDps] = pClass

    def addHealer(self, nHealer, pClass = "will be soft mommy dom"):
        if len(self.tHealers) < 2:
            self.tHealers[nHealer] = pClass
        else:
            self.oHealers[nHealer] = pClass

    def addTank(self, nTank, pClass = "will be masochistic"):
        if len(self.tTanks) < 2:
            self.tTanks[nTank] = pClass
        else:
            self.oTanks[nTank] = pClass
    
    def bDPS(self, nDps, pClass = "could be sadistic"):
        self.oDps[nDps] = pClass

    def bHealer(self, nHealer, pClass = "could be soft mommy dom"):
        self.oHealers[nHealer] = pClass
    
    def bTank(self, nTank, pClass = "could be masochistic"):
        self.oTanks[nTank] = pClass

    #remove people from right spots
    def removeDPS(self, nDps):
        if nDps in self.tDps:
            del self.tDps[nDps]
        else:
            del self.oDps[nDps]

    def removeHealer(self, nHealer):
        if nHealer in self.tHealers:
            del self.tHealers[nHealer]
        else:
            del self.oHealers[nHealer]

    def removeTank(self, nTank):
        if nTank in self.tTanks:
            del self.tTanks[nTank]
        else:
            del self.oTanks[nTank]

    #Fill the roster with overflow people
    def fillSpots(self):
        loop = True
        while (loop):
            if len(self.tDps) < 8 and len(self.oDps) > 0:
                first = list(self.oDps.keys())[0]
                self.tDps[first] = self.oDps.get(first)
                del self.oDps[first]
            else:
                loop = False
        loop = True
        while (loop):
            if len(self.tHealers) < 2 and len(self.oHealers) > 0:
                first = list(self.oHealers.keys())[0]
                self.tHealers[first] = self.oHealers.get(first)
                del self.oHealers[first]
            else:
                loop = False
        loop = True
        while (loop):
            if len(self.tTanks) < 2 and len(self.oTanks) > 0:
                first = list(self.oTanks.keys())[0]
                self.tTanks[first] = self.oTanks.get(first)
                del self.oTanks[first]
            else:
                loop = False

def saveToDoc():
    try:
        global storage
        dbfile = open('trialStorage.pkl', 'wb')
        toDump = []
        for key in storage:
            toDump.append([key, storage[key].getData()])
        pickle.dump(toDump, dbfile)
        dbfile.close()
    except:
        print("Error, shit didnt work")

class Trial(commands.Cog, name="Trials"):
    """Recieves trial commands"""

    def __init__(self, bot: commands.Bot):
        try:
            global storage
            dbfile = open('trialStorage.pkl', 'rb')
            allData = pickle.load(dbfile)
            for i in range(len(allData)):
                # 0: trial, 1: date, 2: time, 3: leader, 4: tDps = {}, 
                # 5: tHealers = {}, 6: tTanks = {}, 7: oDps = {}, 8: oHealers = {}, 9: oTanks = {}
                storage[allData[i][0]] = EsoTrial(allData[i][1][0],allData[i][1][1],allData[i][1][2],allData[i][1][3],
                    allData[i][1][4],allData[i][1][5],allData[i][1][6],allData[i][1][7],allData[i][1][8],allData[i][1][9])

            dbfile.close()
            print("Loaded!")
        except Exception as e:
            print(e)
        self.bot = bot

    #@commands.command()
    #async def gif(self, ctx: commands.Context):
    #    """Checks for a response from the bot"""
    #    await ctx.send("Here is a gif")

    @commands.command()
    async def trial(self, ctx: commands.Context):
        """Creates a new trial for BOK | format: !trial [leader],[trial],[date info],[time]"""

        try:
            msg = ctx.message.content
            msg = msg.split(" ",1) #Split into 2 parts of a list, the first space then the rest
            msg = msg[1] #drop the !trial part
            leader,trial,date,time = msg.split(",")

            ran = ctx.message.channel.id #use the id of the text channel to make a channel-specific trial listing
            embed = nextcord.Embed(
                title = trial + " " + date + " " + time,
                description = "I hope people sign up for this.",
                color = nextcord.Color.blue()
            )
            embed.set_footer(text="Remember to spay or neuter your support!")
            embed.set_author(name=leader)
            embed.add_field(name="Healers", value='To Heal Us', inline='False')
            embed.add_field(name="Tanks", value='To Be Stronk', inline='False')
            embed.add_field(name="DPS", value='To Stand In Stupid', inline='False')
            await ctx.send(embed=embed)

            #create new trial and put it in storage for later use
            newTrial = EsoTrial(trial, date, time, leader, tDps = {}, tHealers = {}, tTanks = {}, oDps = {}, oHealers = {}, oTanks = {})
            storage[ran] = newTrial
            saveToDoc()
        except Exception as e:
            await ctx.send(e)#"Errror, please use !help trial if you are having problems or notify Drak")
            

#    @commands.command()
#    async def displayembed(self, ctx: commands.Context):
#        embed = nextcord.Embed(
#            title = 'Title ',
#            description = 'This is a description',
#            color = nextcord.Color.blue()
#        )
#        embed.set_footer(text="This is a footer")
#        embed.set_image(url='https://cdn.discordapp.com/attachments/911730032286785536/911837688141856768/congaline.png')
#        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/911730032286785536/911837688141856768/congaline.png')
#        embed.set_author(name='me', icon_url='https://cdn.discordapp.com/attachments/911730032286785536/911837688141856768/congaline.png')
#        embed.add_field(name="Healers", value='Healers', inline='False')
#        embed.add_field(name="Tanks", value='Tanks', inline='False')
#        embed.add_field(name="DPS", value='DPS', inline='False')
#        await ctx.send(embed=embed)

    @commands.command()
    async def su(self, ctx: commands.Context):
        """Use !su [role] [optional message]"""
        worked = True
        global storage
        try:
            try:
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
                    #Works if there is the optional message
                    msg = ctx.message.content
                    msg = msg.split(" ",2) #Split into 2 parts of a list
                    if msg[1].lower() == "dps":
                        trial.addDPS(ctx.message.author.name,msg[2])
                    elif msg[1].lower() == "healer":
                        trial.addHealer(ctx.message.author.name, msg[2])
                    elif msg[1].lower() == "tank":
                        trial.addTank(ctx.message.author.name, msg[2])
                    else:
                        await ctx.send("Error, please type it as !su [type] [optional message]")
                        worked = False
            except:
                #Works without optional message. 
                msg = ctx.message.content
                msg = msg.split(" ",1) #Split into 2 parts of a list
                num = ctx.message.channel.id
                trial = storage.get(num)
                if msg[1].lower() == "dps":
                    trial.addDPS(ctx.message.author.name)
                elif msg[1].lower() == "healer":
                    trial.addHealer(ctx.message.author.name)
                elif msg[1].lower() == "tank":
                    trial.addTank(ctx.message.author.name)
                else:
                    await ctx.send("Error, please type it as !su [type] [optional message]")
                    worked = False
            if worked == True:
                #Update trial
                storage[num] = trial
                await ctx.send(ctx.message.author.mention + " Added!")
                saveToDoc()
        except:
            await ctx.send("Error, please type it as !su [type] [optional message]. If you did this please notify Drak")

    @commands.command()
    async def bu(self, ctx: commands.Context):
        """Use !bu [role] [optional message]"""
        worked = True        
        try:
            try:
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
                    msg = msg.split(" ",2) #Split into 2 parts of a list
                    if msg[1].lower() == "dps":
                        trial.bDPS(ctx.message.author.name,msg[2])
                    elif msg[1].lower() == "healer":
                        trial.bHealer(ctx.message.author.name, msg[2])
                    elif msg[1].lower() == "tank":
                        trial.bTank(ctx.message.author.name, msg[2])
                    else:
                        await ctx.send("Error, please type it as !bu [type] [optional message]")
                        worked = False
            except:
                msg = ctx.message.content
                msg = msg.split(" ",2) #Split into 2 parts of a list
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
            if worked == True:
                #Update trial
                storage[num] = trial
                saveToDoc()
                await ctx.send(ctx.author.mention + " Added for Backup!")
        except:
            await ctx.send("Error, please type it as !bu [type] [optional message]. If you did this please notify Drak")
    
    @commands.command()
    async def wd(self, ctx: commands.Context):
        """Use !wd to remove yourself from the roster. If you are in several spots use several times"""
        try:
            worked = True
            num = ctx.message.channel.id
            trial = storage.get(num)
            if ctx.message.author.name in trial.tDps.keys() or ctx.message.author.name in trial.oDps.keys():
                trial.removeDPS(ctx.message.author.name)
            elif ctx.message.author.name in trial.tHealers.keys() or ctx.message.author.name in trial.oHealers.keys():
                trial.removeHealer(ctx.message.author.name)
            elif ctx.message.author.name in trial.tTanks.keys() or ctx.message.author.name in trial.oTanks.keys():
                trial.removeTank(ctx.message.author.name)
            else:
                worked = False
                await ctx.send("You are not signed up for this Trial")
            if worked == True:
                for i in ctx.guild.members:
                    if i.name == ctx.message.author.name:               
                        await ctx.send(ctx.message.author.mention + " removed :(")
                storage[num] = trial
                saveToDoc()
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
                trial.fillSpots()
                storage[num] = trial
                saveToDoc()
                await ctx.send("Spots filled!")
            except:
                await ctx.send("Something has gone wrong! Consult Drak!")
        else:
            await ctx.send("You must be a Storm Bringer to fill a roster.")
                 

    @commands.command()
    async def status(self, ctx: commands.Context):
        """Prints out a list of all who are signed up as main and backups"""
        num = ctx.message.channel.id
        dCount = 0
        hCount = 0
        tCount = 0
        trial = storage.get(num)

        embed = nextcord.Embed(
            title = trial.trial + " " + trial.date + " " + trial.time,
            description = "This battle will be legendary!", #trial.time,
            color = nextcord.Color.green()
        )
        embed.set_footer(text="Remember to spay or neuter your support!")
        embed.set_author(name=trial.leader)
        
        # HEALERS
        names = ""
        #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="Healer")
        for i in trial.tHealers:
            names += "<:Healer:933835785352904864>"+ i + " " + trial.tHealers[i]  + " " + "\r\n"
            #names += "\r\n"
            hCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Healers", value = names, inline='False')
        
        #TANKS
        names = ""
        #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="Tank")
        for i in trial.tTanks:
            names += "<:Tank:933835838951948339>"+ i + " " + trial.tTanks[i]  + " " + "\r\n"
            #names += "\r\n"
            tCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Tanks", value = names, inline='False')

        #DPS
        names = ""
        #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="DPS")
        for i in trial.tDps:
            names += "<:DPS:933835811684757514>"+ i + " " + trial.tDps[i] + " " + "\r\n"
            #names += "\r\n"
            dCount += 1
        if len(names) == 0:
            names = "None"

        embed.add_field(name="DPS", value = names, inline='False')
        names = "Healers: " + str(hCount) + " \nTanks: " + str(tCount) + " \nDPS: " + str(dCount)
        embed.add_field(name="Total", value = names, inline='False')
        await ctx.send(embed=embed)        

        #Show Backup/Overflow
        dCount = 0
        hCount = 0
        tCount = 0
        embed = nextcord.Embed(
            title = "Backups",
            #description = " ",
            color = nextcord.Color.orange()
        )
        embed.set_footer(text="Remember to beep when backing up that dumptruck")
        #embed.set_author(name=trial.leader)
        #BACKUP HEALERS
        names = ""
        #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="Healer")
        for i in trial.oHealers:
            names += "<:Healer:933835785352904864>"+ i + " " + trial.oHealers[i] + "\r\n"
            hCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Healers", value = names, inline='False')
        
        #BACKUP TANKS
        names = ""
        #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="Tank")
        for i in trial.oTanks:
            names += "<:Tank:933835838951948339>"+ i + " " + trial.oTanks[i] + "\r\n"
            tCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Tanks", value = names, inline='False')

        #BACKUP DPS
        names = "" 
        #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="DPS")
        for i in trial.oDps:
            names += "<:DPS:933835811684757514>"+ i + " " + trial.oDps[i] + "\r\n"
            dCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="DPS", value = names, inline='False')

        names = "Healers: " + str(hCount) + "\nTanks: " + str(tCount) + "\nDPS: " + str(dCount)
        embed.add_field(name="Total", value = names, inline='False')
        await ctx.send(embed=embed) 

    @commands.command()
    async def msg(self, ctx: commands.Context):
        """!msg [message] to modify your message in the embed"""
        trial = storage.get(ctx.message.channel.id)
        found = True
        msg = ctx.message.content
        msg = msg.split(" ",1)
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

    @commands.command()
    async def listTrials(self, ctx: commands.Context):
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
            user = ctx.message.author
            if user in role.members:
                num = ctx.message.channel.id
                trial = storage.get(num)
                names = "\nHealers \n"
                for i in trial.tHealers:
                    for j in ctx.guild.members:
                        if i == j.name:
                            names += j.mention + "\n" 
                if len(trial.tHealers) == 0:
                    names += "None " + "\n"

                names += "\nTanks \n"
                for i in trial.tTanks:
                    for j in ctx.guild.members:
                        if i == j.name:
                            names += j.mention + "\n" 
                if len(trial.tTanks) == 0:
                    names += "None" + "\n"
                
                names += "\nDPS \n"
                for i in trial.tDps:
                    for j in ctx.guild.members:
                        if i == j.name:
                            names += j.mention + "\n"   
                if len(trial.tDps) == 0:
                    names += "None" + "\n"

                await ctx.send(names)
                await ctx.send("It is go time!")
                del storage[num]
                saveToDoc()
            else:
                await ctx.send("You do not have permission for that.")
        except:
            await ctx.send("Error! Idk something went wrong!")

    @commands.command()
    async def save(self, ctx: commands.Context):
        """Saves roster data to storage"""
        if ctx.message.author.id == 212634819190849536:
            try:
                saveToDoc()
                await ctx.send("Saved!")
            except Exception as e:
                await ctx.send("Error, issue saving. Have Drak try to fix.")
        else:
            await ctx.send("You do not have permission to do that.")

    @commands.command()
    async def load(self, ctx: commands.Context):
        """Loads the trials from storage into the bot"""
        if ctx.message.author.id == 212634819190849536:
            try:
                global storage
                dbfile = open('trialStorage.pkl', 'rb')
                allData = pickle.load(dbfile)
                for i in range(len(allData)):
                    # 0: trial, 1: date, 2: time, 3: leader, 4: tDps = {}, 
                    # 5: tHealers = {}, 6: tTanks = {}, 7: oDps = {}, 8: oHealers = {}, 9: oTanks = {}
                    storage[allData[i][0]] = EsoTrial(allData[i][1][0],allData[i][1][1],allData[i][1][2],allData[i][1][3],
                        allData[i][1][4],allData[i][1][5],allData[i][1][6],allData[i][1][7],allData[i][1][8],allData[i][1][9])

                dbfile.close()
                await ctx.send("Loaded!")
            except Exception as e:
                await ctx.send("Error, data not loaded. Have Drak check code.")
        else:
            await ctx.send("You do not have permission to do that.")


    @commands.command()
    async def check(self, ctx: commands.Context):
        """Check the status of the pickle"""
        if ctx.message.author.id == 212634819190849536:
            try:
                global storage
                dbfile = open('trialStorage.pkl', 'rb')
                allData = pickle.load(dbfile)
                print(allData)
                dbfile.close()
            except Exception as e:
                await ctx.send("Error, data not loaded. Have Drak check code.")
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
                saveToDoc()
                await ctx.send("The butt has been wiped.")
            except Exception as e:
                await ctx.send("Error, data not cleaned.")
                print(e)
        else:
            await ctx.send("You do not have permission to do that.")

    @commands.command()
    async def check(self, ctx: commands.Context, num):
        """To see the status of an orphan"""
        if ctx.message.author.id == 212634819190849536:
            try:
                num = int(num)
                global storage
                trial = storage.get(num)
                #TODO: Make a single function for all this stuff.
                dCount = 0
                hCount = 0
                tCount = 0
                embed = nextcord.Embed(
                    title = trial.trial + " " + trial.date + " " + trial.time,
                    description = "This battle will be legendary!", #trial.time,
                    color = nextcord.Color.green()
                )
                embed.set_footer(text="Remember to spay or neuter your support!")
                embed.set_author(name=trial.leader)
                
                # HEALERS
                names = ""
                #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="Healer")
                for i in trial.tHealers:
                    names += "<:Healer:933835785352904864>"+ i + " " + trial.tHealers[i]  + " " + "\r\n"
                    #names += "\r\n"
                    hCount += 1
                if len(names) == 0:
                    names = "None"
                embed.add_field(name="Healers", value = names, inline='False')
                
                #TANKS
                names = ""
                #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="Tank")
                for i in trial.tTanks:
                    names += "<:Tank:933835838951948339>"+ i + " " + trial.tTanks[i]  + " " + "\r\n"
                    #names += "\r\n"
                    tCount += 1
                if len(names) == 0:
                    names = "None"
                embed.add_field(name="Tanks", value = names, inline='False')

                #DPS
                names = ""
                #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="DPS")
                for i in trial.tDps:
                    names += "<:DPS:933835811684757514>"+ i + " " + trial.tDps[i] + " " + "\r\n"
                    #names += "\r\n"
                    dCount += 1
                if len(names) == 0:
                    names = "None"

                embed.add_field(name="DPS", value = names, inline='False')
                names = "Healers: " + str(hCount) + " \nTanks: " + str(tCount) + " \nDPS: " + str(dCount)
                embed.add_field(name="Total", value = names, inline='False')
                await ctx.send(embed=embed)        

                #Show Backup/Overflow
                dCount = 0
                hCount = 0
                tCount = 0
                embed = nextcord.Embed(
                    title = "Backups",
                    #description = " ",
                    color = nextcord.Color.orange()
                )
                embed.set_footer(text="Remember to beep when backing up that dumptruck")
                #embed.set_author(name=trial.leader)
                #BACKUP HEALERS
                names = ""
                #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="Healer")
                for i in trial.oHealers:
                    names += "<:Healer:933835785352904864>"+ i + " " + trial.oHealers[i] + "\r\n"
                    hCount += 1
                if len(names) == 0:
                    names = "None"
                embed.add_field(name="Healers", value = names, inline='False')
                
                #BACKUP TANKS
                names = ""
                #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="Tank")
                for i in trial.oTanks:
                    names += "<:Tank:933835838951948339>"+ i + " " + trial.oTanks[i] + "\r\n"
                    tCount += 1
                if len(names) == 0:
                    names = "None"
                embed.add_field(name="Tanks", value = names, inline='False')

                #BACKUP DPS
                names = "" 
                #emoji = nextcord.utils.get(ctx.message.guild.emojis, name="DPS")
                for i in trial.oDps:
                    names += "<:DPS:933835811684757514>"+ i + " " + trial.oDps[i] + "\r\n"
                    dCount += 1
                if len(names) == 0:
                    names = "None"
                embed.add_field(name="DPS", value = names, inline='False')

                names = "Healers: " + str(hCount) + "\nTanks: " + str(tCount) + "\nDPS: " + str(dCount)
                embed.add_field(name="Total", value = names, inline='False')
                await ctx.send(embed=embed) 

            except Exception as e:
                await ctx.send(e)
        else:
            await ctx.send("You do not have permission to do that.")

def setup(bot: commands.Bot):
    bot.add_cog(Trial(bot))