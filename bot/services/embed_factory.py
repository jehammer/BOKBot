from discord import Embed, Color
import logging
from bot.models import Roster, Rank, Count

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


class EmbedFactory:
    """Class of Static Methods that create and return embeds"""

    @staticmethod
    def create_status(roster: Roster, language, bot, roles_req, guild):
        try:

            dps_count = 0
            healer_count = 0
            tank_count = 0

            desc = f"{language['Rank']} {roles_req}\n{language['Pingable']} <@&{roster.pingable}>"

            if roster.memo != "None":
                desc += f"\n\n{roster.memo}"

            embed = Embed(
                title=f"{roster.trial.replace('_', r'\_')} {roster.date}",
                description=desc,
                color=Color.green()
            )
            embed.set_footer(text=f"{language['Footer']}")
            embed.set_author(name=f"{language['Author']} {roster.leader.replace("_", r"\_")}")

            names = ""
            # TANKS
            if not len(roster.tanks) == 0:
                tanks = roster.tanks
                for i in tanks:
                    member_name = guild.get_member(int(i))
                    if member_name is not None:
                        names += f"{bot.config['raids']['tank_emoji']}{member_name.display_name.replace("_", r"\_")}\n{roster.tanks[i].replace("_", r"\_")}\n"
                        tank_count += 1

            embed.add_field(name=f"{language['Tanks']} {tank_count}/{roster.tank_limit}", value=names, inline=True)

            names = ""
            # HEALERS
            if not len(roster.healers) == 0:
                for i in roster.healers:
                    member_name = guild.get_member(int(i))
                    if member_name is not None:
                        names += f"{bot.config['raids']['healer_emoji']}{member_name.display_name.replace("_", r"\_")}\n{roster.healers[i].replace("_", r"\_")}\n"
                        healer_count += 1

            embed.add_field(name=f"{language['Healers']} {healer_count}/{roster.healer_limit}", value=names,
                            inline=True)

            names = ""
            # DPS
            if not len(roster.dps) == 0:
                dps = roster.dps
                for i in dps:
                    member_name = guild.get_member(int(i))
                    if member_name is not None:
                        names += f"{bot.config['raids']['dps_emoji']}{member_name.display_name.replace("_", r"\_")}\n{roster.dps[i].replace("_", r"\_")}\n"
                        dps_count += 1

            embed.add_field(name=f"{language['DPS']} {dps_count}/{roster.dps_limit}", value=names, inline=True)

            # Show Backup/Overflow Roster
            dps_count = 0
            healer_count = 0
            tank_count = 0

            names = ""
            # BACKUP TANKS
            if not len(roster.backup_tanks) == 0:
                tanks = roster.backup_tanks
                for i in tanks:
                    member_name = guild.get_member(int(i))
                    if member_name is not None:
                        names += f"{bot.config['raids']['tank_emoji']}{member_name.display_name.replace("_", r"\_")}\n{roster.backup_tanks[i].replace("_", r"\_")}\n"
                        tank_count += 1

            if tank_count > 0:
                embed.add_field(name=f"{language['Backup_Tanks']} {tank_count}", value=names, inline=True)

            names = ""
            # BACKUP HEALERS
            if not len(roster.backup_healers) == 0:
                backup_healers = roster.backup_healers
                for i in backup_healers:
                    member_name = guild.get_member(int(i))
                    if member_name is not None:
                        names += f"{bot.config['raids']['healer_emoji']}{member_name.display_name.replace("_", r"\_")}\n{roster.backup_healers[i].replace("_", r"\_")}\n"
                        healer_count += 1

            if healer_count > 0:
                embed.add_field(name=f"{language['Backup_Healers']} {healer_count}", value=names, inline=True)

            names = ""
            # BACKUP DPS
            if not len(roster.backup_dps) == 0:
                dps = roster.backup_dps
                for i in dps:
                    member_name = guild.get_member(int(i))
                    if member_name is not None:
                        names += f"{bot.config['raids']['dps_emoji']}{member_name.display_name.replace("_", r"\_")}\n{roster.backup_dps[i].replace("_", r"\_")}\n"
                        dps_count += 1

            if dps_count > 0:
                embed.add_field(name=f"{language['Backup_DPS']} {dps_count}", value=names, inline=True)

            return embed
        except Exception as e:
            logging.error(f"Status Embed Create Error: {e}")
            raise e

    @staticmethod
    def create_new_roster(trial, date, roles_req, leader, memo, pingable):
        # Unlike with other commands, creating a new Roster is always in english

        # Generate the description
        desc = f"Rank(s) Required: {roles_req}\nGroup: <@&{pingable}>"

        if memo != "None":
            desc += f"\n\n{memo}"

        desc += f"\n\nI hope people sign up for this."

        embed = Embed(
            title=f"{trial} {date}",
            description=desc,
            color=Color.blue()
        )
        embed.set_footer(text="Remember to spay or neuter your support!\nAnd mention your sets!")
        embed.set_author(name="Raid Lead: " + leader)
        embed.add_field(name="Calling Healers!", value='To Heal Us!', inline=False)
        embed.add_field(name="Calling Tanks!", value='To Be Stronk!', inline=False)
        embed.add_field(name="Calling DPS!", value='To Stand In Stupid!', inline=False)

        return embed

    @staticmethod
    def create_ranking(rank: Rank, lang, name):
        embed = Embed(
            title=name,
            color=Color.red()
        )
        embed.set_footer(text=f"{lang['Footer']}")
        embed.set_author(name=f"{lang['Author']}")
        embed.add_field(name=f"{lang['Total'] % rank.count}", value=" ", inline=False)
        embed.add_field(name=f"{lang['Last'] % rank.last_called}", value=" ", inline=False)
        embed.add_field(name=f"{lang['Lowest'] % rank.lowest}", value=" ", inline=False)
        embed.add_field(name=f"{lang['Highest'] % rank.highest}", value=" ", inline=False)
        embed.add_field(name=f"{lang['Singles'] % rank.singles}", value=" ", inline=False)
        embed.add_field(name=f"{lang['Doubles'] % rank.doubles}", value=" ", inline=False)
        embed.add_field(name=f"{lang['Samsies'] % rank.samsies}", value=" ", inline=False)
        embed.add_field(name=f"{lang['SixNine'] % rank.six_nine}", value=" ", inline=False)
        embed.add_field(name=f"{lang['FourTwenty'] % rank.four_twenty}", value=" ", inline=False)
        embed.add_field(name=f"{lang['Boob'] % rank.boob}", value=" ", inline=False)
        embed.add_field(name=f"{lang['Pie'] % rank.pie}", value=" ", inline=False)
        return embed

    @staticmethod
    def create_count(count: Count, lang, name, guild_name):
        embed = Embed(
            title=name,
            color=Color.orange()
        )
        embed.set_footer(text=f"{lang['Footer']}")
        embed.set_author(name=f"{lang['Author'] % guild_name}")
        embed.add_field(name=f"{lang['Total']}", value=count.count, inline=True)
        embed.add_field(name=f"{lang['LastRan']}", value=count.lastTrial, inline=True)
        embed.add_field(name=f"{lang['LastDate']}", value=count.lastDate, inline=True)
        embed.add_field(name=f"{lang['Stats']}", value=f"{lang['RoleRuns']}", inline=False)
        embed.add_field(name=f"{lang['DPS']}", value=count.dpsRuns, inline=True)
        embed.add_field(name=f"{lang['Tank']}", value=count.tankRuns, inline=True)
        embed.add_field(name=f"{lang['Healer']}", value=count.healerRuns, inline=True)
        return embed

