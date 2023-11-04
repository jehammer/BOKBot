#!/usr/bin/python3
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import os
import logging
import yaml
from datetime import datetime
import shutil
import re
from errors.boterrors import *

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)
bot.remove_command("help")  # the help.py cog will replace the default command
log_name = "log.log"

role = None
ranks = None
poons = None
other = None


# Events
@bot.event
async def on_member_join(member):
    try:
        guild = member.guild
        base = bot.config["roles"]['default']
        if base != "none":
            await member.add_roles(role, ranks, poons, other)
            logging.info(
                f"Added Roles: {str(role)}, {str(ranks)}, {str(poons)}, {str(other)} to: {member.display_name}")
        await guild.system_channel.send(f"Welcome {member.mention} to Breath Of Kynareth! Winds of Kyne be with you!\n"
                                        f"Please read the rules in <#847968244949844008> and follow the directions for "
                                        f"access to the rest of the server.\n"
                                        f"Once you do, I will send you a little DM to help you get started!\n"
                                        f"If the bot does not work just ping the Storm Bringers.")
    except Exception as e:
        private_channel = guild.get_channel(bot.config['administration']['private'])
        await private_channel.send("Unable to apply initial role and/or welcome the new user")
        logging.error(f"Member Join Error: {str(e)}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That is not a command I know.")
    elif isinstance(error, commands.MissingRole):
        await ctx.send(f"You do not have permission to use this command. {str(error)}")
    elif isinstance(error, commands.NotOwner):
        await ctx.send(f"You are not my creator. You may not use this command.")
    elif isinstance(error, UnknownError):
        logging.error(f"UNKNOWN ERROR REACHED: {str(error)}")
        await ctx.send(f"Unreachable code has been reached. Logging details. Alerting Creator.")
        guild = bot.get_guild(bot.config['guild'])
        creator = guild.get_member(bot.config["creator"])
        await creator.send(f"{str(error)}")
    elif isinstance(error, NoDefaultError):
        await ctx.reply(f"{str(error)}")
    elif isinstance(error, NoRoleError):
        await ctx.reply(f"{str(error)}")
    else:
        await ctx.send("Unable to complete the command. I am not sure which error was thrown.")
        logging.error(f"Generic Error: {str(error)}")

async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        return await interaction.response.send_message(f"You're missing permissions to use that")
    elif isinstance(error, app_commands.MissingRole):
        return await interaction.response.send_message(f"{str(error)}")
    else:
        await interaction.response.send_message(f"Some weird error is being thrown. Not sure what it is")
        logging.error(f"{str(error)}")

bot.tree.on_error = on_tree_error

def load_configurations():
    with open("config.yaml", 'r') as stream:
        data_loaded = yaml.safe_load(stream)
    return data_loaded


async def change_playing():
    await bot.change_presence(activity=discord.Game(name=bot.config['presence_message']))
    logging.info(f"Status has been set")


async def load_cogs():
    """Load cogs from the cogs folder"""
    for filename in os.listdir("cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logging.info(f"Successfully loaded {filename}")

            except Exception as e:
                logging.info(f"Failed to load {filename}")
                logging.error(f"cog load error: {str(e)}")


async def startup_logging():
    """Checks if there is logs from a bad shutdown"""
    try:
        date = datetime.now().strftime("%m-%d-%Y")
        if os.path.exists(log_name):
            file_name = f"log-{date}-crash.log"
            os.makedirs("logs", exist_ok=True)
            version = 1
            while os.path.exists(os.path.join("logs", file_name)):
                base_name, extension = os.path.splitext(file_name)
                base_name = re.sub(r'\(\d{1,2}\)', '', base_name)
                file_name = f"{base_name}({version}){extension}"
                version += 1
            path = os.path.join("logs", file_name)
            shutil.move(log_name, path)
        time = datetime.now().strftime("%I:%M:%S %p")
        with open(log_name, "w") as file:
            file.write(f"Bot stated at: {time} on {date}\n\n")

        logging.basicConfig(
            level=logging.INFO, format='%(asctime)s: %(message)s',
            handlers=[
                logging.FileHandler('log.log', mode='a'),
                logging.StreamHandler()
            ])  # , datefmt="%Y-%m-%d %H:%M:%S")

    except Exception as e:
        logging.error(f"I was unable to set up the new logging information: {str(e)}")


async def gather_roles(guild, config):
    """Loads the starting roles for people when joining """
    global role
    global ranks
    global poons
    global other
    role = discord.utils.get(guild.roles, name=config["roles"]["default"])
    ranks = discord.utils.get(guild.roles, name=config["roles"]["ranks"])
    poons = discord.utils.get(guild.roles, name=config["roles"]["poons"])
    other = discord.utils.get(guild.roles, name=config["roles"]["other"])
    logging.info(f"Global Roles Set")


@bot.event
async def on_ready():
    logging.info(f"Logged in as: {bot.user.name}")
    await gather_roles(bot.get_guild(bot.config["guild"]), bot.config)
    await change_playing()
    synced = await bot.tree.sync()
    logging.info(f"Synced {len(synced)} command(s)")
    logging.info("Bot is ready for use")
    logging.info("Sending out load_on_ready Event")
    bot.dispatch("load_on_ready", bot)


async def main():
    async with bot:
        await startup_logging()
        bot.config = load_configurations()
        await load_cogs()
        await bot.start(bot.config['bot']['token'])


asyncio.run(main())
