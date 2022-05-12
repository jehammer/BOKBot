#!/usr/bin/python3

import nextcord
from nextcord.ext import commands
import os
import logging

logging.basicConfig(level=logging.INFO)

intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)

# Remove Help command for custom one (for later)
# TODO: Implement custom help commands
# bot.remove_command("help")


# @bot.command()
# async def help(ctx):
#     embed = nextcord.Embed(title="BOKBot Help", description="Help command for BOKBot")


# Events
@bot.event
async def on_member_join(member):
    # Apply Recruits role on server entry
    guild = member.guild
    user = member
    role = nextcord.utils.get(member.guild.roles, name="Recruits")
    await user.add_roles(role)
    await guild.system_channel.send(f"Welcome {member.mention} to Breath Of Kynareth! Winds of Kyne be "
                                    "with you, please\n" +
                                    "read the rules in <#847968244949844008> and type !agree to join the rest of the "
                                    "server. Use !roles in\n" +
                                    "<#933596721630548059> to check out the assignable roles using !role [role] If "
                                    "the bot does not work just ping the Storm Bringers.")


@bot.event
async def on_member_remove(member):
    # Lets the Officers know when someone leaves the guild, good for managing stuff
    guild = member.guild
    user = member
    channel = member.guild.get_channel(908210533927370784)
    await channel.send(f"{member.name}#{user.discriminator} - {member.display_name} has left the server")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That is not a command I know.")
    else:
        await ctx.send("Something went wrong with the command. If needed please consult the guide "
                       "in <#932438565009379358>")


async def change_playing():
    await bot.change_presence(activity=nextcord.Game(name="Several Godslayer Progs"))
    print(f"Status has been set")


def load_cogs():
    """Load cogs from the cogs folder"""
    for filename in os.listdir("cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Successfully loaded {filename}")

            except Exception as e:
                print(f"Failed to load {filename}")
                logging.error("cog load error: " + str(e))


@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")
    await change_playing()  # Works in non-cog without self, requires self in cogs
    print("Bot is ready for use")


@bot.command()
async def shutdown(ctx: commands.Context):
    """Owner-Only shutdown command"""
    try:
        if ctx.message.author.id == 212634819190849536:
            logging.info("Closing connection and shutting down")
            await bot.close()
        else:
            await ctx.reply("You do not have permission to do this")
    except Exception as e:
        await ctx.send("Error shutting down")
        logging.error("Shutdown error: " + str(e))


load_cogs()
if __name__ == '__main__':
    with open('Token.txt') as f:
        token = f.readline()
    bot.run(token)
