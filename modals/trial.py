from models.roster import Roster
from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle, Embed, Color
from discord.utils import get
from aws import Dynamo
from services import Utilities, RosterExtended, Librarian
import logging


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


class TrialModal(Modal):
    def __init__(self, roster: Roster, interaction: Interaction, config, language, channel=None ):
        self.language = language["replies"]
        self.ui_language = language["ui"]
        self.config = config
        self.leader_trial_val = None
        self.date_val = None
        self.limit_val = None
        self.role_nums_val = "8,2,2"
        self.memo_val = "None"
        self.new_roster = True
        self.new_name = f""
        if roster is not None:
            self.channel= channel
            self.new_roster = False
            self.roster = roster
            self.leader_trial_val = f"{roster.leader},{roster.trial}"
            self.date_val = f"{roster.date}"
            self.limit_val = f"{roster.role_limit}"
            self.role_nums_val = f"{roster.dps_limit},{roster.healer_limit},{roster.tank_limit}"
            self.memo_val = f"{roster.memo}"
        super().__init__(title=self.ui_language["TrialModify"]["Title"])
        self.initialize()

    def initialize(self):
        # Add all the items here based on what is above
        self.leader_trial =  TextInput(
            label=self.ui_language["TrialModify"]["LeaderTrial"]["Label"],
            placeholder=self.ui_language["TrialModify"]["LeaderTrial"]["Placeholder"],
            default = self.leader_trial_val,
            required=True
        )
        self.date = TextInput(
            label=self.ui_language["TrialModify"]["Date"]["Label"],
            placeholder=self.ui_language["TrialModify"]["Date"]["Placeholder"],
            default = self.date_val,
            required=True
        )
        self.limit = TextInput(
            label=self.ui_language["TrialModify"]["Limit"]["Label"],
            placeholder=self.ui_language["TrialModify"]["Limit"]["Placeholder"],
            default=self.limit_val,
            required=True,
        )
        self.role_nums = TextInput(
            label=self.ui_language["TrialModify"]["RoleNums"]["Label"],
            default=self.role_nums_val,
            required=True
        )
        self.memo = TextInput(
            label=self.ui_language["TrialModify"]["Memo"]["Label"],
            default=self.memo_val,
            placeholder=self.ui_language["TrialModify"]["Memo"]["Placeholder"],
            style=TextStyle.long,
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
            roles = RosterExtended.get_limits(table_config=self.config['Dynamo']['ProgDB'],
                                              roles_config=self.config['raids']['roles'],
                                              creds_config=self.config['AWS'])
            role_limit = int(self.limit.value)
            if role_limit < 0 or role_limit > len(roles):
                await interaction.response.send_message(f"{self.language['TrialModify']['BadLimit'] % len(roles)}")
                return
        except (NameError, ValueError) as e:
            await interaction.response.send_message(f"{self.language['TrialModify']['InvalidLimit'] % self.limit.value}")
            return
        try:
            leader, trial = self.leader_trial.value.split(",")
        except (NameError, ValueError):
            await interaction.response.send_message(f"{self.language['TrialModify']['BadLeaderTrial'] % self.leader_trial.value}")
            return
        try:
            dps_limit, healer_limit, tank_limit = self.role_nums.value.split(",")
        except (NameError, ValueError):
            await interaction.response.send_message(f"{self.language['TrialModify']['BadRoleNums'] % self.role_nums.value}")
            return
        try:
            dps_limit = int(dps_limit.strip())
        except ValueError:
            await interaction.response.send_message(f"{self.language['TrialModify']['InvalidDPS'] % dps_limit}`")
            return
        try:
            healer_limit = int(healer_limit.strip())
        except ValueError:
            await interaction.response.send_message(f"{self.language['TrialModify']['InvalidHealers'] % healer_limit}`")
            return
        try:
            tank_limit = int(tank_limit.strip())
        except ValueError:
            await interaction.response.send_message(f"{self.language['TrialModify']['InvalidTanks'] % tank_limit}")
            return

        try:
            formatted_date = RosterExtended.format_date(self.date.value)
            category = interaction.guild.get_channel(self.config["raids"]["category"])

            if self.new_roster is False:
                # Update all values then update the DB
                self.roster.trial = trial
                self.roster.leader = leader
                self.roster.dps_limit = dps_limit
                self.roster.healer_limit = healer_limit
                self.roster.tank_limit = tank_limit
                self.roster.date = formatted_date
                self.roster.memo = self.memo.value
                self.roster.role_limit = role_limit

                try:
                    self.new_name = RosterExtended.generate_channel_name(formatted_date, trial, self.config['raids']['timezone'])
                    modify_channel = interaction.guild.get_channel(int(self.channel))

                    await modify_channel.edit(name=self.new_name)
                except ValueError:
                    await interaction.response.send_message(f"{self.language['TrialModify']['NewNameErr']}")
                    return

            elif self.new_roster is True:
                try:
                    self.roster = RosterExtended.factory(leader, trial, formatted_date, dps_limit, healer_limit, tank_limit, role_limit, self.memo.value, self.config)

                    logging.info(f"Creating new channel.")
                    try:
                        self.new_name = RosterExtended.generate_channel_name(self.roster.date, self.roster.trial, self.config["raids"]["timezone"])
                    except ValueError:
                        await interaction.response.send_message(f"{self.language['TrialModify']['NewNameErr']}")
                        return
                    try:
                        channel = await category.create_text_channel(self.new_name)
                    except Exception as e:
                        await interaction.response.send_message(f"{self.language['TrialModify']['CantCreate']}")
                        logging.error(f"Unable To Create New Roster Channel: {str(e)}")
                        return
                    roles_req = ""
                    if isinstance(roles[role_limit], list):
                        # Need to work with 3 roles to check, dps | tank | healer order
                        # TODO: Make the prog roles be gotten if they exist, but for the main limiters consider global permanent variables
                        limiter_dps = get(interaction.guild.roles, name=roles[role_limit][0])
                        limiter_tank = get(interaction.guild.roles, name=roles[role_limit][1])
                        limiter_healer = get(interaction.guild.roles, name=roles[role_limit][2])

                        roles_req += f"{limiter_dps.mention} {limiter_tank.mention} {limiter_healer.mention}"

                    else:
                        limiter = get(interaction.guild.roles, name=roles[role_limit])
                        roles_req += f"{limiter.mention}"
                    embed = Embed(
                        title=f"{self.roster.trial} {self.roster.date}",
                        description=f"Rank(s) Required: {roles_req}\n\nI hope people sign up for this.",
                        color=Color.blue()
                    )
                    embed.set_footer(text="Remember to spay or neuter your support!\nAnd mention your sets!")
                    embed.set_author(name="Raid Lead: " + leader)
                    embed.add_field(name="Calling Healers!", value='To Heal Us!', inline=False)
                    embed.add_field(name="Calling Tanks!", value='To Be Stronk!', inline=False)
                    embed.add_field(name="Calling DPS!", value='To Stand In Stupid!', inline=False)

                    if self.roster.memo != "None":
                        embed_memo = Embed(
                            title=" ",
                            color=Color.dark_gray()
                        )
                        embed_memo.add_field(name=" ", value=self.roster.memo, inline=True)
                        embed_memo.set_footer(text="This is very important!")
                        await channel.send(embed=embed_memo)
                    await channel.send(embed=embed)
                    logging.info(f"self.roster Channel: channelID: {str(channel.id)}")
                    self.channel = channel.id
                except Exception as e:
                    await interaction.response.send_message(f"{self.language['TrialModify']['CantEmbed']}")
                    logging.error(f"Raid Creation Channel And Embed Error: {str(e)}")
                    return
            else:
                await interaction.response.send_message(f"{self.language['TrialModify']['Unreachable']}")
                return
        except Exception as e:
            logging.error(f"Trial/Modify Error During Channel Create and Embed: {str(e)}")
            await interaction.response.send_message(f"{self.language['TrialModify']['Unreachable']}")
            return
        finally:
            # Save Roster info to DynamoDB
            try:
                # TODO: Implement new roster mapper for data saving

                logging.info(f"Saving Roster channelID: {str(channel.id)}")
                Librarian.put_roster(channel_id=self.channel, data=self.roster.get_roster_data(),
                                     table_config=self.config['Dynamo']["RosterDB"], credentials=self.config["AWS"])
                logging.info(f"Saved Roster channelID: {str(channel.id)}")
            except Exception as e:
                await interaction.response.send_message(f"{self.language['TrialModify']['DBSaveError']}")
                logging.error(f"Roster Save DynamoDB Error: {str(e)}")
                return
            if self.new_roster:
                await interaction.response.send_message(f"{self.language['TrialModify']['NewRosterCreated'] % self.new_name}")
            elif not self.new_roster:
                await interaction.response.send_message(f"{self.language['TrialModify']['ExistingUpdated'] % self.new_name}")

        # Refresh category
        category = interaction.guild.get_channel(self.config["raids"]["category"])

        # Sort channels
        for i in category.text_channels:
            i.position = RosterExtended.get_sort_key(i, self.config)

        for i in category.text_channels:
            if i.position >= 100: # Fix the rate_limit so only adjust channels we want to adjust
                await i.edit(position=i.position)
                time.sleep(1)
    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'I was unable to complete the command. Logs have more detail.')
        logging.error(f"Trial Creation/Modify Error: {str(error)}")
        return
