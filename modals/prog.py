from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle, Embed, Color
from services import Librarian
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


class ProgModal(Modal):
    def __init__(self, bot, interaction: Interaction, user_language):
        self.config = self.bot.config
        self.bot = bot
        self.language = self.bot.language[user_language]['replies']
        self.ui_language = self.bot.language[user_language]['ui']
        super().__init__(title=self.ui_language['Prog']['Title'])
        self.initialize()

    def initialize(self):
        roles = Librarian.get_progs(self.config['Dynamo']['ProgDB'], self.config['AWS'])
        default_vals = ""
        if roles is not None:
            for i in roles:
                default_vals += f"{str(i)}\n"
        self.roles_input = TextInput(
            label=self.ui_language['Prog']['RolesInput']['Label'],
            placeholder=self.ui_language['Prog']['RolesInput']['Placeholder'],
            default=default_vals,
            style=TextStyle.long,
            required=True
        )
        self.add_item(self.roles_input)

    async def on_submit(self, interaction: Interaction):
        role_list = self.roles_input.value.splitlines()
        logging.info(f"Updating Prog Role Data")
        Librarian.put_progs(role_list, self.config['Dynamo']['ProgDB'], self.config['AWS'])
        logging.info(f"Updated Prog Role Data")
        self.bot.dispatch("update_limits_data")
        await interaction.response.send_message(self.language['Prog']['Updated'])
        return

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        logging.error(f"Prog Roles Update Error: {str(error)}")
        await interaction.response.send_message(
            f"{Utilities.format_error(self.user_language, self.language['Incomplete'])}")
        return
