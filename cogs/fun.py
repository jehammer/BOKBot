import discord
from discord.ext import commands, tasks
import random
import logging
import datetime
import calendar

# For using Aliases: (name="ex", aliases=["al1", "al2"])

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


class Fun(commands.Cog, name="Fun Things"):
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

    @tasks.loop(time=datetime.time(14, 0, 0, 0))  # UTC Time, remember to convert and use a 24 hour-clock.
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

    @commands.command(name="wrap")
    async def create_bubblewrap(self, ctx: commands.context):
        """For all your popping needs"""
        message = f"||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop||\n" \
                  f"||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop||\n" \
                  f"||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop||\n" \
                  f"||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop|| ||pop||"
        await ctx.send(message)

    @commands.command(name="rng")
    async def rng(self, ctx: commands.Context):
        """RNG In vAA HM"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730139770019921/RNG.gif')

    @commands.command(name="vundees")
    async def vundees_moment(self, ctx: commands.Context):
        """He splooged."""
        try:
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730140604678204/Vundees.gif')
        except Exception as e:
            await ctx.send("Unable to send image")
            logging.error("Vundees error: " + str(e))

    @commands.command(name="fishing")
    async def fishing(self, ctx: commands.Context):
        """Glub Glub"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/976527850524016650/Fishing.gif')

    @commands.command(name="dance")
    async def dance(self, ctx: commands.Context):
        """A little jiggle"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730135919628328/Dance.gif')

    @commands.command(name="f")
    async def f(self, ctx: commands.Context):
        """F"""
        await ctx.send('https://tenor.com/view/keyboard-hyperx-rgb-hyperx-family-hyperx-gaming-gif-17743649')

    @commands.command(name="jabs")
    async def jabs(self, ctx: commands.Context):
        """The Templars do be like that"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911837712196173824/jabs.gif')

    @commands.command(name="facepalm")
    async def facepalm(self, ctx: commands.Context):
        """Arma every other second"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/912569604973404160/Facepalm.gif')

    @commands.command(name="hummus")
    async def hummus(self, ctx: commands.Context):
        """It's what Drak likes"""
        await ctx.send('https://tenor.com/view/hummus-hummusyes-hummushappy-gif-8630288')

    @commands.command(name="maja")
    async def maja(self, ctx: commands.Context):
        """How she be after we kick her butt"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/932433681992278088/Creed.gif')

    @commands.command(name="lost")
    async def lost(self, ctx: commands.Context):
        """Then he was lost!"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/975825818506903562/Lost_died.gif')

    @commands.command(name="dungeons")
    async def dungeons(self, ctx: commands.Context):
        """DUNGEONS"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/983363613425278997/dungeons.gif')

    @commands.command(name="youtube")
    async def youtube(self, ctx: commands.Context):
        """Links you to the BOK Trials Playlist"""
        await ctx.send('https://youtube.com/playlist?list=PL-z7L6gs44NMN_fDzsZY-3RRwaxHzxCBQ')

    @commands.command(name="lore")
    async def lore(self, ctx: commands.Context):
        """Shows a random lore tidbit"""
        ran = random.randint(1, 10)  # Update to account for number of files
        grab = str(ran)
        grab += ".txt"
        with open('Lore/' + grab, ) as l:
            message = l.read()
        await ctx.send(message)

    @commands.command(name="joke")
    async def joke(self, ctx: commands.Context):
        """Tells a Joke"""
        ran = random.randint(1, 11)  # Update to account for number of files
        grab = str(ran)
        grab += ".txt"
        with open('Jokes/' + grab, encoding="utf8") as l:
            message = l.read()
        await ctx.send(message)

    @commands.command(name="otter")
    async def otter(self, ctx: commands.Context):
        """Adder"""
        await ctx.send('Adder')

    @commands.command(name="adder")
    async def adder(self, ctx: commands.Context):
        """Otter"""
        await ctx.send('Otter')

    @commands.command(name="vka")
    async def vka(self, ctx: commands.Context):
        """Something you wanna see for vKA"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911837688141856768/congaline.png')

    @commands.command(name="lewd")
    async def lewd(self, ctx: commands.Context):
        """Be wary, very lewd option"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911776421473550346/interlocking.gif')

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
        """He always loses it"""
        try:
            await ctx.send('https://tenor.com/view/e40-tellmewhentogo-gif-21713338')
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"Chainz error: {str(e)}")

    @commands.command(name="pizza")
    async def pizza(self, ctx: commands.Context):
        """Pizza Pizza"""
        await ctx.send('https://youtu.be/0YgW-05_y3A')

    @commands.command(name="rezparse")
    async def rezparse(self, ctx: commands.Context):
        """When drak gets the highest rezzes instead of someone else"""
        await ctx.send('https://youtu.be/uRbLz8COzHg')

    @commands.command(name="philosophy")
    async def philosophy(self, ctx: commands.Context):
        """The philosophy of Drak"""
        await ctx.send(
            "All Healers are soft mommy doms \nAll Tanks are masochists \nAll DPS are sadistic \n - Drak the Wise, "
            "who ponders his orb.")

    @commands.command()
    async def translate(self, ctx: commands.Context):
        """For the Boomers to understand Drak"""

        await ctx.send("Pog/Poggers: A triumphant cry of celebration. \nBased: The opposite of cringe. "
                       "\nRedpilled: To have seen reality for what it is. \nBaller: Very nice"
                       "\nNo Cap: An expression of authenticity."
                       "\nSussy Baka: An insincere comment saying summon is a suspicious fool, said as a joke."
                       "\nBussin: Same as Baller")

    @commands.command(name="twitch")
    async def get_twitch_url(self, ctx: commands.context):
        """Share Draks Twitch URL"""
        try:
            await ctx.send("https://www.twitch.tv/drakadorx")
        except Exception as e:
            await ctx.send("Unable to send link.")
            logging.error("Print Twitch Error: " + str(e))

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

    @commands.command()
    async def morning(self, ctx: commands.context):
        """A way to say good morning to bok"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/970733506948890655/sleepy-sleep.gif')

    @commands.command(name="arma")
    async def get_arma_moment(self, ctx: commands.Context):
        """Arma Moments"""
        try:
            ran = random.randint(1, 2)
            match ran:
                case 1:
                    await ctx.send(
                        'https://media.discordapp.net/attachments/911730032286785536/911730134044794930/Arma.gif')
                case 2:
                    await ctx.send('https://youtu.be/SQ9oCUNNbxc')
        except Exception as e:
            await ctx.send("Unable to send image")
            logging.error("Arma error: " + str(e))

    @commands.command(name="drak")
    async def get_drak_moment(self, ctx: commands.Context):
        """Drak Moment"""
        try:
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730136628461589/Drak.gif')
        except Exception as e:
            await ctx.send("Unable to send gif")
            logging.error("Drak error: " + str(e))

    @commands.command(name="abbr")
    async def dm_trial_abbreviations(self, ctx: commands.Context):
        """DMs the User the Trial abbreviations"""
        message = f"n - Normal\n" \
                  f"v - Veteran\n" \
                  f"+[#] - How many Minis are up for the Arena type Trials\n" \
                  f"hm - Hard Mode\n" \
                  f"hrc - Hel Ra Citadel\n" \
                  f"aa - Atherian Archive\n" \
                  f"so - Sanctum Ophidia\n" \
                  f"mol - Maw of Lorkhaj\n" \
                  f"hof - Halls of Fabrication\n" \
                  f"as - Asylum Sanctorium\n" \
                  f"cr - Cloud Rest\n" \
                  f"ss - Sunspire\n" \
                  f"ka - Kyne's Aegis\n" \
                  f"rg - Rockgrove\n" \
                  f"dsr - Dreadsail Reef"
        author = ctx.author
        await author.send(message)

    @commands.command(name="mommy")
    async def mommy(self, ctx: commands.Context):
        """You know you like it, you dirty little gamer"""
        try:
            await ctx.send("https://media.discordapp.net/attachments/911730032286785536/985284353359749190/mommy.png")
        except Exception as e:
            await ctx.send("Unable to send image")
            logging.error(f"Mommy error: {str(e)}")

    @commands.command(name="r34")
    async def a_very_funny_prank(self, ctx: commands.Context):
        """Links to all the R34 that Drak has found for you dirty people"""
        try:
            await ctx.send("https://cdn.discordapp.com/attachments/911730032286785536/985383946718150716/yes.png")
        except Exception as e:
            await ctx.send("Unable to send the stuff")
            logging.error(f"R34 error: {str(e)}")

    @commands.command(name="bever")
    async def bever_moment(self, ctx: commands.Context):
        """Bever stuff"""
        try:
            await ctx.send("https://media.discordapp.net/attachments/911730032286785536/987806807386894336/Bever.png")
        except Exception as e:
            await ctx.send("Unable to send the image")
            logging.error(f"Bever error: {str(e)}")

    @commands.command(name="reef")
    async def reef_image(self, ctx: commands.Context):
        """Helpful image for DSR"""
        try:
            await ctx.send("https://media.discordapp.net/attachments/911730032286785536/990441515979505714/Reef.png")
        except Exception as e:
            await ctx.send("Unable to send the image")
            logging.error(f"Reef error: {str(e)}")

    @commands.command(name="vas", aliases=["nas", "as"])
    async def as_gif(self, ctx: commands.Context):
        """Kite gif for AS"""
        try:
            await ctx.send("https://media.discordapp.net/attachments/911730032286785536/913342788907716628/vAS.gif")
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"AS Gif error: {str(e)}")

    @commands.command(name="wiped", aliases=["wipe"])
    async def wipe_meme(self, ctx: commands.Context):
        """Funny thing for when you wipe"""
        try:
            await ctx.send("https://cdn.discordapp.com/attachments/911730032286785536/999758223110320168/Wipe.png")
        except Exception as e:
            await ctx.send("Unable to send the image")
            logging.error(f"Wipe error: {str(e)}")

    @commands.command(name="logz")
    async def logz(self, ctx: commands.Context):
        """Actual gif of him"""
        try:
            await ctx.send("LISTEN HERE SHITHEADS!")
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730138935349308/Logz.gif')
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"Logz error: {str(e)}")

    @commands.command(name="phone")
    async def phone(self, ctx: commands.Context):
        """You got a new one"""
        try:
            await ctx.send("New phone who dis?")
        except Exception as e:
            await ctx.send("Unable to send the message")
            logging.error(f"Phone error: {str(e)}")

    @commands.command(name="auddy")
    async def auddy_moment(self, ctx: commands.Context):
        """It tickled the snoot"""
        try:
            await ctx.send("https://media.discordapp.net/attachments/911730032286785536/911730135034646558/Auddy.gif")
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"Auddy error: {str(e)}")

    @commands.command(name="sr")
    async def send_message_into_chat(self, ctx: commands.Context):
        """Just a fun little thing"""
        try:
            if ctx.message.author.id == 212634819190849536:
                msg = ctx.message.content
                msg = msg.split(" ", 2)
                guild = self.bot.get_guild(574095793414209556)
                channel = guild.get_channel(int(msg[1]))
                await channel.send(msg[2])
            else:
                await ctx.send(f"You do not have permission to do this.")
        except Exception as e:
            await ctx.send("Unable to send the message")
            logging.error("sr error:" + str(e))

    @commands.command(name='hrc', aliases=['vhrc', 'hrchm', 'vhrchm'])
    async def send_hrc_gif(self, ctx: commands.Context):
        """A helpful gif for vHRC HM"""
        try:
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/1043799209771548683/HRC_HM.gif')
        except Exception as e:
            await ctx.send("Unable to send the message")
            logging.error(f"HRC gif error: {str(e)}")

    @commands.command(name="dracus", aliases=["drac"])
    async def send_dracus_image(self, ctx: commands.Context):
        """His joke was ruined"""
        try:
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/1046640340641271838/Dracus.png')
        except Exception as e:
            await ctx.send("Unable to send the image")
            logging.error(f"Dracus Image error: {str(e)}")

    @commands.command(name="bocket")
    async def send_bocket_image(self, ctx: commands.Context):
        """Dracus! Chains!"""
        try:
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/1050804078202077274/bocket.png')
        except Exception as e:
            await ctx.send("Unable to send the image")
            logging.error(f"Bocket Image error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))