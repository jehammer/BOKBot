from nextcord.ext import commands
import random
import logging


# Singular function to get random zones
def get_zone():
    loop = True
    last4 = []
    while loop:
        ran = random.randint(1, 10)
        if ran not in last4:
            loop = False
    zone = ""
    match ran:
        case 1:
            zone = "EP - Bal Foyen, Blackrock, Deshaan, Eastmarch, The Rift, Shadowfen, Stonefalls"
        case 2:
            zone = "DC - Alik'r Desert, Bangkorai, Betnikh, Glenumbra, Rivenspire, Stormhaven, Stros M'Kai"
        case 3:
            zone = "AD - Auridon, Grahtwood, Greenshade, Khenarthi's Roost, Malabal Tor, Reaper's March"
        case 4:
            zone = "Craglorn"
        case 5:
            zone = "Coldharbour, Wrothgar"
        case 6:
            zone = "Daedric War Storyline - Vvardenfell, Clockwork City, Summerset, Artaeum"
        case 7:
            zone = "Season of the Dragon - North Elsweyr, Southern Elsweyr "
        case 8:
            zone = "Dark Heart of Skyrim - Western Skyrim, The Reach, Blackreach Caverns, Arkthzand Cavern"
        case 9:
            zone = "Gates Of Oblivion - Blackwood, Fargrave, Deadlands"
        case 10:
            zone = "Gold Coast, Hew's Bane, Murkmire"
    if len(last4) < 4:
        last4.append(ran)
    else:
        last4.pop()
        last4.append(ran)
    logging.info("Last4 overland: " + str(last4))
    return zone


def get_trial(cap):
    loop = True
    last4 = []
    while loop:
        ran = random.randint(1, cap)
        if ran not in last4:
            loop = False
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
        # TODO: Add in Dreadsail Reef as an option when High Isle releases
    if len(last4) < 4:
        last4.append(ran)
    else:
        last4.pop()
        last4.append(ran)
    logging.info("Status of last4: " + str(last4))
    return trial


# Function to get a random event to do
def get_event():
    ran = random.randint(1, 3)
    eve = ""
    match ran:
        case 1:
            eve = "Shyshard Hunt - " + get_zone()
        case 2:
            eve = "World Boss Crawl - " + get_zone()
        case 3:
            eve = "Overland - " + get_zone()
    return eve


class Overland(commands.Cog, name="Events"):
    """For Overland Type Stuff"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logging.info("Overland cog loaded")

    @commands.command()
    async def event(self, ctx: commands.Context):
        """Gives you a random event and zone to do"""
        await ctx.send(get_event())

    @commands.command()
    async def zone(self, ctx: commands.Context):
        """Gives you a random zone to do for your event"""
        await ctx.send(get_zone())

    # Get a trial randomly chosen
    @commands.command()
    async def ntrial(self, ctx: commands.Context):
        """Gives you a random normal trial to do"""
        trial = get_trial(10)
        await ctx.send("Normal " + trial)
        logging.info("Random normal generated: " + trial)

    @commands.command()
    async def vtrial(self, ctx: commands.Context):
        """Gives you a random veteran trial to do"""
        trial = get_trial(10)
        await ctx.send("Veteran " + trial)

    @commands.command()
    async def hmtrial(self, ctx: commands.Context):
        """Gives you a random veteran hm trial to do"""
        trial = get_trial(4)
        await ctx.send("Veteran " + trial + " HM")


def setup(bot: commands.Bot):
    bot.add_cog(Overland(bot))
