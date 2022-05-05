import asyncio
import nextcord
from nextcord.ext import commands, tasks
import random
import logging
import datetime

logging.basicConfig(level=logging.INFO)


# Singular function to get random trials depending on what is currently doable by the guild.

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


class Things(commands.Cog, name="Fun Things"):
    """For Fun/Event Type Things"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logging.info("Things cog loaded")
        self.scheduled_good_morning.start()

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

    @commands.command()
    async def youtube(self, ctx: commands.Context):
        """Links you to the BOK Trials Playlist"""
        await ctx.send('https://youtube.com/playlist?list=PL-z7L6gs44NMN_fDzsZY-3RRwaxHzxCBQ')

    @commands.command()
    async def lore(self, ctx: commands.Context):
        """Shows a random lore tidbit"""
        ran = random.randint(1, 10)  # Update to account for number of files
        grab = str(ran)
        grab += ".txt"
        with open('Lore/' + grab, ) as l:
            message = l.read()
        await ctx.send(message)

    @commands.command()
    async def joke(self, ctx: commands.Context):
        """Tells a Joke"""
        ran = random.randint(1, 11)  # Update to account for number of files
        grab = str(ran)
        grab += ".txt"
        with open('Jokes/' + grab, encoding="utf8") as l:
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
        await ctx.send(
            'https://media.discordapp.net/attachments/911730032286785536/932434215058944000/Slash_Fisted.PNG')

    @commands.command()
    async def chainz(self, ctx: commands.Context):
        """He always loses it"""
        await ctx.send('New phone who dis?')

    @commands.command()
    async def pizza(self, ctx: commands.Context):
        """Pizza Pizza"""
        await ctx.send('https://youtu.be/0YgW-05_y3A')

    @commands.command()
    async def drakrez(self, ctx: commands.Context):
        """When he gets the highest rezzes instead of someone else"""
        await ctx.send('https://youtu.be/uRbLz8COzHg')

    @commands.command()
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

    @commands.command(name="getarma")
    async def get_arma(self, ctx: commands.Context):
        """Gets Arma with a series of DMs and pings in case he forgets again"""
        role = nextcord.utils.get(ctx.message.author.guild.roles, name="Storm Bringers")
        user = ctx.message.author
        if user in role.members:
            try:
                arma = ctx.message.guild.get_member(152077378317844480)
                if arma:
                    for i in range(4):
                        await arma.send("It is time for your regularly scheduled event")
                        await ctx.send(arma.mention + " it is time for you to get on!")
                        await asyncio.sleep(.5)

                else:
                    await ctx.send("Cannot find Arma")
            except Exception as e:
                await ctx.send("I cannot call Arma")
                logging.error("Call Arma error: " + str(e))
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(name="twitch")
    async def get_twitch_url(self, ctx: commands.context):
        """Share Draks Twitch URL"""
        try:
            await ctx.send("https://www.twitch.tv/drakadorx")
        except Exception as e:
            await ctx.send("Unable to send link.")
            logging.error("Print Twitch Error: " + str(e))

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
And a quiet old guild-mom who was whispering “hush”

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
And goodnight to the guild-mom whispering “hush”
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

    @tasks.loop(time=datetime.time(13, 0, 0, 0))  # UTC Time, remember to convert and use a 24 hour-clock.
    async def scheduled_good_morning(self):
        channel = self.bot.get_guild(574095793414209556).get_channel(574095793414209558)
        await channel.send("Good Morning!")

    @commands.command()
    async def joined(self, ctx: commands.context):
        """Tells you when you joined the server"""
        try:
            user = ctx.message.author
            await ctx.reply(f"You, {user.display_name} joined {ctx.guild.name} on {user.joined_at}")
        except Exception as e:
            logging.error("Joined command error: " + str(e))
            await ctx.send("Unable to fetch joined information.")


#    @tasks.loop(time=datetime.time(12, 0, 0, 0))
#    async def arma_reminder(self, bot):
#        """An automated task to remind Arma to do stuff"""
#        # Check if it is Monday at Noon
#        if datetime.today().weekday() == 0:
#            guild = bot.get_guild(id=574095793414209556)
#            arma = guild.get_member(152077378317844480)
#            if arma:
#                await arma.send("Reminder to go and look at Guild Traders")


def setup(bot: commands.Bot):
    bot.add_cog(Things(bot))
