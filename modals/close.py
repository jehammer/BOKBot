from discord import Interaction, TextStyle
from discord.ui import Modal, TextInput
from models import Roster
from services import Utilities, RosterExtended, Librarian
import logging


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")

class CloseModal(Modal):
    def __init__(self,  roster: Roster, interaction: Interaction, bot, lang, roster_map, channel_id=None):
        self.language = bot.language[lang]["replies"]
        self.ui_language = bot.language[lang]["ui"]
        self.bot = bot
        self.user_language = lang
        self.config = bot.config
        self.channel_id = channel_id
        self.roster = roster
        self.roster_map = roster_map
        self.channel = interaction.guild.get_channel(int(self.channel_id))
        if self.channel is None:
            self.name = self.channel_id
        else:
            self.name = self.channel.name
        super().__init__(title=f"{self.ui_language['Close']['Title']}")
        self.initialize()
    def initialize(self):
        # Add all the items here based on what is above
        self.confirm = TextInput(
            label=f"{self.ui_language['Close']['Confirm']['Label'] % self.name}",
            placeholder=f"{self.ui_language['Close']['Confirm']['Placeholder']}",
            style=TextStyle.short,
            required=True
        )
        self.runs = TextInput(
            label=f"{self.ui_language['Close']['Runs']['Label']}",
            placeholder=f"{self.ui_language['Close']['Runs']['Placeholder']}",
            style=TextStyle.short,
            required=True
        )
        self.runscount = TextInput(
            label=f"{self.ui_language['Close']['RunsCount']['Label']}",
            placeholder=f"{self.ui_language['Close']['RunsCount']['Placeholder']}",
            default="1",
            style=TextStyle.short,
            required=True
        )
        self.add_item(self.confirm)
        self.add_item(self.runs)
        self.add_item(self.runscount)

    async def on_submit(self, interaction: Interaction):
        confirm_value = self.confirm.value.strip().lower()
        runs_inc = self.runs.value.strip().lower()
        if confirm_value != "n" and confirm_value != "y" and runs_inc != "n" and runs_inc != "y":
            await interaction.response.send_message(f"{Utilities.format_error(self.user_language, self.language['Close']['BadConfirmError'])}")
            return
        if confirm_value != "y":
            await interaction.response.send_message(f"{Utilities.format_error(self.user_language, self.language['Close']['CloseWithoutClose'])}")
            return
        runs_increased = False
        if runs_inc == "y":
            try:
                inc_val = int(self.runscount.value)
                if inc_val < 1:
                    inc_val = 1
                RosterExtended.increase_roster_count(self.roster, inc_val, table_config=self.bot.config['Dynamo']["MapDB"],
                                                     creds_config=self.bot.config["AWS"])
                runs_increased = True
            except ValueError:
                await interaction.response.send_message(f"{Utilities.format_error(self.user_language, self.language['Close']['NotNumberError'])}")
                return

        logging.info(f"Deleting Roster {self.name}")
        Librarian.delete_roster(self.channel_id, table_config=self.bot.config['Dynamo']["RosterDB"], credentials=self.bot.config["AWS"])
        logging.info(f"Roster Deleted")

        # Save Roster Mapping
        logging.info(f"Updating Roster Map")
        del self.roster_map[str(self.channel_id)]
        Librarian.put_roster_map(data=self.roster_map,
                                 table_config=self.config['Dynamo']["MapDB"], credentials=self.config["AWS"])
        logging.info(f"Updated Roster Map")

        if self.channel is not None:
            await self.channel.delete()
        if runs_increased:
            await interaction.response.send_message(f"{self.language['Close']['Increase'] % self.name}")
        else:
            await interaction.response.send_message(f"{self.language['Close']['NoIncrease'] % self.name}")

        self.bot.dispatch("reload_roster_map", self.roster_map)
        return

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(f"{Utilities.format_error(self.user_language, self.language['Incomplete'])}")
        logging.error(f"Roster Close Error: {str(error)}")
        return