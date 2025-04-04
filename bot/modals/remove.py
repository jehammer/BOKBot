from bot.models.roster import Roster
from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle
from bot.services import Utilities
import logging


class RemoveModal(Modal):
    def __init__(self, roster: Roster, interaction: Interaction, bot, user_lang, channel_id=None):
        self.channel_id = channel_id
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        self.roster = roster
        self.people = {}
        self.bot = bot
        self.ui = bot.language[user_lang]['ui']['Remove']
        self.language = bot.language[user_lang]['replies']
        self.user_language = user_lang
        super().__init__(title=f"{self.ui['Title']}")
        self.initialize(interaction)

    def initialize(self, interaction):
        counter = 1
        total = ""
        # Print out everyone and put them in a list to get from
        for i in self.roster.dps.keys():
            self.people[counter] = i
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        for i in self.roster.healers.keys():
            self.people[counter] = i
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        for i in self.roster.tanks.keys():
            self.people[counter] = i
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        for i in self.roster.backup_dps.keys():
            self.people[counter] = i
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        for i in self.roster.backup_healers.keys():
            self.people[counter] = i
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1
        for i in self.roster.backup_tanks.keys():
            self.people[counter] = i
            total += f"{counter}: {interaction.guild.get_member(int(i)).display_name}\n"
            counter += 1

        self.users = TextInput(
            label=f"{self.channel.name}",
            default=f"{total}",
            style=TextStyle.long,
            required=False
        )
        self.options = TextInput(
            label=f"{self.ui['Label']}",
            placeholder=f"{self.ui['Placeholder']}",
            style=TextStyle.short,
            required=True
        )
        self.add_item(self.users)
        self.add_item(self.options)

    async def on_submit(self, interaction: Interaction):
        try:
            to_remove = [int(i) for i in self.options.value.split(',')]
            self.bot.dispatch("update_rosters_data", channel_id=self.channel_id, channel_name=self.channel.name,
                              update_roster=self.roster, method="remove",
                              interaction=interaction, user_language=self.user_language, removed=to_remove, people=self.people)
            return
        except ValueError:
            await interaction.response.send_message(f"{Utilities.format_error(self.user_language, self.language['Remove']['NumbersOnly'])}")
            return

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(f"{Utilities.format_error(self.user_language, self.language['Unknown'])}")
        logging.error(f"Remove From Roster Error: {str(error)}")
        return
