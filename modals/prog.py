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
    def __init__(self, interaction: Interaction, config, language):
        self.config = config
        self.language = language['replies']
        self.ui_language = language['ui']
        super().__init__(title=self.ui_language['Prog']['Title'])
        self.initialize()
    def initialize(self):
        roles = Librarian.get_progs(self.config['Dynamo']['ProgDB'], self.config['AWS'])
        default_vals = ""
        if roles is not None:
            for i in roles:
                default_vals += f"{str(i)}\n"
        self.roles_input = TextInput(
            label= self.ui_language['Prog']['RolesInput']['Label'],
            placeholder= self.ui_language['Prog']['RolesInput']['Placeholder'],
            default = default_vals,
            style=TextStyle.long,
            required=True
        )
        self.add_item(self.roles_input)

    async def on_submit(self, interaction: Interaction):
        role_list = self.roles_input.value.splitlines()
        Librarian.put_progs(role_list, self.config['Dynamo']['ProgDB'], self.config['AWS'])
        await interaction.response.send_message(self.language['Prog']['Updated'])
        return
    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(self.language['Prog']['Incomplete'])
        logging.error(f"Prog Roles Update Error: {str(error)}")
        return