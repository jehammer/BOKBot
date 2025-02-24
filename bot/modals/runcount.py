from bot.models import Roster
from bot.services import RosterExtended
from discord import Interaction, TextStyle
from discord.ui import TextInput, Modal


class RunCountModal(Modal):
    def __init__(self, roster: Roster, interaction: Interaction, bot, users_language):
        self.bot = bot
        self.language = bot.language[users_language]['replies']
        self.ui = bot.language[users_language]['ui']
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        self.roster = roster
        self.user_language = users_language
        super().__init__(title=f"{self.ui_language['RunCount']['Title'] % self.channel.name}")
        self.initialize()

    def initialize(self):
        self.num = TextInput(
            label=f"{self.ui_language['RunCount']['Num']['Label']}",
            default="1",
            placeholder=f"{self.ui_language['RunCount']['Num']['Placeholder']}",
            style=TextStyle.short,
            required=True
        )
        self.add_item(self.num)

    async def on_submit(self, interaction: Interaction):
        try:
            inc_val = int(self.num.value)
            if inc_val > 10:
                raise ValueError
            RosterExtended.increase_roster_count(self.roster, inc_val,
                                                 table_config=self.bot.config['Dynamo']["CountDB"],
                                                 creds_config=self.bot.config["AWS"])
        except ValueError:
            await interaction.response.send_message(
                f"{Utilities.format_error(self.user_language, self.localization['Close']['NotNumberError'])}")
            return
        await interaction.response.send_message(
            f"{self.language['RunCount']['Increase'] % (self.channel.name, inc_val)}")
        return

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            f"{Utilities.format_error(self.user_language, self.bot.language['Unknown'])}")
        logging.error(f"Run Count Error: {str(error)}")
        return
