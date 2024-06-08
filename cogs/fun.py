import discord
from discord.ext import commands
from discord import app_commands
import logging
import datetime
import time
import calendar
import random
from pymongo import MongoClient

from services import Utilities, Librarian

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")

global ranks



def set_channels(config):
    """Function to set the MongoDB information on cog load"""
    global ranks
    client = MongoClient(config['mongo'])
    database = client['bot']
    ranks = database.ranks


def update_db(user_id, info):
    rec = ranks.find_one({'userID': user_id})
    if rec is None:
        rec = {
            'userID': user_id,
            'data': info.get_data()
        }
        ranks.insert_one(rec)
    else:
        new_rec = {'$set': {'data': info.get_data()}}
        ranks.update_one({'userID': user_id}, new_rec)


def load_rank(user_id):
    rec = ranks.find_one({'userID': user_id})
    if rec is not None:
        info = Rankings(rec['data']['count'], rec['data']['last_called'], rec['data']['lowest'], rec['data']['highest'],
                        rec['data']['doubles'], rec['data']['singles'], rec['data']['six_nine'],
                        rec['data']['four_twenty'], rec['data']['boob'])
    elif rec is None:
        info = Rankings(0, "Never", 1000000000, 0, 0, 0, 0, 0, 0)
    return info


class Rankings:
    """A class object to store and manage ranking information"""

    def __init__(self, count, last_called, lowest, highest, doubles, singles, six_nine, four_twenty, boob):
        self.count = count
        self.last_called = last_called
        self.lowest = lowest
        self.highest = highest
        self.doubles = doubles
        self.singles = singles
        self.six_nine = six_nine
        self.four_twenty = four_twenty
        self.boob = boob

    def get_data(self):
        all_data = {
            "count": self.count,
            "last_called": self.last_called,
            "lowest": self.lowest,
            "highest": self.highest,
            "doubles": self.doubles,
            "singles": self.singles,
            "six_nine": self.six_nine,
            "four_twenty": self.four_twenty,
            "boob": self.boob
        }
        return all_data


class Fun(commands.Cog, name="Fun"):
    """For Fun/Event Type Things"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        set_channels(self.bot.config)

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

    @commands.command(name="joined")
    async def joined(self, ctx: commands.context, m: discord.Member = None):
        """Tells you when you joined the server in M-D-Y Format"""
        try:
            if m is None:
                user = ctx.message.author
                await ctx.reply(f"According to the records you joined {ctx.guild.name} on "
                                f"{calendar.month_name[user.joined_at.month]} {user.joined_at.day}{Utilities.suffix(user.joined_at.day)}"
                                f"{user.joined_at.year}")
            else:
                await ctx.reply(f"According to the records {m.display_name} joined {ctx.guild.name} on "
                                f"{calendar.month_name[m.joined_at.month]} {m.joined_at.day}{Utilities.suffix(m.joined_at.day)}"
                                f"{m.joined_at.year}")
        except Exception as e:
            logging.error("Joined command error: " + str(e))
            await ctx.send("Unable to fetch joined information.")

    @commands.command(name="fishing")
    async def fishing(self, ctx: commands.Context):
        """Glub Glub"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/1219447029688959067/FishFishes.gif')

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

    @commands.command(name="pizza")
    async def pizza_video(self, ctx: commands.Context):
        """Leahs favorite early morning/late night meal."""
        try:
            await ctx.send('https://youtu.be/SMkG2FDCQ7w')
        except Exception as e:
            await ctx.send("Unable to send the link")
            logging.error(f"Pizza Error: {str(e)}")

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

    @commands.command(name="cover")
    async def my_bok_cover(self, ctx: commands.Context):
        """Put this over your chat when you stream!"""
        try:
            await ctx.send(
                'https://cdn.discordapp.com/attachments/911730032286785536/1219457387640000612/BOK_Stream_Cover.png')
        except Exception as e:
            await ctx.send("Unable to send the picture")
            logging.error(f"Cover Picture error: {str(e)}")

    @app_commands.command(name="rank", description="See how much BOKBot approves of you today.")
    @app_commands.describe(member="Discord user to rank if not yourself.")
    async def rank_app_command(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
        """Ranks someone out of 10000 you ping"""
        try: # TODO: Change the vanity checks to be in a dictonary and do an in-check or something to make it less of an if-else
            if member is None:
                member = interaction.user
            timestamp = int(time.mktime(datetime.datetime.now().timetuple()))  # All this just for a utc timestamp int
            ran = random.randint(1, 10000)
            user_id = member.id
            info = load_rank(user_id)
            info.last_called = f"<t:{timestamp}:f>"
            info.count += 1

            # Lowest and Highest check
            if info.lowest > ran:
                info.lowest = ran
            if info.highest < ran:
                info.highest = ran

            # 69 420, 8008 check
            if ran == 69:
                info.six_nine += 1
            elif ran == 420:
                info.four_twenty += 1
            elif ran == 8008:
                info.boob += 1

            listed = [int(x) for x in str(ran)]

            # Check for Singles
            listed_set = set(listed)
            if len(set(listed_set)) <= 1:  # This is single
                info.singles += 1

            # Check for Doubles
            if (len(listed) == 4 and str(listed[0]) + str(listed[1]) == str(listed[2]) + str(listed[3])) or \
                    (len(listed) == 2 and str(listed[0]) == str(listed[1])):
                info.doubles += 1

            update_db(user_id, info)

            await interaction.response.send_message(f"{member.display_name} ranks {Utilities.suffix(ran)}!")

        except IOError as e:
            await interaction.response.send_message(f"Sorry, I was unable to load or save your new information.")
            logging.error(f"Rank Command Error: {str(e)}")
        except Exception as e:
            await interaction.response.send_message("Sorry, I was unable to complete the command")
            logging.error(f"Rank Command Error: {str(e)}")

    @app_commands.command(name="kowtow", description="Check someones Ranking records")
    @app_commands.describe(member="Discord user to check if not yourself.")
    async def send_rank_info_app_command(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
        """Prints a leaderboard for your /rank uses"""
        try:
            if member is None:
                member = interaction.user
            user_id = member.id
            rec = ranks.find_one({'userID': user_id})
            if rec is None:
                await interaction.response.send_message(f"{member.display_name} has not been ranked before, there is no information.")
                return
            info = load_rank(user_id)
            embed = discord.Embed(
                title=member.display_name,
                color=discord.Color.red()
            )
            embed.set_footer(text="Be sure to get ranked again!")
            embed.set_author(name=f"Rank Information Board")
            embed.add_field(name=f"Total Times Ranked: {info.count}", value=" ", inline=False)
            embed.add_field(name=f"Last Ranked: {info.last_called}", value=" ", inline=False)
            embed.add_field(name=f"Lowest Rank: {info.lowest}", value=" ", inline=False)
            embed.add_field(name=f"Highest Rank: {info.highest}", value=" ", inline=False)
            embed.add_field(name=f"Doubles: {info.doubles}", value=" ", inline=False)
            embed.add_field(name=f"Singles: {info.singles}", value=" ", inline=False)
            embed.add_field(name=f"69 Count: {info.six_nine}", value=" ", inline=False)
            embed.add_field(name=f"420 Count: {info.four_twenty}", value=" ", inline=False)
            embed.add_field(name=f"Boob Count: {info.boob}", value=" ", inline=False)
            await interaction.response.send_message(embed=embed)

        except IOError as e:
            await interaction.response.send_message(f"I was unable to load your rank information.")
            logging.error(f"Kowtow Error: {str(e)}")
        except Exception as e:
            await interaction.response.send_message(f"Sorry, I was unable to complete the command.")
            logging.error(f"Kowtow Error: {str(e)}")


    @commands.command(name="kowtow", hidden=True)
    async def send_kowtow_notice(self, ctx: commands.Context):
        await ctx.reply(f"This has moved to the /kowtow application command.\n"
                        f"Keep an eye out for future re-use of this ! command.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
