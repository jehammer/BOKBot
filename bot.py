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
from errors import *


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

def load_languages():
    """Function to load all the Language options for BOKBot"""
    languages = {}
    for root, _, files in os.walk("languages"):
        for file in files:
            if file.endswith(".yaml"):
                filepath = os.path.join(root, file)
                language = os.path.basename(root)
                section = os.path.splitext(file)[0]

                if language not in languages:
                    languages[language] = {}

                with open(filepath, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    languages[language][section] = data

    return languages



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
            file.write(f"Bot started at: {time} on {date}\n\n")

        logging.basicConfig(
            level=logging.INFO, format='%(asctime)s: %(message)s',
            handlers=[
                logging.FileHandler('log.log', mode='a'),
                logging.StreamHandler()
            ])  # , datefmt="%Y-%m-%d %H:%M:%S")

    except Exception as e:
        logging.error(f"I was unable to set up the new logging information: {str(e)}")


@bot.event
async def on_ready():
    logging.info(f"Logged in as: {bot.user.name}")
    await gather_roles(bot.get_guild(bot.config["guild"]), bot.config)
    await change_playing()
    logging.info("Bot is ready for use")
    logging.info("Sending out load_on_ready Event")
    bot.dispatch("load_on_ready", bot)

async def main():
    async with bot:
        await startup_logging()
        bot.config = load_configurations()
        bot.language = load_languages()
        await load_cogs()
        await bot.start(bot.config['bot']['token'])

asyncio.run(main())