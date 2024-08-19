from discord import TextStyle, Embed, Color

from models import Roster


class EmbedFactory:
    """Class of Static Methods that create and return embeds"""

    @staticmethod
    def create_status(roster: Roster, language, bot, roles_req, guild):

        dps_count = 0
        healer_count = 0
        tank_count = 0

        desc = f"{language['Rank']} {roles_req}"

        if roster.memo != "None":
            desc += f"\n\n{roster.memo}"

        embed = Embed(
            title=f"{roster.trial} {roster.date}",
            description=desc,
            color=Color.green()
        )
        embed.set_footer(text=f"{language['Footer']}")
        embed.set_author(name=f"{language['Author']} {roster.leader}")

        names = ""
        # DPS
        if not len(roster.dps) == 0:
            dps = roster.dps
            for i in dps:
                member_name = guild.get_member(int(i))
                if member_name is not None:
                    names += f"{bot.config['raids']['dps_emoji']}{member_name.display_name} {roster.dps[i]}\n"
                    dps_count += 1

        embed.add_field(name=f"{language['DPS']} {dps_count}/{roster.dps_limit}", value=names, inline=True)

        names = ""
        # TANKS
        if not len(roster.tanks) == 0:
            tanks = roster.tanks
            for i in tanks:
                member_name = guild.get_member(int(i))
                if member_name is not None:
                    names += f"{bot.config['raids']['tank_emoji']}{member_name.display_name} {roster.tanks[i]}\n"
                    tank_count += 1

        embed.add_field(name=f"{language['Tanks']} {tank_count}/{roster.tank_limit}", value=names, inline=True)

        names = ""
        # HEALERS
        if not len(roster.healers) == 0:
            for i in roster.healers:
                member_name = guild.get_member(int(i))
                if member_name is not None:
                    names += f"{bot.config['raids']['healer_emoji']}{member_name.display_name} {roster.healers[i]}\n"
                    healer_count += 1

        embed.add_field(name=f"{language['Healers']} {healer_count}/{roster.healer_limit}", value=names, inline=True)

        # Show Backup/Overflow Roster
        dps_count = 0
        healer_count = 0
        tank_count = 0

        names = ""
        # BACKUP DPS
        if not len(roster.backup_dps) == 0:
            dps = roster.backup_dps
            for i in dps:
                member_name = guild.get_member(int(i))
                if member_name is not None:
                    names += f"{bot.config['raids']['dps_emoji']}{member_name.display_name} {roster.backup_dps[i]}\n"
                    dps_count += 1


        if dps_count > 0:
            embed.add_field(name=f"{language['Backup_DPS']} {dps_count}", value=names, inline=True)

        names = ""
        # BACKUP TANKS
        if not len(roster.backup_tanks) == 0:
            tanks = roster.backup_tanks
            for i in tanks:
                member_name = guild.get_member(int(i))
                if member_name is not None:
                    names += f"{bot.config['raids']['tank_emoji']}{member_name.display_name} {roster.backup_tanks[i]}\n"
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
                    names += f"{bot.config['raids']['healer_emoji']}{member_name.display_name} {roster.backup_healers[i]}\n"
                    healer_count += 1

        if healer_count > 0:
            embed.add_field(name=f"{language['Backup_Healers']} {healer_count}", value=names, inline=True)

        return embed

    @staticmethod
    def create_new_roster(trial, date, roles_req, leader, memo):
        #Unlike with other commands, creating a new Roster is always in english

        # Generate the description
        desc = f"Rank(s) Required: {roles_req}"

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