from discord.ext import commands
import random
import logging

last4z = []
last4t = []


# Singular function to get random zones
def get_zone():
    loop = True
    while loop:
        ran = random.randint(1, 11)
        if ran not in last4z:
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
        case 11:
            zone = "Legacy of The Bretons - High Isle and Amenos, Galen and Y'ffelon"
    if len(last4z) < 4:
        last4z.append(ran)
    else:
        last4z.pop(0)
        last4z.append(ran)
    logging.info("Last4z overland: " + str(last4z))
    return zone


def get_trial(cap):
    loop = True
    while loop:
        ran = random.randint(1, cap)
        if ran not in last4t:
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
            trial = "Halls of Fabrication"
        case 6:
            trial = "Asylum Sanctorium"
        case 7:
            trial = "Cloudrest"
        case 8:
            trial = "Sunspire"
        case 9:
            trial = "Kyne's Aegis"
        case 10:
            trial = "Rockgrove"
        case 11:
            trial = "Dreadsail Reef"
    if len(last4t) < 4:
        last4t.append(ran)
    else:
        last4t.pop(0)
        last4t.append(ran)
    logging.info("Status of last4: " + str(last4t))
    return trial


# Function to get a random event to do
def get_event():
    ran = random.randint(1, 4)
    eve = ""
    match ran:
        case 1:
            eve = "Shyshard Hunt starting: " + get_zone()
        case 2:
            eve = "World Boss Crawl starting: " + get_zone()
        case 3:
            eve = "Overland starting: " + get_zone()
        case 4:
            eve = f"Public Dungeon Crawl starting: {get_zone()}"
    return eve


class Events(commands.Cog, name="Events"):
    """For PVE/PVP Type Stuff"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="event")
    async def event(self, ctx: commands.Context):
        """Gives you a random event and zone to do"""
        await ctx.send(get_event())

    @commands.command(name="zone")
    async def zone(self, ctx: commands.Context):
        """Gives you a random zone to do for your event"""
        await ctx.send(get_zone())

    # Get a trial randomly chosen
    @commands.command(name="ntrial")
    async def ntrial(self, ctx: commands.Context):
        """Gives you a random normal trial to do"""
        trial = get_trial(11)
        await ctx.send("Normal " + trial)
        logging.info("Random normal generated: " + trial)

    @commands.command(name="vtrial")
    async def vtrial(self, ctx: commands.Context):
        """Gives you a random veteran trial to do"""
        trial = get_trial(11)
        await ctx.send("Veteran " + trial)

    @commands.command(name="hmtrial")
    async def hmtrial(self, ctx: commands.Context):
        """Gives you a random veteran hm trial to do"""
        trial = get_trial(5)
        await ctx.send("Veteran " + trial + " HM")


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
