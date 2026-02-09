from discord.ui import Modal, Label, Select
from discord import Interaction, SelectOption
from bot.services import Utilities
import logging

import calendar


class BirthdayModal(Modal):
    def __init__(self, interaction: Interaction, bot, user_lang):
        self.bot = bot
        self.ui = bot.language[user_lang]["ui"]["Birthday"]
        self.language = bot.language[user_lang]["replies"]
        self.user_language = user_lang
        super().__init__(title=f"{self.ui['Title']}")
        self.initialize(interaction)

    def initialize(self, interaction):
        total_months = []
        total_days_1 = []
        total_days_2 = []

        # Load Day and Month options into selection
        for i in range(0, 4):
            total_days_1.append(SelectOption(label=str(i), value=i))

        for i in range(0, 10):
            total_days_2.append(SelectOption(label=str(i), value=i))

        for i in range(1, 13):
            month_name = calendar.month_name[i]
            total_months.append(SelectOption(label=month_name, value=i))

        self.month = Label(
            text=f"{self.ui['Month']['Label']}",
            description=f"{self.ui['Month']['Description']}",
            component=Select(
                placeholder=f"{self.ui['Month']['Placeholder']}",
                options=total_months,
                max_values=1,
            ),
        )

        self.day1 = Label(
            text=f"{self.ui['Day1']['Label']}",
            description=f"{self.ui['Day1']['Description']}",
            component=Select(
                placeholder=f"{self.ui['Day1']['Placeholder']}",
                options=total_days_1,
                max_values=1,
            ),
        )

        self.day2 = Label(
            text=f"{self.ui['Day2']['Label']}",
            description=f"{self.ui['Day2']['Description']}",
            component=Select(
                placeholder=f"{self.ui['Day2']['Placeholder']}",
                options=total_days_2,
                max_values=1,
            ),
        )

        self.add_item(self.month)
        self.add_item(self.day1)
        self.add_item(self.day2)

    async def on_submit(self, interaction: Interaction):
        try:

            assert isinstance(self.month.component, Select)
            assert isinstance(self.day1.component, Select)
            assert isinstance(self.day2.component, Select)

            month = int(self.month.component.values[0])
            day1 = self.day1.component.values[0]
            day2 = self.day2.component.values[0]

            day = int(f"{day1}{day2}")
            if day < 1 or day > 31:
                raise ValueError
            if month < 1 or month > 12:
                raise ValueError

            max_days = 29 if month == 2 else calendar.mdays[month]
            if day > max_days:
                raise ValueError

            birthday = f"{month}/{day}"

            self.bot.librarian.put_birthday(interaction.user.id, birthday)

            await interaction.response.send_message(
                self.language["Birthday"]["Set"] % birthday, ephemeral=True
            )

            return
        except (ValueError, IndexError):
            await interaction.response.send_message(
                f"{Utilities.format_error(self.user_language, self.language['Birthday']['Invalid'])}",
                ephemeral=True,
            )
            return

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            f"{Utilities.format_error(self.user_language, self.language['Unknown'])}"
        )
        logging.error(f"Birthday Error: {str(error)}")
        return
