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


def setup(bot: commands.Bot):
    bot.add_cog(Overland(bot))
