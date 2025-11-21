from bot.models import EventRoster, Roster
from discord.ui import Modal, Label, Select
from discord import Interaction, SelectOption
from bot.services import Utilities
import logging


class RemoveModal(Modal):
    def __init__(self, interaction: Interaction, bot, user_lang, channel_id):
        self.channel_id = channel_id
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        self.roster = bot.rosters[channel_id]
        self.bot = bot
        self.ui = bot.language[user_lang]['ui']['Remove']
        self.language = bot.language[user_lang]['replies']
        self.user_language = user_lang
        super().__init__(title=f"{self.ui['Title']}")
        self.initialize(interaction)

    def initialize(self, interaction):
        counter = 0
        total = []
        # Print out everyone and put them in a list to get from
        if isinstance(self.roster, Roster):
            for i in self.roster.dps.keys():
                guildie = interaction.guild.get_member(int(i))
                total.append(SelectOption(label=guildie.display_name, value=i))
                counter += 1
            for i in self.roster.healers.keys():
                guildie = interaction.guild.get_member(int(i))
                total.append(SelectOption(label=guildie.display_name, value=i))
                counter += 1
            for i in self.roster.tanks.keys():
                guildie = interaction.guild.get_member(int(i))
                total.append(SelectOption(label=guildie.display_name, value=i))
                counter += 1
            for i in self.roster.backup_dps.keys():
                guildie = interaction.guild.get_member(int(i))
                total.append(SelectOption(label=guildie.display_name, value=i))
                counter += 1
            for i in self.roster.backup_healers.keys():
                guildie = interaction.guild.get_member(int(i))
                total.append(SelectOption(label=guildie.display_name, value=i))
                counter += 1
            for i in self.roster.backup_tanks.keys():
                guildie = interaction.guild.get_member(int(i))
                total.append(SelectOption(label=guildie.display_name, value=i))
                counter += 1
        elif isinstance(self.roster, EventRoster):
            for i in self.roster.members.keys():
                guildie = interaction.guild.get_member(int(i))
                total.append(SelectOption(label=guildie.display_name, value=i))
                counter += 1

        self.users = Label(
            text=f"{self.ui['Label']}",
            description=f"{self.ui['Description']}",
            component=Select(
                placeholder=f"{self.ui['Placeholder']}",
                options=total,
                max_values=counter
            ),
        )

        self.add_item(self.users)

    async def on_submit(self, interaction: Interaction):
        try:

            assert isinstance(self.users.component, Select)
            removed = self.users.component.values
            names = ''
            for i in removed:
                if isinstance(self.roster, Roster):
                    if (i in self.bot.rosters[self.channel_id].dps.keys() or i in
                            self.bot.rosters[self.channel_id].backup_dps.keys()):
                        self.bot.rosters[self.channel_id].remove_dps(i)
                        names += f"{interaction.guild.get_member(int(i)).display_name}\n"
                    elif (i in self.bot.rosters[self.channel_id].healers.keys() or i in
                          self.bot.rosters[self.channel_id].backup_healers.keys()):
                        self.bot.rosters[self.channel_id].remove_healer(i)
                        names += f"{interaction.guild.get_member(int(i)).display_name}\n"
                    elif (i in self.bot.rosters[self.channel_id].tanks.keys() or i in
                          self.bot.rosters[self.channel_id].backup_tanks.keys()):
                        self.bot.rosters[self.channel_id].remove_tank(i)
                        names += f"{interaction.guild.get_member(int(i)).display_name}\n"
                elif isinstance(self.roster, EventRoster):
                    self.bot.rosters[self.channel_id].remove_member(i)
                    names += f"{interaction.guild.get_member(int(i)).display_name}\n"

            self.bot.librarian.put_roster(self.channel_id, self.bot.rosters[self.channel_id])

            await interaction.response.send_message(f"{self.language['Remove']['Removed']
                                                       % (self.channel.name, names)}")
            return
        except ValueError:
            await interaction.response.send_message(
                f"{Utilities.format_error(self.user_language, self.language['Remove']['NumbersOnly'])}")
            return

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            f"{Utilities.format_error(self.user_language, self.language['Unknown'])}")
        logging.error(f"Remove From Roster Error: {str(error)}")
        return
