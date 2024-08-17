from discord.ext import commands
import random
import logging

from services import Utilities

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


last4z = []
last4t = []

#TODO: Change zone and trial to use the multi-language support by printing each after second language is added.

def get_trial_option(cap):
    loop = True
    while loop:
        ran = random.randint(1, cap)
        if ran not in last4t:
            loop = False
    if len(last4t) < 4:
        last4t.append(ran)
    else:
        last4t.pop(0)
        last4t.append(ran)
    return ran-1


# Singular function to get random zones
def get_zone_option(cap):
    loop = True
    while loop:
        ran = random.randint(1, cap)
        if ran not in last4z:
            loop = False
    if len(last4z) < 4:
        last4z.append(ran)
    else:
        last4z.pop(0)
        last4z.append(ran)
    return ran-1

def get_event_option():
    options = ['SSH', 'WBC', 'PDC', 'OL']
    ran = random.randint(1, len(options))
    return options[ran-1]

class Events(commands.Cog, name="Events"):
    """For PVE/PVP Type Stuff"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="event")
    async def event(self, ctx: commands.Context):
        """Gives you a random event and zone to do"""
        user_language = Utilities.get_language(ctx.author)
        try:
            options = self.bot.language[user_language]['replies']['Zones']
            ran =  get_zone_option(len(options))
            event = get_event_option()
            await ctx.send(f"{self.bot.language[user_language]['replies']['Events'][event]} {options[ran]}")
        except Exception as e:
            await ctx.reply(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"Get Event Error: {str(e)}")

    @commands.command(name="zone")
    async def zone(self, ctx: commands.Context):
        """Gives you a random zone to do for your event"""
        """Gives you a random normal trial to do"""
        user_language = Utilities.get_language(ctx.author)
        try:
            options = self.bot.language[user_language]['replies']['Zones']
            ran =  get_zone_option(len(options))
            await ctx.send(f"{options[ran]}")
        except Exception as e:
            await ctx.reply(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"Get Zone Error: {str(e)}")

    # Get a trial randomly chosen
    @commands.command(name="ntrial")
    async def ntrial(self, ctx: commands.Context):
        """Gives you a random normal trial to do"""
        user_language = Utilities.get_language(ctx.author)
        try:
            options = self.bot.language[user_language]['replies']['Trials']
            ran =  get_trial_option(len(options))
            await ctx.send(f"{self.bot.language[user_language]['replies']['Events']['Norm']} {options[ran]}")
        except Exception as e:
            await ctx.reply(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"NTrial Error: {str(e)}")

    @commands.command(name="vtrial")
    async def vtrial(self, ctx: commands.Context):
        """Gives you a random veteran trial to do"""
        user_language = Utilities.get_language(ctx.author)
        try:
            options = self.bot.language[user_language]['replies']['Trials']
            ran =  get_trial_option(len(options))
            await ctx.send(f"{self.bot.language[user_language]['replies']['Events']['Vet']} {options[ran]}")
        except Exception as e:
            await ctx.reply(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"VTrial Error: {str(e)}")

    @commands.command(name="hmtrial")
    async def hmtrial(self, ctx: commands.Context):
        """Gives you a random veteran hm trial to do"""
        user_language = Utilities.get_language(ctx.author)
        try:
            options = self.bot.language[user_language]['replies']['Trials']
            ran =  get_trial_option(len(options))
            await ctx.send(f"{self.bot.language[user_language]['replies']['Events']['Vet']} {options[ran]} {self.bot.language[user_language]['replies']['Events']['HM']}")
        except Exception as e:
            await ctx.reply(f"{self.bot.language[user_language]['replies']['Unknown']}")
            logging.error(f"HMTrial Error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
