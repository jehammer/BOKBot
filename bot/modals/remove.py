from bot.models import EventRoster, Roster
from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle
from bot.services import Utilities
import logging


class RemoveModal(Modal):
    def __init__(self, interaction: Interaction, bot, user_lang, channel_id):
        self.channel_id = channel_id
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        self.roster = self.bot.rosters[channel_id]
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
            removed = [int(i) for i in self.options.value.split(',')]
            for i in removed:
                if people[i] in self.bot.rosters[self.channel_id].dps.keys() or people[i] in self.bot.rosters[self.channel_id].backup_dps.keys():
                    self.bot.rosters[self.channel_id].remove_dps(people[i])
                    names += f"{interaction.guild.get_member(int(people[i])).display_name}\n"
                elif (people[i] in self.bot.rosters[self.channel_id].healers.keys() or people[i] in
                      self.bot.rosters[self.channel_id].backup_healers.keys()):
                    self.bot.rosters[self.channel_id].remove_healer(people[i])
                    names += f"{interaction.guild.get_member(int(people[i])).display_name}\n"
                elif (people[i] in self.bot.rosters[self.channel_id].tanks.keys() or people[i] in
                      self.bot.rosters[self.channel_id].backup_tanks.keys()):
                    self.bot.rosters[self.channel_id].remove_tank(people[i])
                    names += f"{interaction.guild.get_member(int(people[i])).display_name}\n"

            if isinstance(self.bot.roster[self.channel_id], Roster):
                self.bot.librarian.put_trial_roster(self.channel_id, self.bot.roster[self.channel_id])
            elif isinstance(self.bot.roster[self.channel_id], EventRoster):
                self.bot.librarian.put_event_roster(self.channel_id, self.bot.roster[self.channel_id])

            await interaction.response.send_message(f"{self.bot.language[user_language]['replies']['Remove']['Removed']
                                                       % (channel_name, names)}")
            return
        except ValueError:
            await interaction.response.send_message(f"{Utilities.format_error(self.user_language, self.language['Remove']['NumbersOnly'])}")
            return

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(f"{Utilities.format_error(self.user_language, self.language['Unknown'])}")
        logging.error(f"Remove From Roster Error: {str(error)}")
        return
