import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


class Roles(commands.Cog, name="Roles"):
    """Receives roles commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def agree(self, ctx: commands.Context):
        """For agreeing with the rules of the discord"""
        try:
            role = discord.utils.get(ctx.guild.roles, name=self.bot.config["raids"]["roles"]["base"])
            if role != "@everyone":
                await ctx.message.author.add_roles(role)
            await ctx.author.send(self.bot.config['agree'])
        except Exception as e:
            await ctx.send("Unable to grant the role, please notify an Admin/Officer")
            logging.error(f"Agree Error: {str(e)}")

    @commands.command()
    async def role(self, ctx: commands.Context, role=None):
        """use !role [role] to get the request role from roles"""
        try:
            if role is None:
                await ctx.send(f"Please include a role to add")
                return
            user = ctx.author
            total_roles = self.bot.config['roles']['vanity']
            role_name = total_roles.get(role.lower()).get('role_name')
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if user in role.members:
                await ctx.author.remove_roles(role)
                await user.send(f"Removed role: {role_name}")
            else:
                await ctx.author.add_roles(role)
                await user.send(f"Added role: {role_name}")
        except Exception as e:
            await ctx.send("Unable to grant roles, please notify an Admin/Officer")
            logging.error(f"Add Role Error: {str(e)}")

    @commands.command()
    async def roles(self, ctx: commands.Context):
        """Lists the roles you can request from the bot"""
        total_roles = self.bot.config['roles']['vanity']
        msg = ""
        for i in total_roles.keys():
            msg += f"{i}: {total_roles.get(i)['explain']}\n"
        await ctx.send(msg)


async def setup(bot: commands.Bot):
    await bot.add_cog(Roles(bot))
