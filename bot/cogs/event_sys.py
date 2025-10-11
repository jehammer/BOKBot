from discord.ext import commands
from discord import app_commands, Interaction, utils, Member, Role
import logging
import time

# My created imports
from bot import decor as permissions
from bot.errors import *
from bot.modals import *
from bot.models import Roster, Count
from bot.services import Utilities, RosterExtended, EmbedFactory
from bot.ui import RosterSelector


class EventsSys(commands.Cog, name="EventsSys"):
    """Automated/Lower Level Management Stuff for the Events system(s)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_sort_rosters(self):
        try:
            # Order Channels correctly now
            new_positions = RosterExtended.sort_rosters(self.bot.rosters)
            for i in new_positions:
                channel = self.bot.get_channel(i)
                await channel.edit(position=new_positions[i])
                time.sleep(2)
        except Exception as e:
            logging.error(f"Position Change Error: {str(e)}")
            await interaction.followup.send(
                f"{Utilities.format_error(user_language, self.bot.language[user_language]['replies']['TrialModify']['CantPosition'])}")
            return

    # Creator-Only commands

    @commands.command(name="roster")
    @permissions.creator_only()
    async def printout_roster(self, ctx: commands.Context, channel_id):
        """Printout a roster directly for any debugging needs"""
        try:
            await ctx.reply(rosters[str(channel_id)].get_roster_data())
        except Exception as e:
            await ctx.reply(f"Unable to complete: {str(e)}")

    @commands.command(name="allrosters")
    @permissions.creator_only()
    async def printout_all_rosters(self, ctx: commands.Context):
        """Printout all rosters directly for any debugging needs"""
        try:
            for i in rosters:
                await ctx.reply(rosters[i].get_roster_data())
        except Exception as e:
            await ctx.reply(f"Unable to complete: {str(e)}")

    @commands.command(name="saverosters")
    @permissions.creator_only()
    async def save_roster_info(self, ctx: commands.Context):
        """Force Save current Roster Map and Rosters"""
        try:
            for i in self.bot.rosters: #TODO: make it save based on roster instance type
                self.bot.librarian.put_roster(i, rosters[i].get_roster_data())
            await ctx.reply(f"Rosters saved.")

        except Exception as e:
            await ctx.reply(f"Unable to complete: {str(e)}")

    @commands.command(name="reloadrosters")
    @permissions.creator_only()
    async def reload_roster_info(self, ctx: commands.Context):
        """Force Reload all Roster information"""
        try:
            logging.info("Force Reload Roster Information Called")
            global rosters

            fetched = self.bot.librarian.get_all_rosters()
            if fetched is not None:
                rosters = fetched
                logging.info(f"Found and Loaded Rosters")
            await ctx.reply(f"Roster Information Reloaded.")
        except Exception as e:
            await ctx.reply(f"Unable to complete: {str(e)}")

    @commands.command(name="resort")
    @permissions.creator_only()
    async def force_resort_rosters(self, ctx: commands.Context):
        """Force all Rosters to be sorted again."""
        try:
            new_positions = RosterExtended.sort_rosters(rosters)
            for i in new_positions:
                channel = self.bot.get_channel(i)
                await channel.edit(position=new_positions[i])
                time.sleep(2)
            await ctx.reply(f"Finished Sorting!")
        except Exception as e:
            await ctx.reply(f"Unable to complete: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(EventsSys(bot))
