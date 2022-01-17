from nextcord.ext import commands
import random

#Singular function to get random trials depending on what is currently doable by the guild.
def getTrial(cap):
    ran = random.randint(1, cap)
    trial = ""
    match ran:
        case 1:
            trial = "Hel Ra Citadel"
        case 2:
            trial = "Atherian Archive"
        case 3:
            trial = "Sanctum Ophidia"
        case 4:
            trial = "Maw of Lorkhaj"
        case 5:
            trial = "Sunspire"
        case 6:
            trial = "Asylum Sanctorium"
        case 7:
            trial = "Cloudrest"
        case 8:
            trial = "Halls of Fabrication"
        case 9:
            trial = "Kyne's Aegis"
        case 10:
            trial = "Rockgrove"
    return trial

class Things(commands.Cog, name="Fun Things"):
    """For Fun/Event Type Things"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # Get a trial randomly chosen
    @commands.command()
    async def ntrial(self, ctx: commands.Context):
        """Gives you a random normal trial to do"""
        trial = getTrial(10)
        await ctx.send("Normal " + trial)

    @commands.command()
    async def vtrial(self, ctx: commands.Context):
        """Gives you a random veteran trial to do"""
        trial = getTrial(6)
        await ctx.send("Veteran " + trial)

    @commands.command()
    async def hmtrial(self, ctx: commands.Context):
        """Gives you a random veteran hm trial to do"""
        trial = getTrial(3)
        await ctx.send("Veteran " + trial + " HM")

    @commands.command()
    async def youtube(self, ctx: commands.Context):
        """Links you to the BOK Trials Playlist"""
        await ctx.send('https://youtube.com/playlist?list=PL-z7L6gs44NMN_fDzsZY-3RRwaxHzxCBQ')

    @commands.command()
    async def lore(self, ctx: commands.Context):
        """Shows a random lore tidbit"""
        ran = random.randint(1, 4) #Update to account for number of files
        grab = str(ran)
        grab += ".txt"
        with open('Lore/'+ grab,) as l:
            message = l.read();
        await ctx.send(message)

    @commands.command()
    async def joke(self, ctx: commands.Context):
        """Tells a Joke"""
        ran = random.randint(1, 3) #Update to account for number of files
        grab = str(ran)
        grab += ".txt"
        with open('Jokes/'+ grab,encoding="utf8") as l:
            message = l.read()
        await ctx.send(message)

    @commands.command()
    async def vka(self, ctx: commands.Context):
        """Something you wanna see for vKA"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911837688141856768/congaline.png')

    @commands.command()
    async def lewd(self, ctx: commands.Context):
        """Be wary, very lewd option"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911776421473550346/interlocking.gif')

    @commands.command()
    async def bokemon(self, ctx: commands.Context):
        """A link to a perfect song"""
        await ctx.send('https://youtu.be/OZrs7Blmank')

    @commands.command()
    async def thepull(self, ctx: commands.Context):
        """Drak got the thing"""
        await ctx.send('https://youtu.be/Cnf9lRtLSYk')

    @commands.command()
    async def fisted(self, ctx: commands.Context):
        """It happens to all of us"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/932434215058944000/Slash_Fisted.PNG')

    @commands.command()
    async def chains(self, ctx: commands.Context):
        """He always loses it"""
        await ctx.send('New phone who dis?')
        
def setup(bot: commands.Bot):
    bot.add_cog(Things(bot))