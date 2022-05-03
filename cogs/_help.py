from typing import Optional
from nextcord.ext import commands
import logging
from nextcord import Embed


class MyHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return '{0.clean_prefix}{1.qualified_name} {1.signature}'.format(self, command)

    async def _help_embed(self, title: str, description: Optional[str] = None, mapping: Optional[str] = None):
        embed = Embed(title=title)
        if description:
            embed.description = description
        if mapping:
            pass
            # Add a short description of command sin each cog
        for cog, command_set in mapping.items():
            filtered = await self.filter_commands(command_set, sort=True)
            if not filtered:
                continue
            name = cog.qualified_name if cog else "No Category"
            # Use an en-space
            cmd_list = "\u2002".join(
                f"`{self.context.clean_prefix}{cmd.name}`" for cmd in filtered
            )
            value = (

                # Will give command list if there is a description, else just the command list

                f"{cog.description}\n{cmd_list}"
                if cog and cog.description
                else cmd_list
            )
            embed.add_field(name=name, value=value)
        return embed

    async def send_bot_help(self, mapping: dict):
        embed = await self._help_embed(
            title="Bot Commands",
            description=self.context.bot.description,
            mapping=mapping
        )
        await self.get_destination().send(embed=embed)
        # TODO: Continue from here: https://youtu.be/TzR8At0SFQI?t=701

    async def send_command_help(self, command):
        pass

    async def send_cog_help(self, cog):
        pass

    send_group_help = send_command_help


class Help(commands.Cog, name="Help"):
    """Shows help info about commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logging.info("Help cog loaded")

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
