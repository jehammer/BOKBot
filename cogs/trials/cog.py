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
    def addDPS(self, nDps, pClass = " "):
        if len(self.tDps) < 8:
            self.tDps[nDps] = pClass
        else:
            self.oDps[nDps] = pClass

    def addHealer(self, nHealer, pClass = " "):
        if len(self.tHealers) < 2:
            self.tHealers[nHealer] = pClass
        else:
            self.oHealers[nHealer] = pClass

    def addTank(self, nTank, pClass = " "):
        if len(self.tTanks) < 2:
            self.tTanks[nTank] = pClass
        else:
            self.oTanks[nTank] = pClass
    
    def bDPS(self, nDps, pClass = " "):
        self.oDps[nDps] = pClass

    def bHealer(self, nHealer, pClass = " "):
        self.oHealers[nHealer] = pClass
    
    def bTank(self, nTank, pClass = " "):
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
        self.bot = bot

    #@commands.command()
    #async def gif(self, ctx: commands.Context):
    #    """Checks for a response from the bot"""
    #    await ctx.send("Here is a gif")

    @commands.command()
    async def trial(self, ctx: commands.Context,leader,trial,date,time):
        """Creates a new trial for BOK"""
        leader = leader.replace(',','')
        trial = trial.replace(',','')
        date = date.replace(',','')
        time = time.replace(',','')

        #create random number id for the trial and verify it is not in use
        #loop = True
        #while(loop):
        #    ran = random.randint(1000, 9999)
        #    if ran in storage:
        #        pass
        #    else:
        #        loop = False

        ran = ctx.message.channel.id #use the id of the text channel to make a channel-specific trial listing
        embed = nextcord.Embed(
            title = trial + " " + date,
            description = time,
            color = nextcord.Color.blue()
        )
        embed.set_footer(text="Remember to spay or neuter your support!")
        embed.set_author(name=leader)
        embed.add_field(name="Healers", value='To Heal Us', inline='False')
        embed.add_field(name="Tanks", value='To Be Stronk', inline='False')
        embed.add_field(name="DPS", value='To Stand In Stupid', inline='False')
        #sent_embed = ctx.send(embed=embed)
        await ctx.send(embed=embed)

        #create new trial and put it in storage for later use
        newTrial = EsoTrial(trial, date, time, leader)
        storage[ran] = newTrial
        saveToDoc()
        

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
                        await ctx.send("Error, please type it as !su [type], [optional message]")
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
                    await ctx.send("Error, please type it as !su [type], [optional message]")
                    worked = False
            if worked == True:
                #Update trial
                storage[num] = trial
                await ctx.send(ctx.message.author.mention + " Added!")
                saveToDoc()
        except:
            await ctx.send("Error, Incorrect Trial? Please Consult Posting Guide or notify Drak.")

    @commands.command()
    async def bu(self, ctx: commands.Context):
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
                        await ctx.send("Error, please type it as !bu [type], [optional message]")
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
                    await ctx.send("Error, please type it as !bu [type], [optional message]")
                    worked = False
            if worked == True:
                #Update trial
                storage[num] = trial
                saveToDoc()
                await ctx.send(ctx.author.mention + " Added for Backup!")
        except:
            await ctx.send("Error, Incorrect Trial? Please Consult Posting Guide or notify Drak.")
    
    @commands.command()
    async def wd(self, ctx: commands.Context):
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
        try:
            num = ctx.message.channel.id
            trial = storage.get(num)
            trial.fillSpots()
            storage[num] = trial
            saveToDoc()
            await ctx.send("Spots filled!")
        except:
            await ctx.send("Something has gone wrong! Consult Drak!")
                 

    @commands.command()
    async def status(self, ctx: commands.Context):
        num = ctx.message.channel.id
        dCount = 0
        hCount = 0
        tCount = 0
        trial = storage.get(num)

        embed = nextcord.Embed(
            title = trial.trial + " " + trial.date,
            description = trial.time,
            color = nextcord.Color.blue()
        )
        embed.set_footer(text="Remember to spay or neuter your support!")
        embed.set_author(name=trial.leader)
        names = ""

        for i in trial.tHealers:
            names += i + " " + trial.tHealers[i] + "\n\n"
            hCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Healers", value = names, inline='False')
        names = ""
        for i in trial.tTanks:
            names += i + " " + trial.tTanks[i] + "\n\n"
            tCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Tanks", value = names, inline='False')
        names = ""
        for i in trial.tDps:
            names += i + " " + trial.tDps[i] + "\n\n"
            dCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="DPS", value = names, inline='False')
        names = "Healers: " + str(hCount) + "\nTanks: " + str(tCount) + "\nDPS: " + str(dCount)
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
        names = ""

        for i in trial.oHealers:
            names += i + " " + trial.oHealers[i] + "\n\n"
            hCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Healers", value = names, inline='False')
        names = ""
        for i in trial.oTanks:
            names += i + " " + trial.oTanks[i] + "\n\n"
            tCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Tanks", value = names, inline='False')
        names = "" 
        for i in trial.oDps:
            names += i + " " + trial.oDps[i] + "\n\n"
            dCount += 1
        if len(names) == 0:
            names = "None"
        embed.add_field(name="DPS", value = names, inline='False')

        names = "Healers: " + str(hCount) + "\nTanks: " + str(tCount) + "\nDPS: " + str(dCount)
        embed.add_field(name="Total", value = names, inline='False')
        await ctx.send(embed=embed) 

    @commands.command()
    async def msg(self, ctx: commands.Context):
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
        msg = ""
        if len(storage) > 0:
            for i in storage:
                msg += str(i) + "\n"
        else:
            msg = "None"
        await ctx.send(msg)

    @commands.command()
    async def end(self, ctx: commands.Context):
        try:
            num = ctx.message.channel.id
            del storage[num]
            await ctx.send("Trial Closed!")
        except:
            await ctx.send("Error! Trial not deleted!")

    @commands.command()
    async def gather(self, ctx: commands.Context):
        try:
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
        except:
            await ctx.send("Error! Idk something went wrong!")

    @commands.command()
    async def save(self, ctx: commands.Context):
        if ctx.message.author.name == "Drakador":
            try:
                saveToDoc()
                #with open('outputfile', 'w') as fout:
                #    json.dump(toDump, fout)
            except Exception as e:
                await ctx.send("Error, issue saving. Have Drak try to fix.")

    @commands.command()
    async def load(self, ctx: commands.Context):
        if ctx.message.author.name == "Drakador":
            try:
                global storage
                dbfile = open('trialStorage.pkl', 'rb')
                allData = pickle.load(dbfile)
                #with open('outputfile', 'r') as fin:
                #    allData = json.load(fin)
                for i in range(len(allData)):
                    # 0: trial, 1: date, 2: time, 3: leader, 4: tDps = {}, 
                    # 5: tHealers = {}, 6: tTanks = {}, 7: oDps = {}, 8: oHealers = {}, 9: oTanks = {}
                    storage[allData[i][0]] = EsoTrial(allData[i][1][0],allData[i][1][1],allData[i][1][2],allData[i][1][3],
                        allData[i][1][4],allData[i][1][5],allData[i][1][6],allData[i][1][7],allData[i][1][8],allData[i][1][9])

                dbfile.close()
                await ctx.send("Loaded!")
            except Exception as e:
                await ctx.send("Error, data not loaded. Have Drak check code.")

    #This verifies my idea will work, which is an incredibly stupid idea being done because I would rather see how complicated
    # I can make this section on a dare from a friend saying I wont do it. Please never do this. There are better ways out there.
    #@commands.command()
    #async def findUser(self, ctx: commands.Context):
    #    name = "Drakador"
    #    for i in ctx.guild.members:
    #        if i.name == name:
    #            await ctx.send(i.mention + " Found")



def setup(bot: commands.Bot):
    bot.add_cog(Trial(bot))
    