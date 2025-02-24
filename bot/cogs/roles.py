import discord
from discord.ext import commands
import logging
from bot import decor as permissions
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")

roles_info = None
agree_role = None
recruits_role = None


def set_roles_info(bot):
    """Function to set the role information on cog load"""
    global roles_info
    global agree_role
    global recruits_role
    guild = bot.get_guild(bot.config['guild'])
    recruits_role = discord.utils.get(guild.roles, name=bot.config["roles"]["default"])
    agree_role = discord.utils.get(guild.roles, name=bot.config["roles"]["unlock"])
    client = MongoClient(bot.config['mongo'])
    database = client.bot
    misc = database.misc
    roles_info = misc.find_one({'roles': "ids"})
    if roles_info is None:
        roles_info = {}
        return
    roles_info = roles_info["data"]


def save_roles_info(config):
    """Function to save new channels information"""
    global roles_info
    client = MongoClient(config['mongo'])
    database = client.bot
    misc = database.misc
    old_rec = misc.find_one({'roles': "ids"})
    if old_rec is not None:
        new_rec = {'$set': {'data': roles_info}}
        misc.update_one({'roles': "ids"}, new_rec)
    else:
        rec = {
            'roles': "ids",
            'data': roles_info
        }
        misc.insert_one(rec)

class Roles(commands.Cog, name="Roles"):
    """Commands related to Discord roles"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_load_on_ready(self, bot):
        set_roles_info(bot)
        logging.info(f"Roles Cog Roles Set")


    @commands.command(name="agree")
    async def agree(self, ctx: commands.Context):
        """For agreeing with the rules of the discord | `!agree`"""
        try:
            await ctx.author.remove_roles(recruits_role)
            await ctx.author.add_roles(agree_role)
            await ctx.author.send(self.bot.config['agree'])
        except discord.Forbidden:
            await ctx.reply(f"I need permission to DM you for this. Please enable DMs on this server.\n"
                            f"I have granted you the role for now, call the command later on for me to DM you important info!")
        except Exception as e:
            await ctx.send("Unable to grant the role, please notify an Admin/Officer")
            logging.error(f"Agree Error: {str(e)}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Listener for reaction add"""
        try:
            guild = self.bot.get_guild(self.bot.config["guild"])
            member = discord.utils.get(guild.members, id=payload.user_id)
            if member.bot:
                return

            if int(payload.channel_id) != int(roles_info["channel"]):
                return

            if str(payload.message_id) not in roles_info.keys():
                logging.error("Could not find message id for reaction add")
                return
            role_type = roles_info[str(payload.message_id)]
            role = self.bot.config["vanity"][role_type][str(payload.emoji)]
            main_role = None
            match role_type:
                case "tank":
                    main_role = "Tank"
                case "healer":
                    main_role = "Healer"
                case "mag":
                    main_role = "DPS"
                case "stam":
                    main_role = "DPS"
            await member.add_roles(discord.utils.get(guild.roles, name=role))
            if main_role is not None:
                await member.add_roles(discord.utils.get(guild.roles, name=main_role))
            await member.send(f"Added role: {role}")
        except discord.Forbidden as e:
            logging.error(
                f"Add Role Error: Forbidden to DM {member.display_name} after adding role, Message: {str(e)}")
        except KeyError as e:
            channel = member.guild.get_channel(self.bot.config["administration"]["private"])
            await channel.send(
                f"User: {member.display_name} attempted to add a role. but I could not find that "
                f"role in the config.")
            logging.error(f"Add Role Error: {str(e)}")
        except Exception as e:
            channel = member.guild.get_channel(self.bot.config["administration"]["private"])
            await channel.send(f"User: {member.display_name} attempted to add a role but there was an error.")
            logging.error(f"Add Role Error: {str(e)}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Listener for reaction remove"""
        try:
            guild = self.bot.get_guild(self.bot.config["guild"])
            member = discord.utils.get(guild.members, id=payload.user_id)
            if member.bot:
                return

            if int(payload.channel_id) != int(roles_info["channel"]):
                return

            if str(payload.message_id) not in roles_info.keys():
                return

            role_type = roles_info[str(payload.message_id)]
            role = self.bot.config["vanity"][role_type][str(payload.emoji)]
            await member.remove_roles(discord.utils.get(guild.roles, name=role))
            await member.send(f"Removed role: {role}")
            if role_type == "misc":
                return
            all_roles = set((self.bot.config["vanity"][role_type]).values())
            if role_type == "mag":
                all_roles.update(set((self.bot.config["vanity"]["stam"]).values()))
            elif role_type == "stam":
                all_roles.update(set((self.bot.config["vanity"]["mag"]).values()))
            all_user_roles = set([i.name for i in member.roles])
            keep_main_role = bool(all_roles.intersection(all_user_roles))
            if not keep_main_role:
                match role_type:
                    case "tank":
                        main_role = "Tank"
                    case "healer":
                        main_role = "Healer"
                    case "mag":
                        main_role = "DPS"
                    case "stam":
                        main_role = "DPS"
                await member.remove_roles(discord.utils.get(guild.roles, name=main_role))
                await member.send(f"You have removed all {main_role} vanities and have been removed from the {main_role} tag")
        except discord.Forbidden as e:
            logging.error(
                f"Remove Role Error: Forbidden to DM {member.display_name} after removing role, Message: {str(e)}")
        except KeyError as e:
            channel = guild.get_channel(self.bot.config["administration"]["private"])
            await channel.send(f"User: {member.display_name} attempted to remove role but I could not find that role "
                               f"in the config.")
            logging.error(f"Remove Role Error: {str(e)}")
        except Exception as e:
            channel = guild.get_channel(self.bot.config["administration"]["private"])
            await channel.send(f"User: {member.display_name} attempted to remove role but there was an error.")
            logging.error(f"Remove Role Error: {str(e)}")

    @commands.command(name="setrolechannel")
    @permissions.has_officer()
    async def setup_role_reactionaries(self, ctx: commands.Context, channel_id=None):
        """Officer command to set up emoji role selections"""
        try:
            def embed_factory(message_type):
                message_color = discord.Color.light_grey()
                title_type = ""
                if message_type.lower() == "tank":
                    emote = self.bot.config['raids']['tank_emoji']
                    message_color = discord.Color.red()
                    title_type = "Tank"
                elif message_type.lower() == "healer":
                    emote = self.bot.config['raids']['healer_emoji']
                    message_color = discord.Color.fuchsia()
                    title_type = "Healer"
                elif message_type.lower() == "mag":
                    emote = self.bot.config['raids']['dps_emoji']
                    message_color = discord.Color.blue()
                    title_type = "Magicka DPS"
                elif message_type.lower() == "stam":
                    emote = self.bot.config['raids']['dps_emoji']
                    message_color = discord.Color.green()
                    title_type = "Stamina DPS"
                else:
                    emote = ""
                    title_type = "Misc"
                embed = discord.Embed(
                    title=f"{message_type.capitalize()} Roles!",
                    color=message_color
                )
                all_classes = ""
                all_classes_emoji = []
                van_dict = self.bot.config["vanity"][message_type.lower()]
                for key in van_dict:
                    all_classes += f"{key}{van_dict[key]}\n"
                    all_classes_emoji.append(key)
                if title_type == "Misc":
                    embed.add_field(name=f"React below for all other stuff.", value=f'{all_classes}', inline=False)
                else:
                    embed.add_field(name=f"React below for what classes you play as for "
                                         f"{emote}{title_type}{emote}", value=f'{all_classes}', inline=False)

                return embed, all_classes_emoji

            if channel_id is None:
                channel_id = ctx.message.channel.id

            new_roles_info = {"channel": channel_id}

            crafted_embed, classes = embed_factory("tank")
            message = await ctx.send(embed=crafted_embed)
            for i in classes:
                await message.add_reaction(i)
            new_roles_info[str(message.id)] = "tank"

            crafted_embed, classes = embed_factory("healer")
            message = await ctx.send(embed=crafted_embed)
            for i in classes:
                await message.add_reaction(i)
            new_roles_info[str(message.id)] = "healer"

            crafted_embed, classes = embed_factory("mag")
            message = await ctx.send(embed=crafted_embed)
            for i in classes:
                await message.add_reaction(i)
            new_roles_info[str(message.id)] = "mag"

            crafted_embed, classes = embed_factory("stam")
            message = await ctx.send(embed=crafted_embed)
            for i in classes:
                await message.add_reaction(i)
            new_roles_info[str(message.id)] = "stam"

            crafted_embed, classes = embed_factory("misc")
            message = await ctx.send(embed=crafted_embed)
            for i in classes:
                await message.add_reaction(i)
            new_roles_info[str(message.id)] = "misc"

            global roles_info
            roles_info = new_roles_info

            save_roles_info(self.bot.config)

        except Exception as e:
            await ctx.send("Unable to setup messages and roles.")
            logging.error(f"Roleset Error: {str(e)}")

    @commands.command(name="updaterole")
    @permissions.has_officer()
    async def update_role_emoji(self, ctx: commands.Context, update_role_type=None):
        """Officer command to update selection | !updaterole [type]"""
        try:
            if update_role_type is None:
                await ctx.send(f"Need to specify type to update")

            def embed_factory(message_type):
                message_color = discord.Color.light_grey()
                title_type = ""
                if message_type.lower() == "tank":
                    emote = self.bot.config['raids']['tank_emoji']
                    message_color = discord.Color.red()
                    title_type = "Tank"
                elif message_type.lower() == "healer":
                    emote = self.bot.config['raids']['healer_emoji']
                    message_color = discord.Color.fuchsia()
                    title_type = "Healer"
                elif message_type.lower() == "mag":
                    emote = self.bot.config['raids']['dps_emoji']
                    message_color = discord.Color.blue()
                    title_type = "Magicka DPS"
                elif message_type.lower() == "stam":
                    emote = self.bot.config['raids']['dps_emoji']
                    message_color = discord.Color.green()
                    title_type = "Stamina DPS"
                else:
                    emote = ""
                    title_type = "Misc"
                embed = discord.Embed(
                    title=f"{message_type.capitalize()} Roles!",
                    color=message_color
                )
                all_classes = ""
                all_classes_emoji = []
                van_dict = self.bot.config["vanity"][message_type.lower()]
                for key in van_dict:
                    all_classes += f"{key}{van_dict[key]}\n"
                    all_classes_emoji.append(key)
                if title_type == "Misc":
                    embed.add_field(name=f"React below for all other stuff.", value=f'{all_classes}', inline=False)
                else:
                    embed.add_field(name=f"React below for what classes you play as for "
                                         f"{emote}{title_type}{emote}", value=f'{all_classes}', inline=False)

                return embed, all_classes_emoji

            guild = self.bot.get_guild(self.bot.config["guild"])
            channel = guild.get_channel(int(roles_info["channel"]))
            msg_id = 0
            for key, value in roles_info.items():
                if value == update_role_type.lower():
                    msg_id = int(key)
            message = await channel.fetch_message(msg_id)
            new_embed, classes = embed_factory(update_role_type)
            await message.edit(embed=new_embed)
            for i in classes:
                await message.add_reaction(i)

            await ctx.send(f"Updated everything.")

        except Exception as e:
            await ctx.send(f"Sorry, I was unable to update that.")
            logging.error(f"Unable to update the type, Message: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Roles(bot))
