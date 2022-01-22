#!/usr/bin/python3
import nextcord
from nextcord.ext import commands
import os

intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)
###TODO: Slash commands when they become available, or redevelop in another system that supports it. 

#Events
@bot.event
async def on_member_join(member):
    #Apply Recruits role on server entry
    guild = member.guild
    user = member
    role = nextcord.utils.get(member.guild.roles, name="Recruits")
    await user.add_roles(role)
    await guild.system_channel.send(f'''Welcome {member.mention} to Breath Of Kynareth!
Winds of Kyne be with you, please read the rules in <#847968244949844008> and type !agree to join the rest of the server.
Use !roles in <#933596721630548059> to check out the assignable roles using !role [role]
If the bot does not work just ping the Storm Bringers.''')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Error, Unknown Command.")
    else:
        await ctx.send("Error, something has gone wrong. Are you invoking the command correctly?")

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
