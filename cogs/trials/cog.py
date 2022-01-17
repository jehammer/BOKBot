import nextcord
from nextcord.ext import commands
import random


# Dictionary to store different embeds
storage = {}

#Special class to store trial in
class EsoTrial:
    """Class to hold trial information"""

    def __init__(self, trial, date, time, leader):
        self.trial = trial
        self.date = date
        self.time = time
        self.leader = leader
        self.tDps = {}
        self.tHealers = {}
        self.tTanks = {}
        self.oDps = {}
        self.oHealers  = {}
        self.oTanks = {}

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
            self.oHealer[nHealer] = pClass

    def addTank(self, nTank, pClass = " "):
        if len(self.tTanks) < 2:
            self.tTanks[nTank] = pClass
        else:
            self.oTank[nTank] = pClass
    
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
        if nTank in self.tTanksS:
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
            title = trial,
            description = date + " " + time,
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
        try:
            try:
                msg = ctx.message.content
                #print(msg)
                msg = msg.split(" ",2) #Split into 2 parts of a list
                #print (msg)
                num = ctx.message.channel.id
                trial = storage.get(num)
                if msg[1].lower() == "dps":
                    trial.addDPS(ctx.message.author,msg[2])
                elif msg[1].lower() == "healer":
                    trial.addHealer(ctx.message.author, msg[2])
                else:
                    trial.addTank(ctx.message.author, msg[2])
            except:
                msg = ctx.message.content
                #print(msg)
                msg = msg.split(" ",2) #Split into 2 parts of a list
                #print (msg)
                num = ctx.message.channel.id
                trial = storage.get(num)
                if msg[1].lower() == "dps":
                    trial.addDPS(ctx.message.author)
                elif msg[1].lower() == "healer":
                    trial.addHealer(ctx.message.author)
                else:
                    trial.addTank(ctx.message.author)       
            #Update trial
            storage[num] = trial
            await ctx.send(ctx.message.author.mention + " Added!")
        except:
            await ctx.send("Error, Incorrect Trial? Please Consult Posting Guide.")

    @commands.command()
    async def bu(self, ctx: commands.Context):
        try:
            try:
                msg = ctx.message.content
                #print(msg)
                msg = msg.split(" ",2) #Split into 2 parts of a list
                #print (msg)
                num = ctx.message.channel.id
                trial = storage.get(num)
                if msg[1].lower() == "dps":
                    trial.bDPS(ctx.message.author,msg[2])
                elif msg[1].lower() == "healer":
                    trial.bHealer(ctx.message.author, msg[2])
                else:
                    trial.bTank(ctx.message.author, msg[2])
            except:
                msg = ctx.message.content
                #print(msg)
                msg = msg.split(" ",2) #Split into 2 parts of a list
                #print (msg)
                num = ctx.message.channel.id
                trial = storage.get(num)
                if msg[1].lower() == "dps":
                    trial.bDPS(ctx.message.author)
                elif msg[1].lower() == "healer":
                    trial.bHealer(ctx.message.author)
                else:
                    trial.bTank(ctx.message.author)       
            #Update trial
            storage[num] = trial
            await ctx.send(ctx.message.author.mention + " Added for Backup!")
        except:
            await ctx.send("Error, Incorrect Trial? Please Consult Posting Guide.")
    #@commands.command()
    #async def getName(self, ctx: commands.Context):
    #    await ctx.send(ctx.message.author.name)
    
    @commands.command()
    async def wd(self, ctx: commands.Context):
        num = ctx.message.channel.id
        trial = storage.get(num)
        if ctx.message.author in trial.tDps.keys() or ctx.message.author in trial.oDps.keys():
            trial.removeDPS(ctx.message.author)
        elif ctx.message.author in trial.tHealers.keys() or ctx.message.author in trial.oHealers.keys():
            trial.removeHealer(ctx.message.author)
        else:
            trial.removeTank(ctx.message.author)
        await ctx.send(ctx.message.author.mention + " removed :(")

    @commands.command()
    async def fill(self, ctx: commands.Context):
        num = ctx.message.channel.id
        trial = storage.get(num)
        trial.fillSpots()       

    @commands.command()
    async def status(self, ctx: commands.Context):
        num = ctx.message.channel.id

        trial = storage.get(num)

        embed = nextcord.Embed(
            title = trial.trial,
            description = trial.date + " " + trial.time,
            color = nextcord.Color.blue()
        )
        embed.set_footer(text="Remember to spay or neuter your support!")
        embed.set_author(name=trial.leader)
        names = ""

        for i in trial.tHealers:
            names += i.name + " " + trial.tHealers[i] + "\n"
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Healers", value = names, inline='False')
        names = ""
        for i in trial.tTanks:
            names += i.name + " " + trial.tTanks[i] + "\n"
        if len(names) == 0:
            names = "None"
        embed.add_field(name="Tanks", value = names, inline='False')
        names = "" 
        for i in trial.tDps:
            names += i.name + " " + trial.tDps[i] + "\n"
        if len(names) == 0:
            names = "None"
        embed.add_field(name="DPS", value = names, inline='False')
        await ctx.send(embed=embed)        

    @commands.command()
    async def msg(self, ctx: commands.Context):
        trial = storage.get(ctx.message.channel.id)
        found = True
        msg = ctx.message.content
        msg = msg.split(" ",1)
        msg = msg[1]
        if ctx.message.author in trial.tDps.keys():
            trial.tDps[ctx.message.author] = msg
        elif ctx.message.author in trial.oDps:
            trial.oDps[ctx.message.author] = msg
        elif ctx.message.author in trial.tHealers:
            trial.oDps[ctx.message.author] = msg
        elif ctx.message.author in trial.oHealers:
            trial.oDps[ctx.message.author] = msg
        elif ctx.message.author in trial.tTanks:
            trial.oDps[ctx.message.author] = msg
        elif ctx.message.author in trial.oTanks:
            trial.oDps[ctx.message.author] = msg
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
                names += i.mention + "\n"
            if len(trial.tHealers) == 0:
                names += "None " + "\n"

            names += "\nTanks \n"
            for i in trial.tTanks:
                names += i.mention + "\n"
            if len(trial.tTanks) == 0:
                names += "None" + "\n"
            
            names += "\nDPS \n"
            for i in trial.tDps:
                names += i.mention + "\n"   
            if len(trial.tDps) == 0:
                names += "None" + "\n"

            await ctx.send(names)
            await ctx.send("It is go time!")
            del storage[num]
        except:
            await ctx.send("Error! Idk something went wrong!")



def setup(bot: commands.Bot):
    bot.add_cog(Trial(bot))
    