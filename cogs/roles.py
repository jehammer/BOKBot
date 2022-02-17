import nextcord
from nextcord.ext import commands
import logging


class Roles(commands.Cog, name="Roles"):
    """Receives roles commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def agree(self, ctx: commands.Context):
        """for agreeing with the rules of the discord"""
        try:
            user = ctx.message.author
            role = nextcord.utils.get(ctx.guild.roles, name="Kynes Founded")
            await user.add_roles(role)
            # await ctx.message.delete()
            await user.send("Welcome to Breath of Kynareth!")
        except Exception as e:
            await ctx.message.author.send("Unable to grant role, please notify a Storm Bringer")
            logging.error("Agree error: " + str(e))

    @commands.command()
    async def role(self, ctx: commands.Context):
        """use !role [role] to get the request role from roles"""
        try:
            msg = ctx.message.content
            msg = msg.split(" ", 1)  # Split into 2 parts of a list
            req = msg[1].lower()
            user = ctx.message.author
            # code reuse is just beautiful. Though I am user there are better ways to do this. I will look into it.

            if req == "tank":
                role = nextcord.utils.get(ctx.guild.roles, name="Tank")
                if user in role.members:
                    await user.remove_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role granted")

            elif req == "healer":
                role = nextcord.utils.get(ctx.guild.roles, name="Healer")
                if user in role.members:
                    await user.remove_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role granted")

            elif req == "dps":
                role = nextcord.utils.get(ctx.guild.roles, name="DPS")
                if user in role.members:
                    await user.remove_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role granted")

            elif req == "ebonheart":
                role = nextcord.utils.get(ctx.guild.roles, name="Ebonheart")
                if user in role.members:
                    await user.remove_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role granted")

            elif req == "daggerfall":
                role = nextcord.utils.get(ctx.guild.roles, name="Daggerfall")
                if user in role.members:
                    await user.remove_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role granted")

            elif req == "aldmeri":
                role = nextcord.utils.get(ctx.guild.roles, name="Aldmeri")
                if user in role.members:
                    await user.remove_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role granted")

            elif req == "crafter":
                role = nextcord.utils.get(ctx.guild.roles, name="Crafter")
                if user in role.members:
                    await user.remove_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role granted")

            elif req == "ex-cons":
                role = nextcord.utils.get(ctx.guild.roles, name="Ex-Cons")
                if user in role.members:
                    await user.remove_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role granted")

            elif req == "160":
                role = nextcord.utils.get(ctx.guild.roles, name="Kyne's Follower")
                if user in role.members:
                    await user.remove_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    # await ctx.message.delete()
                    await user.send(req + " role granted")
            else:
                await user.send("Role not found. use !roles to see which roles you can request.")
        except Exception as e:
            await ctx.message.author.send("Unable to grant role, please notify a Storm Bringer")
            logging.error("Role error: " + str(e))

    @commands.command()
    async def roles(self, ctx: commands.Context):
        """Lists the roles you can request from the bot"""
        await ctx.send("Healer, DPS, Tank, Aldmeri, Daggerfall, Ebonheart, Crafter, Ex-Cons, 160")


def setup(bot: commands.Bot):
    bot.add_cog(Roles(bot))
