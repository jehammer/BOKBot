import discord
from discord.ext import commands
from discord import app_commands
import logging
import time
import secrets
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")

auth = None
length = 20

def set_channels(config):
    """Function to set the MongoDB information on cog load"""
    global auth
    client = MongoClient(config['mongo'])
    database = client['bot']
    auth = database.auth

def generate_access_token():
    """Creates a users access token"""
    return secrets.token_hex(length)

def generate_timeout():
    """Calculates when to time out an access Token."""
    return int(time.time() + (2 * 3600))

class Auth(commands.Cog, name="Auth"):
    """Authorizes you into the BOK Website"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        set_channels(bot.config)

    @app_commands.command(name="auth", description="Creates your access Token to the BOK Website")
    async def send_site_authorization(self, interaction: discord.Interaction) -> None:
        """Get yourself a token to log into the website!"""
        try:
            if isinstance(interaction.channel, discord.channel.DMChannel):
                await interaction.response.send_message(f"This command must be called from within the server so I can get your permissions.")
                logging.info(f"User: {interaction.user.display_name} attempted to generate Token from DMs")
                return

            user = interaction.user
            await user.send('Generating Token')
            logging.info(f"Generating Site Token for: {interaction.user.display_name}")
            permissions = []
            user_id = str(user.id)
            generated_token = generate_access_token()
            timeout = generate_timeout()
            name = user.display_name

            for i in user.roles:
                if i.name == self.bot.config["roles"]["unlock"]:
                    permissions.append(self.bot.config["permissions"]["general"])
                elif i.name == self.bot.config["roles"]["admin"]:
                    permissions.append(self.bot.config["permissions"]["officer"])
                elif i.name == self.bot.config["raids"]["lead"]:
                    permissions.append(self.bot.config["permissions"]["raidLead"])

            # Delete old user token if they re-authed
            old_token = auth.find_one({'userID': user_id})
            if old_token is not None:
                auth.delete_one(old_token)

            rec = {
                'token': generated_token,
                "timeout": timeout,
                'userID': user_id,
                "name": name,
                "permissions": permissions
            }
            auth.insert_one(rec)
            await user.send(f"Your token has been generated:\n{str(generated_token)}")
            logging.info(f"Generated Site Token for: {interaction.user.display_name}")

            await interaction.response.send_message(f"Check your DMs.", ephemeral=True)

        except discord.Forbidden:
            await interaction.response.send_message(f"Please enable DMs on this server, I need permission to DM you for this command.")
        except Exception as e:
            await interaction.response.send_message("Unable to setup authorization for you.")
            logging.error(f"Auth Command Error: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Auth(bot))
