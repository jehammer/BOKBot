from bot.models.roster import Roster
from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle, Role
from discord.utils import get
from bot.services import Utilities, RosterExtended, EmbedFactory
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


class TrialModal(Modal):
    def __init__(self, roster: Roster, interaction: Interaction, bot, lang, limits, channel=None):
        self.localization = bot.language[lang]['replies']
        self.ui_localization = bot.language[lang]["ui"]
        self.config = bot.config
        self.limits = limits
        self.leader_trial_val = None
        self.date_val = None
        self.limit_val = None
        self.role_nums_val = "8,2,2"
        self.memo_val = "None"
        self.new_roster = True
        self.new_name = f""
        self.user_language = lang
        self.bot = bot
        self.channel = None
        self.change_name = True
        self.sort_channels = True
        self.roster = None
        if roster is not None:
            self.channel_id = channel
            self.new_roster = False
            self.roster = roster
            self.leader_trial_val = f"{roster.leader},{roster.trial}"
            self.date_val = f"{roster.date}"
            self.limit_val = f"{roster.role_limit}"
            self.role_nums_val = f"{roster.dps_limit},{roster.healer_limit},{roster.tank_limit}"
            self.memo_val = f"{roster.memo}"
        super().__init__(title=self.ui_localization['TrialModify']['Title'])
        self.initialize()

    def initialize(self):
        # Add all the items here based on what is above
        self.leader_trial = TextInput(
            label=self.ui_localization["TrialModify"]["LeaderTrial"]["Label"],
            placeholder=self.ui_localization["TrialModify"]["LeaderTrial"]["Placeholder"],
            default=self.leader_trial_val,
            required=True
        )
        self.date = TextInput(
            label=self.ui_localization["TrialModify"]["Date"]["Label"],
            placeholder=self.ui_localization["TrialModify"]["Date"]["Placeholder"],
            default=self.date_val,
            required=True
        )
        self.limit = TextInput(
            label=self.ui_localization["TrialModify"]["Limit"]["Label"],
            placeholder=self.ui_localization["TrialModify"]["Limit"]["Placeholder"],
            default=self.limit_val,
            required=True,
        )
        self.role_nums = TextInput(
            label=self.ui_localization["TrialModify"]["RoleNums"]["Label"],
            default=self.role_nums_val,
            required=True
        )
        self.memo = TextInput(
            label=self.ui_localization["TrialModify"]["Memo"]["Label"],
            default=self.memo_val,
            placeholder=self.ui_localization["TrialModify"]["Memo"]["Placeholder"],
            style=TextStyle.long,
            max_length=200,
            required=True
        )
        self.add_item(self.leader_trial)
        self.add_item(self.date)
        self.add_item(self.limit)
        self.add_item(self.role_nums)
        self.add_item(self.memo)

    async def on_submit(self, interaction: Interaction):
        # Split the values:
        try:
            roles = self.limits

            role_limit = int(self.limit.value)
            if role_limit < 0 or role_limit > len(roles):
                await interaction.response.send_message(
                    f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['BadLimit'] % len(roles))}")
                return
        except (NameError, ValueError) as e:
            await interaction.response.send_message(
                f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['InvalidLimit'] % self.limit.value)}")
            return
        try:
            leader, trial = self.leader_trial.value.split(",")
            trial.lstrip()
        except (NameError, ValueError):
            await interaction.response.send_message(
                f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['BadLeaderTrial'] % self.leader_trial.value)}")
            return
        try:
            dps_limit, healer_limit, tank_limit = self.role_nums.value.split(",")
        except (NameError, ValueError):
            await interaction.response.send_message(
                f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['BadRoleNums'] % self.role_nums.value)}")
            return
        try:
            dps_limit = int(dps_limit.strip())
        except ValueError:
            await interaction.response.send_message(
                f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['InvalidDPS'] % dps_limit)}")
            return
        try:
            healer_limit = int(healer_limit.strip())
        except ValueError:
            await interaction.response.send_message(
                f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['InvalidHealers'] % healer_limit)}`")
            return
        try:
            tank_limit = int(tank_limit.strip())
        except ValueError:
            await interaction.response.send_message(
                f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['InvalidTanks'] % tank_limit)}")
            return

        try:
            formatted_date = RosterExtended.format_date(self.date.value)
            category = interaction.guild.get_channel(self.config["raids"]["category"])

            if self.new_roster is False:
                old_date = self.roster.date
                old_trial = self.roster.trial
                # Update all values then update the DB
                self.roster.trial = trial
                self.roster.leader = leader
                self.roster.dps_limit = dps_limit
                self.roster.healer_limit = healer_limit
                self.roster.tank_limit = tank_limit
                self.roster.date = formatted_date
                self.roster.memo = self.memo.value
                self.roster.role_limit = role_limit

                self.channel = interaction.guild.get_channel(int(self.channel_id))

                try:

                    day_change = RosterExtended.did_day_change(old_date, self.roster.date,
                                                               self.config["raids"]["timezone"])
                    trial_change = RosterExtended.did_trial_change(old_trial, self.roster.trial)
                    if not day_change:
                        self.sort_channels = False

                    if not trial_change:
                        self.change_name = False

                    if self.sort_channels or self.change_name:
                        self.new_name = RosterExtended.generate_channel_name(formatted_date, trial,
                                                                             self.config['raids']['timezone'])
                        await self.channel.edit(name=self.new_name)

                    if day_change or trial_change:
                        name = RosterExtended.create_pingable_role_name(trial=self.roster.trial, date=self.roster.date,
                                                                        tz=self.config['raids']['timezone'],
                                                                        guild=interaction.guild)
                        await interaction.guild.get_role(self.roster.pingable).edit(name=name)

                except ValueError as e:
                    await interaction.response.send_message(
                        f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['NewNameErr'])}")
                    logging.info(f"New Name Value Error Existing Roster: {e}")
                    return

            elif self.new_roster is True:
                try:
                    self.roster = RosterExtended.factory(leader, trial, formatted_date, dps_limit, healer_limit,
                                                         tank_limit, role_limit, self.memo.value, self.config)

                    group_role = RosterExtended.create_pingable_role_name(trial=self.roster.trial,
                                                                          date=self.roster.date,
                                                                          tz=self.config['raids']['timezone'],
                                                                          guild=interaction.guild)

                    role: Role = await interaction.guild.create_role(name=group_role, mentionable=True)
                    self.roster.pingable = role.id

                    logging.info(f"Creating new channel.")
                    try:
                        self.new_name = RosterExtended.generate_channel_name(self.roster.date, self.roster.trial,
                                                                             self.config["raids"]["timezone"])
                    except ValueError as e:
                        await interaction.response.send_message(
                            f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['NewNameErr'])}")
                        logging.info(f"New Name Value Error New Roster: {e}")
                        return
                    try:
                        self.channel = await category.create_text_channel(self.new_name)
                        self.roster.channel = self.channel.id # Set new rosters channel to the id.
                    except Exception as e:
                        await interaction.response.send_message(
                            f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['CantCreate'])}")
                        logging.error(f"Unable To Create New Roster Channel: {str(e)}")
                        return
                    roles_req = ""
                    if isinstance(roles[role_limit], list):
                        # Need to work with 3 roles to check, dps | tank | healer order

                        limiter_dps = get(interaction.guild.roles, name=roles[role_limit][0])
                        limiter_tank = get(interaction.guild.roles, name=roles[role_limit][1])
                        limiter_healer = get(interaction.guild.roles, name=roles[role_limit][2])

                        roles_req += f"{limiter_dps.mention} {limiter_tank.mention} {limiter_healer.mention}"

                    else:
                        limiter = get(interaction.guild.roles, name=roles[role_limit])
                        roles_req += f"{limiter.mention}"

                    embed = EmbedFactory.create_new_roster(trial=self.roster.trial, date=self.roster.date,
                                                           roles_req=roles_req, leader=self.roster.leader,
                                                           memo=self.roster.memo, pingable=self.roster.pingable)
                    await self.channel.send(embed=embed)

                    logging.info(f"Roster Channel: channelID: {str(self.channel.id)}")
                    self.channel_id = self.channel.id
                except Exception as e:
                    await interaction.response.send_message(
                        f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['CantEmbed'])}")
                    logging.error(f"Raid Creation Channel And Embed Error: {str(e)}")
                    return
            else:
                await interaction.response.send_message(
                    f"{Utilities.format_error(self.user_language, self.localization['Unreachable'])}")
                return
        except Exception as e:
            logging.error(f"Trial/Modify Error During Channel Create and Embed: {str(e)}")
            await interaction.response.send_message(
                f"{Utilities.format_error(self.user_language, self.localization['Unreachable'])}")
            return

        self.bot.dispatch("update_rosters_data", channel_id=self.channel_id, channel_name=self.channel.name,
                          update_roster=self.roster, method="create_update",
                          interaction=interaction, user_language=self.user_language)

        if self.sort_channels:
            try:
                # Put new channel into the right position
                position = RosterExtended.get_channel_position(self.roster, self.config["raids"]["timezone"])
                self.channel.position = position
                await self.channel.edit(position=self.channel.position)
            except Exception as e:
                logging.error(f"Position Change Error: {str(e)}")
                await interaction.response.send_message(
                    f"{Utilities.format_error(self.user_language, self.localization['TrialModify']['CantPosition'])}")
                return
        return

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            f"{Utilities.format_error(self.user_language, self.localization['Incomplete'])}")
        logging.error(f"Trial Creation/Modify Error: {str(error)}")
        return
