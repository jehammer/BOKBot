#!/usr/bin/python3
import nextcord
from nextcord.ext import commands
import os

intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="/", case_insensitive=True, intents=intents)

#Events
@bot.event
async def on_member_join(member):
    guild = member.guild
    await guild.system_channel.send(f'''Welcome {member.mention} to Breath Of Kynareth!
Winds of Kyne be with you, please react in <#847968244949844008> to join the rest of the server.
If the bot does not work just ping the Storm Bringers.''')

#Commands
@bot.command(name="setstat")
async def change_playing(ctx):
    await bot.change_presence(activity=nextcord.Game(name="Several Godslayer Progs"))

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")

if __name__ == '__main__':
    with open('Token.txt') as f:
        token = f.readline();
    # For loop to load all cog file
    for folder in os.listdir("cogs"):
        if os.path.exists(os.path.join("cogs", folder, "cog.py")):
            bot.load_extension(f"cogs.{folder}.cog") #If in a folder modules/ping/ it would be modules.ping.cog

    bot.run(token)
