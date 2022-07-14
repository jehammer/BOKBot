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
        except Exception as e:
            await ctx.send("Unable to grant role, please notify a Storm Bringer")
            logging.error("Agree error: " + str(e))
            return
        try:
            message = f"Welcome to Breath Of Kynareth! I am here to guide you on the basics of BOKBot!\n" \
                      f"You can find more information in <#932438565009379358> for what to do. But lets get the basics out.\n" \
                      f"To start, you can set discord server roles and default roster role in <#933596721630548059> by using the `!role [role]` " \
                      f"command. You can see a list of any available roles by calling `!roles`\n" \
                      f"Next, we should set your default role for Trials signup. In the same channel as before, use `!default [role]` to set " \
                      f"your default when using `!su` or `!bu`. The options you have are DPS, Tank, or Healer.\n" \
                      f"The BOKBot Guide channel will have more examples for you to look at if needed. " \
                      f"If you need some help contact Drakador, he will be more than happy to lend a hand!\n" \
                      f"Some quick examples of the commands above would be: `!role ebonheart` and `!default dps`\n" \
                      f"If you ever need some help with Trial abbreviations, just use `!abbr` for a quick DM!"
            await user.send(message)
        except Exception as e:
            await ctx.send("I was unable to send you the DM. Please enable DMs for this server and try again.")
            logging.error("Agree DM error: " + str(e))

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
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    await user.send(req + " role granted")

            elif req == "healer":
                role = nextcord.utils.get(ctx.guild.roles, name="Healer")
                if user in role.members:
                    await user.remove_roles(role)
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    await user.send(req + " role granted")

            elif req == "dps":
                role = nextcord.utils.get(ctx.guild.roles, name="DPS")
                if user in role.members:
                    await user.remove_roles(role)
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    await user.send(req + " role granted")

            elif req == "ebonheart":
                role = nextcord.utils.get(ctx.guild.roles, name="Ebonheart")
                if user in role.members:
                    await user.remove_roles(role)
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    await user.send(req + " role granted")

            elif req == "daggerfall":
                role = nextcord.utils.get(ctx.guild.roles, name="Daggerfall")
                if user in role.members:
                    await user.remove_roles(role)
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    await user.send(req + " role granted")

            elif req == "aldmeri":
                role = nextcord.utils.get(ctx.guild.roles, name="Aldmeri")
                if user in role.members:
                    await user.remove_roles(role)
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    await user.send(req + " role granted")

            elif req == "crafter":
                role = nextcord.utils.get(ctx.guild.roles, name="Crafter")
                if user in role.members:
                    await user.remove_roles(role)
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    await user.send(req + " role granted")

            elif req == "ex-cons":
                role = nextcord.utils.get(ctx.guild.roles, name="Ex-Cons")
                if user in role.members:
                    await user.remove_roles(role)
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    await user.send(req + " role granted")

            elif req == "160":
                role = nextcord.utils.get(ctx.guild.roles, name="Kyne's Follower")
                if user in role.members:
                    await user.remove_roles(role)
                    await user.send(req + " role removed")
                else:
                    await user.add_roles(role)
                    await user.send(req + " role granted")
            else:
                await ctx.send("Role not found. use `!roles` to see which roles you can request.")
        except Exception as e:
            await ctx.send("Unable to grant role, please notify a Storm Bringer")
            logging.error("Role error: " + str(e))

    @commands.command()
    async def roles(self, ctx: commands.Context):
        """Lists the roles you can request from the bot"""
        message = f"Healer: Grants you the Healer tag\n" \
                  f"Tank: Grants you the Tank tag\n" \
                  f"DPS: Grants you the DPS tag\n" \
                  f"Aldmeri: Grants you the Aldmeri tag for the AD Alliance\n" \
                  f"Daggerfall: Grants you the Daggerfall tag for the DC Alliance\n" \
                  f"Ebonheart: Grants you the Ebonheart tag for the EP Alliance\n" \
                  f"Crafter: Grants you the Crafter tag so you can help others when they need something crafted.\n" \
                  f"Ex-Cons: For all people who came to PC from Console.\n" \
                  f"160: Grants you the Kyne's Follower role, which means you are at least CP 160 for gear trading in trials."
        await ctx.send(message)


def setup(bot: commands.Bot):
    bot.add_cog(Roles(bot))
