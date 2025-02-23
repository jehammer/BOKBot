from models.roster import Roster
from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle, Embed, Color, Role
from discord.utils import get
from services import Utilities, RosterExtended, EmbedFactory
import logging


class FillModal(Modal):
    def __init__(self, roster: Roster, interaction: Interaction, bot, user_language, channel_id=None):
        self.user_language = user_language
        self.bot = bot
        self.ui = self.bot.language[user_language]['ui']['Fill']
        self.lang = self.bot.language[user_language]['replies']
        self.channel_id = channel_id
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        self.roster = roster
        super().__init__(title=f"{self.ui['Title']}")
        self.initialize()

    def initialize(self):
        self.confirm = TextInput(
            label=f"{self.ui['Label'] % self.channel.name}",
            placeholder=f"{self.ui['Placeholder']}",
            style=TextStyle.short,
            required=True
        )
        self.add_item(self.confirm)

    async def on_submit(self, interaction: Interaction):
        val = self.confirm.value.strip().lower()
        if val != 'y' and val != 'n':
            await interaction.response.send_message(f"{self.lang['Fill']['InvalidInput']}")
            return
        if val != "y":
            await interaction.response.send_message(f"{self.lang['Fill']['NInput']}")
            return

        self.bot.dispatch("update_rosters_data", channel_id=self.channel_id, channel_name=self.channel.name,
                          update_roster=self.roster, method="fill",
                          interaction=interaction, user_language=self.user_language)

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(f"{Utilities.format_error(self.user_language, self.bot.language['Unknown'])}")
        logging.error(f"Roster Fill Error: {str(error)}")
        return
