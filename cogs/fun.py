import discord
from discord.ext import commands, tasks
from discord import app_commands
import logging
import datetime
import calendar
import random

# For using Aliases: (name="ex", aliases=["al1", "al2"])

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


def ordinalSuffix(number):
    # 11, 12, and 13 have the suffix th:
    if number % 100 in (11, 12, 13):
        return str(number) + 'th'
    # Numbers that end with 1 have the suffix st:
    if number % 10 == 1:
        return str(number) + 'st'
    # Numbers that end with 2 have the suffix nd:
    if number % 10 == 2:
        return str(number) + 'nd'
    # Numbers that end with 3 have the suffix rd:
    if number % 10 == 3:
        return str(number) + 'rd'
    # All other numbers end with th:
    return str(number) + 'th'


class Fun(commands.Cog, name="Fun"):
    """For Fun/Event Type Things"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduled_good_morning.start()

    @commands.command(name="8ball")
    async def magic_eight_ball(self, ctx: commands.context):
        """Answers a question like a magic 8-ball"""
        # responses from here: https://en.wikipedia.org/wiki/Magic_8-ball#Possible_answers
        try:
            ran = random.randint(1, 20)
            response = ""
            match ran:
                case 1:
                    response = "It is certain."
                case 2:
                    response = "It is decidedly so."
                case 3:
                    response = "Without a doubt."
                case 4:
                    response = "Yes definitely."
                case 5:
                    response = "You may rely on it."
                case 6:
                    response = "As I see it, yes."
                case 7:
                    response = "Most likely."
                case 8:
                    response = "Outlook good."
                case 9:
                    response = "Yes."
                case 10:
                    response = "Signs point to yes."
                case 11:
                    response = "Reply hazy, try again."
                case 12:
                    response = "Ask again later."
                case 13:
                    response = "Better not tell you now."
                case 14:
                    response = "Cannot predict now."
                case 15:
                    response = "Concentrate and ask again."
                case 16:
                    response = "Don't count on it."
                case 17:
                    response = "My reply is no."
                case 18:
                    response = "My sources say no."
                case 19:
                    response = "Outlook not so good."
                case 20:
                    response = "Very doubtful. "
            if ran % 2 == 1:
                ran = random.randint(1, 10)  # Give this a like 1 in 10 chance of showing up if the number is odd
                if ran == 2:
                    response = "Fuck off I am sleeping."

            await ctx.reply(response)
        except Exception as e:
            await ctx.send("Unable to use the magic, something is blocking it!")
            logging.error("Magic 8 Ball Error: " + str(e))

    @tasks.loop(
        time=datetime.time(13, 0, 0, 0))  # UTC Time, remember to convert and use a 24 hour-clock CDT: 13, CST: 14.
    async def scheduled_good_morning(self):
        try:
            guild = self.bot.get_guild(self.bot.config['guild'])
            channel = guild.get_channel(self.bot.config['morning_channel'])
            await channel.send(self.bot.config['morning'])
            try:
                today = datetime.datetime.today()
                today_month = today.month
                today_day = today.day
                today_year = today.year
                for member in guild.members:
                    joined = member.joined_at
                    joined_month = joined.month
                    joined_day = joined.day
                    joined_year = joined.year
                    if today_month == joined_month and today_day == joined_day and today_year > joined_year:
                        await channel.send(f"{member.mention} Happy Anniversary!")
            except Exception as e:
                await channel.send("Unable to get the Anniversaries.")
                logging.error(f"Good Morning Task Anniversary Error: {str(e)}")
        except Exception as e:
            logging.error(f"Good Morning Task Error: {str(e)}")

    @commands.command(name="joined")
    async def joined(self, ctx: commands.context, m: discord.Member = None):
        """Tells you when you joined the server in M-D-Y Format"""
        try:
            def suffix(d):
                return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

            if m is None:
                user = ctx.message.author
                await ctx.reply(f"According to the records you joined {ctx.guild.name} on "
                                f"{calendar.month_name[user.joined_at.month]} {user.joined_at.day}"
                                f"{suffix(user.joined_at.day)} {user.joined_at.year}")
            else:
                await ctx.reply(f"According to the records {m.display_name} joined {ctx.guild.name} on "
                                f"{calendar.month_name[m.joined_at.month]} {m.joined_at.day}"
                                f"{suffix(m.joined_at.day)} {m.joined_at.year}")
        except Exception as e:
            logging.error("Joined command error: " + str(e))
            await ctx.send("Unable to fetch joined information.")

    @commands.command(name="fishing")
    async def fishing(self, ctx: commands.Context):
        """Glub Glub"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/976527850524016650/Fishing.gif')

    @commands.command(name="dance")
    async def dance(self, ctx: commands.Context):
        """A little jiggle"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730135919628328/Dance.gif')

    @commands.command(name="jabs")
    async def jabs(self, ctx: commands.Context):
        """The Templars do be like that"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911837712196173824/jabs.gif')

    @commands.command(name="facepalm")
    async def facepalm(self, ctx: commands.Context):
        """Arma every other second"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/912569604973404160/Facepalm.gif')

    @commands.command(name="fart")
    async def fart(self, ctx: commands.Context):
        """Explosive"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/932433681992278088/Creed.gif')

    @commands.command(name="dungeons")
    async def dungeons(self, ctx: commands.Context):
        """DUNGEONS"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/983363613425278997/dungeons.gif')

    @commands.command(name="bokemon")
    async def bokemon(self, ctx: commands.Context):
        """A link to a perfect song"""
        await ctx.send('https://youtu.be/OZrs7Blmank')

    @commands.command(name="thepull")
    async def thepull(self, ctx: commands.Context):
        """Drak got the thing"""
        await ctx.send('https://youtu.be/Cnf9lRtLSYk')

    @commands.command(name="chainz", aliases=["chains"])
    async def chainz(self, ctx: commands.Context):
        """Just tell him"""
        try:
            await ctx.send('https://tenor.com/view/e40-tellmewhentogo-gif-21713338')
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"Chainz error: {str(e)}")

    @commands.command(name="pizza")
    async def pizza(self, ctx: commands.Context):
        """Pizza Pizza"""
        await ctx.send('https://youtu.be/0YgW-05_y3A')

    @commands.command()
    async def translate(self, ctx: commands.Context):
        """For the Boomers to understand Drak"""

        await ctx.send("Pog/Poggers: A triumphant cry of celebration. \nBased: The opposite of cringe. "
                       "\nRedpilled: To have seen reality for what it is. \nBaller: Very nice"
                       "\nNo Cap: An expression of authenticity."
                       "\nSussy Baka: An insincere comment saying summon is a suspicious fool, said as a joke."
                       "\nBussin: Same as Baller."
                       "\nFr: For Real, see: No Cap."
                       "\nOn God: Confirming or asking one is serious.")

    @commands.command()
    async def goodnight(self, ctx: commands.context):
        """A way to say goodnight to bok"""

        # Wow, this looks ugly, ah well. Say goodnight to the guildies
        message = """
In the great big room
There was a parse dummy backwards in the room
And a merchant buffoon.
And a picture of our first trial clear
And there were there were three little pvpers sitting on chairs
And two little kittens, and even two chickens
And even a Leah, asking for pizza at 1 AM
And a blacksmith and a clothier and a bowl full of alchemy
And a quiet old guild master who was whispering “hush”

Goodnight room
Goodnight moon
Goodnight parse dummy backwards in the room
Goodnight light
And the buffoon
Goodnight pvpers
Goodnight chairs
Goodnight kittens
And goodnight chickens
Goodnight clocks
And goodnight socks
Goodnight Leah
Goodnight blacksmith
And goodnight clothier
Goodnight nobody
Goodnight alchemy
And goodnight to the guild master whispering “hush”
Goodnight stars
Goodnight air
Goodnight noises everywhere
Goodnight BOK
"""
        await ctx.send(message)

    @commands.command(name="logz")
    async def logz(self, ctx: commands.Context):
        """Actual gif of him"""
        try:
            await ctx.send("LISTEN HERE SHITHEADS!")
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730138935349308/Logz.gif')
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"Logz error: {str(e)}")

    @commands.command(name="bocket")
    async def send_bocket_image(self, ctx: commands.Context):
        """Dracus! Chains!"""
        try:
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/1050804078202077274/bocket.png')
        except Exception as e:
            await ctx.send("Unable to send the image")
            logging.error(f"Bocket Image error: {str(e)}")

    @commands.command(name="ec")
    async def my_ec_gif(self, ctx: commands.Context):
        """You have it!"""
        try:
            await ctx.send(
                'https://cdn.discordapp.com/attachments/911730032286785536/1062132264382775296/DrakadorMyEC.gif')
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"EC GIF error: {str(e)}")

    @commands.command(name="noec")
    async def no_ec_gif(self, ctx: commands.Context):
        """You don't have it!"""
        try:
            await ctx.send(
                'https://cdn.discordapp.com/attachments/911730032286785536/1062132263980126250/DrakadorNoEC.gif')
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"NO EC GIF error: {str(e)}")

    @commands.command(name="noquestionsasked")
    async def no_questions_asked_gif(self, ctx: commands.Context):
        """Absolutely none."""
        try:
            await ctx.send('https://tenor.com/view/dont-ask-no-questions-gif-8052545')
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"No Questions Asked GIF error: {str(e)}")

    @app_commands.command(name="rank", description="This is an app command, use /rank @someone!")
    async def rank_app_command(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
        """Ranks someone out of 10000 you ping"""
        try:
            if member is None:
                await interaction.response.send_message(f"Hey! You need to @ someone!")
            ran = random.randint(1, 10000)
            await interaction.response.send_message(f"{member.mention} ranks {ordinalSuffix(ran)}!")
        except Exception as e:
            await interaction.response.send_message("Sorry, I was unable to complete the command")
            logging.error(f"Rank Command Error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
