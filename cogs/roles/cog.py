import nextcord
from nextcord.ext import commands

class Roles(commands.Cog, name="Roles"):
    """Recieves roles commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #@commands.command()
    #async def gif(self, ctx: commands.Context):
    #    """Checks for a response from the bot"""
    #    await ctx.send("Here is a gif")

    @commands.command()
    async def agree(self, ctx: commands.Context):
        """for agreeing with the rules of the discord"""
        try:
            user = ctx.message.author
            role = nextcord.utils.get(user.server.roles, name="Kynes Founded")
            await user.add_roles(user, role)
            await ctx.message.delete()
            await user.send_message("Welcome to Breath of Kynareth!")
        except:
            await ctx.message.author.send_message("Error, unable to grant role, please notify a Storm Bringer")

    @commands.command()
    async def role(self, ctx: commands.Context):
        """use !role [role] to get the request role from roles"""
        try:
            msg = ctx.message.content
            msg = msg.split(" ",1) #Split into 2 parts of a list
            req = msg[1].lower()
            user = ctx.message.author

            #code reuse is just beautiful. Though I am user there are better ways to do this. I will look into it.

            if req == "tank":
                role = nextcord.utils.get(user.server.roles, name="Tank")
                if role in user.roles():
                    await user.remove_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role removed")
                else:
                    await user.add_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role granted")

            elif req == "healer":
                role = nextcord.utils.get(user.server.roles, name="Healer")
                if role in user.roles():
                    await user.remove_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role removed")
                else:
                    await user.add_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role granted")

            elif req == "dps":
                role = nextcord.utils.get(user.server.roles, name="DPS")
                if role in user.roles():
                    await user.remove_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role removed")
                else:
                    await user.add_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role granted")  

            elif req == "ebonheart":
                role = nextcord.utils.get(user.server.roles, name="Ebonheart")
                if role in user.roles():
                    await user.remove_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role removed")
                else:
                    await user.add_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role granted")  

            elif req == "daggerfall":
                role = nextcord.utils.get(user.server.roles, name="Daggerfall")
                if role in user.roles():
                    await user.remove_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role removed")
                else:
                    await user.add_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role granted")

            elif req == "aldmeri":
                role = nextcord.utils.get(user.server.roles, name="Aldmeri")
                if role in user.roles():
                    await user.remove_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role removed")
                else:
                    await user.add_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role granted")

            elif req == "crafter":
                role = nextcord.utils.get(user.server.roles, name="Crafter")
                if role in user.roles():
                    await user.remove_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role removed")
                else:
                    await user.add_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role granted")
                
            elif req == "ex-cons":
                role = nextcord.utils.get(user.server.roles, name="Ex-Cons")
                if role in user.roles():
                    await user.remove_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role removed")
                else:
                    await user.add_roles(user, role)
                    await ctx.message.delete()
                    await user.send_message(req + " role granted")

            else:
                await user.send_message("Error, role not found. use !roles to see which roles you can request.")                   
        except:
            await ctx.message.author.send_message("Error, unable to grant role, please notify a Storm Bringer")        

    @commands.command()
    async def roles(self, ctx: commands.Context):
        """Lists the roles you can request from the bot"""
        await ctx.send("Healer, DPS, Tank, Aldmeri, Daggerfall, Ebonheart, Crafter, Ex-Cons") 
        
def setup(bot: commands.Bot):
    bot.add_cog(Roles(bot))