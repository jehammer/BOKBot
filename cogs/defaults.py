import discord
from discord.ext import commands
import logging
from pymongo import MongoClient

from bot import bot

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')

# Connect and get values from MongoDB
client = MongoClient(bot.config['mongo'])
database = client['bot']  # Or do it with client.PyTest, accessing collections works the same way.
defaults = database.defaults


class Defaults(commands.Cog, name="Defaults"):
    """Commands related to setting Defaults"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="default")
    async def set_default_role(self, ctx: commands.Context, role="check"):
        """Set or check your default role to dps, healer, or tank when using !su. !default [optional: role]"""
        try:
            role = role.lower()
            user_id = ctx.message.author.id
            if role == "dps" or role == "healer" or role == "tank":
                try:
                    rec = defaults.find_one({'userID': user_id})
                    if rec is None:
                        rec = {
                            'userID': user_id,
                            'default': role
                        }
                        defaults.insert_one(rec)
                    else:
                        rec = {'$set': {'default': role}}
                        defaults.update_one({'userID': user_id}, rec)
                    await ctx.reply(f"{ctx.message.author.display_name}: default role has been set to {role}")
                except Exception as e:
                    await ctx.send(f"I was unable to access the database")
                    logging.error(f"Default error: {str(e)}")
                    return
            elif role == "check":
                try:
                    rec = defaults.find_one({'userID': user_id})
                    if rec is None:
                        await ctx.reply(f"{ctx.message.author.display_name}: No default set")
                    else:
                        await ctx.reply(f"{ctx.message.author.display_name} defaults to: {rec['default']}")
                except Exception as e:
                    await ctx.send(f"I was unable to access the database")
                    logging.error(f"Default error: {str(e)}")
                    return
            else:
                await ctx.reply("Please specify an acceptable role. dps, healer, or tank.")
        except Exception as e:
            await ctx.send("Unable to set default role")
            logging.error(f"Default Role Set Error: {str(e)}")

    @commands.command(name="setdef")
    async def admin_set_default_role(self, ctx: commands.Context, m: discord.Member, role="check"):
        """Admin way of manually assigning default roles"""
        try:
            officer = discord.utils.get(ctx.message.author.guild.roles, name=self.bot.config['roles']['admin'])
            user = ctx.message.author
            if user in officer.members:
                role = role.lower()
                user_id = m.id
                if role.lower() == "dps" or role.lower() == "healer" or role.lower() == "tank":
                    try:
                        rec = defaults.find_one({'userID': user_id})
                        if rec is None:
                            rec = {
                                'userID': user_id,
                                'default': role
                            }
                            defaults.insert_one(rec)
                        else:
                            rec = {'$set': {'default': role}}
                            defaults.update_one({'userID': user_id}, rec)
                        await ctx.reply(f"{m.display_name}: default role has been set to {role}")
                    except Exception as e:
                        await ctx.send(f"I was unable to access the database")
                        logging.error(f"Default error: {str(e)}")
                        return
                elif role.lower() == "check":
                    try:
                        rec = defaults.find_one({'userID': user_id})
                        if rec is None:
                            await ctx.reply(f"{ctx.message.author.display_name}: No default set")
                        else:
                            await ctx.reply(f"{ctx.message.author.display_name} defaults to: {rec['default']}")
                    except Exception as e:
                        await ctx.send(f"I was unable to access the database")
                        logging.error(f"Default error: {str(e)}")
                        return
                else:
                    await ctx.reply("Please specify the correct role. dps, healer, or tank.")
            else:
                await ctx.reply("You do not have permission to do this")
        except Exception as e:
            await ctx.send("Unable to set default role")
            logging.error(f"Admin Default Role Set Error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Defaults(bot))
