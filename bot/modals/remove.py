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
            display_roles = ["tank", "healer", "dps"]
            bucket_order = [0, 1, 2]  # main, backup, overflow for ordering.

            for role in display_roles:
                if role not in self.roster.role_map:
                    continue

                main_bucket_name, backup_bucket_name, overflow_bucket_name = self.roster.role_map[role]
                buckets = [main_bucket_name, backup_bucket_name, overflow_bucket_name]

                for index in bucket_order:
                    bucket_name = buckets[index]
                    bucket = getattr(self.roster, bucket_name, {})

                    for user_id in bucket.keys():
                        guildie = interaction.guild.get_member(int(user_id))
                        if guildie is None:
                            continue

                        total.append(
                            SelectOption(
                                label=guildie.display_name,
                                value=user_id,
                                description=["Main", "Backup", "Overflow"][index]
                            )
                        )
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
                    found = False
                    # Check main, backup, and overflow for each role
                    for role, (main, backup, overflow) in self.bot.rosters[self.channel_id].role_map.items():
                        for j in (main, backup, overflow):
                            bucket = getattr(self.bot.rosters[self.channel_id], j)
                            if i in bucket:
                                self.bot.rosters[self.channel_id].remove_member(i)
                                member = interaction.guild.get_member(int(i))
                                if member:
                                    names += f"{member.display_name}\n"

                                found = True
                                break
                        if found:
                            break
                elif isinstance(self.roster, EventRoster):
                    self.bot.rosters[self.channel_id].remove_member(i)
                    names += f"{interaction.guild.get_member(int(i)).display_name}\n"

            self.bot.librarian.put_roster(self.channel_id, self.bot.rosters[self.channel_id])

            await interaction.response.send_message(self.language["Remove"]["Removed"] % (self.channel.name, names))
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
