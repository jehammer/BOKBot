#!/usr/bin/python3
import asyncio
from discord.ext import commands
from discord import app_commands, Intents, Interaction, Game
from datetime import datetime
import logging
import shutil
import yaml
import os
import re
import random

from bot.database import init_librarian
# Bot-Specific Imports
from bot.errors import *

intents = Intents.all()
intents.members = True
main_bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)
main_bot.remove_command('help')  # the help.py cog will replace the default command
log_name = 'log.log'


# Value Loaders
def load_configurations():
    full_config = {}
    directory = os.path.join(os.getcwd(), 'config')
    if not os.path.exists(directory):
        logging.error(f"The directory {directory} does not exist.")
        return
    for filename in os.listdir(directory):  # Go through all the config files but ignore templates
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            if not filename.lower().startswith('template'):
                file_path = os.path.join(directory, filename)

                # Open and read the YAML file
                with open(file_path, 'r') as file:
                    file_content = yaml.safe_load(file)

                    # Ensure the file content is a dictionary
                    if isinstance(file_content, dict):
                        full_config.update(file_content)
                    else:
                        logging.warning(f"Load Configuration Warning: {filename} is improperly formatted "
                                        f"and doesn't make a dictionary")
    return full_config


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


async def load_cogs():
    """Load cogs from the cogs folder"""
    for filename in os.listdir('bot/cogs'):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                await main_bot.load_extension(f"bot.cogs.{filename[:-3]}")
                logging.info(f"Successfully loaded {filename}")

            except Exception as e:
                logging.info(f"Failed to load {filename}")
                logging.error(f"cog load error: {str(e)}")


async def startup_logging():
    """Checks if there are logs from a bad shutdown"""
    try:
        date = datetime.now().strftime('%m-%d-%Y')
        if os.path.exists(log_name):
            file_name = f"log-{date}-crash.log"
            os.makedirs("logs", exist_ok=True)
            version = 1
            while os.path.exists(os.path.join('logs', file_name)):
                base_name, extension = os.path.splitext(file_name)
                base_name = re.sub(r'\(\d{1,2}\)', '', base_name)
                file_name = f"{base_name}({version}){extension}"
                version += 1
            path = os.path.join('logs', file_name)
            # Quick fix for the handlers causing issues with moving the logs, so close them quickly before starting again.
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
                handler.close()
            shutil.move(log_name, path)
        time = datetime.now().strftime('%I:%M:%S %p')
        with open(log_name, 'w') as file:
            file.write(f"Bot started at: {time} on {date}\n\n")

        logging.basicConfig(
            level=logging.INFO, format='%(asctime)s: %(message)s',
            handlers=[
                logging.FileHandler('log.log', mode='a'),
                logging.StreamHandler()
            ])  # , datefmt="%Y-%m-%d %H:%M:%S")

    except Exception as e:
        logging.error(f"I was unable to set up the new logging information: {str(e)}")


# Events and Errors
@main_bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        styles = ["(ツ)", "(•_•)", "(°_°)", "(¬‿¬)", "(ಠ_ಠ)"]
        shrug = f"¯\\\\\\_{random.choice(styles)}\\_/¯"
        await ctx.reply(f"{shrug}")
    elif isinstance(error, commands.MissingRole):
        await ctx.reply(f"You do not have permission to use this command. {str(error)}")
    elif isinstance(error, commands.NotOwner):
        await ctx.reply(f"You are not my creator. You may not use this command.")
    elif isinstance(error, UnknownError):
        logging.error(f"UNKNOWN ERROR REACHED: {str(error)}")
        await ctx.reply(f"Unreachable code has been reached. Logging details. Alerting Creator.")
        guild = main_bot.get_guild(main_bot.config['guild'])
        creator = guild.get_member(main_bot.config["creator"])
        await creator.send(f"{str(error)}")
    elif isinstance(error, NoDefaultError):
        await ctx.reply(f"{str(error)}")
    elif isinstance(error, NoRoleError):
        await ctx.reply(f"{str(error)}")
    elif isinstance(error, NotPrivateError):
        await ctx.reply(f"{str(error)}")
    else:
        await ctx.send("Unable to complete the command. I am not sure which error was thrown.")
        logging.error(f"Generic Error: {str(error)}")


async def on_tree_error(interaction: Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        return await interaction.response.send_message(f"You're missing permissions to use that")
    elif isinstance(error, app_commands.MissingRole):
        return await interaction.response.send_message(f"{str(error)}")
    elif isinstance(error, NotPrivateError):
        return await interaction.response.send_message(f"{str(error)}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Some weird error is being thrown. Not sure what it is")
        logging.error(f"{str(error)}")


main_bot.tree.on_error = on_tree_error


async def set_playing():
    await main_bot.change_presence(activity=Game(name=main_bot.config['presence_message']))
    logging.info(f"Status has been set")


@main_bot.event
async def on_ready():
    logging.info(f"Logged in as: {main_bot.user.name}")
    await set_playing()
    if hasattr(main_bot, "librarian"):
        logging.info(f"Existing Librarian instance found, closing and reopening.")
        main_bot.librarian.close()
    main_bot.librarian = init_librarian(main_bot.config['bot']['mongo'])
    main_bot.private_channel = main_bot.get_guild(main_bot.config['guild']).get_channel(main_bot.config['administration']['private'])
    logging.info('Bot is ready for use')
    logging.info('Sending out load_on_ready Event')
    main_bot.dispatch('load_on_ready', main_bot)


async def main():
    async with main_bot:
        await startup_logging()
        main_bot.config = load_configurations()
        main_bot.language = load_languages()
        await load_cogs()
        await main_bot.start(main_bot.config['bot']['token'])


asyncio.run(main())
