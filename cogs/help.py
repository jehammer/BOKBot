import logging
import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')  # , datefmt="%Y-%m-%d %H:%M:%S")


async def send_embed(ctx, embed):
    try:
        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(f"Help Embed Send Error: {str(e)}")


class Helpers(commands.Cog):
    """Commands for Bot help and more"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, *input):
        """Help system of BOKBot"""

        try:
            # checks if cog parameter was given
            # if not: sending all modules and commands not associated with a cog
            pages = None
            if not input:

                # starting to build embed
                emb = discord.Embed(title='Commands and modules', color=discord.Color.blue(),
                                    description=f'Use `!help <module>` to gain more information about that module\n'
                                                f'Be sure to check <#932438565009379358> for more in-depth help!')

                # iterating trough cogs, gathering descriptions
                cogs_desc = ''
                for cog in self.bot.cogs:
                    cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'

                # adding 'list' of cogs to embed
                emb.add_field(name='Modules', value=cogs_desc, inline=False)

                # integrating trough uncategorized commands
                commands_desc = ''
                for command in self.bot.walk_commands():
                    # if cog not in a cog
                    # listing command if cog name is None and command isn't hidden
                    if not command.cog_name and not command.hidden:
                        commands_desc += f'{command.name} - {command.help}\n'

                # adding those commands to embed
                if commands_desc:
                    emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

                # setting information about author
                emb.add_field(name="About",
                              value=f"BOKBot is Developed by Drakador, for any and all support about it feel\n "
                                    f"free to ask in chat or ping him.")
                emb.set_footer(text=f"Thank you for using BOKBot")

            # block called when one cog-name is given
            # trying to find matching cog and it's commands
            elif len(input) == 1:
                found = False
                # iterating through cogs
                for cog in self.bot.cogs:
                    # check if cog is the matching one
                    if cog.lower() == input[0].lower():

                        # making title - getting description from doc-string below class
                        page = discord.Embed(title=f'{cog} - Commands', description=self.bot.cogs[cog].__doc__,
                                            color=discord.Color.green())

                        page.add_field(name="", value="Use `!help <command>` for specific command information",
                                      inline=False)

                        next_page = discord.Embed(title=f'{cog} - Commands (Cont)', description=self.bot.cogs[cog].__doc__,
                                            color=discord.Color.green())

                        # getting commands from cog
                        count = 0
                        pages = []

                        for command in self.bot.get_cog(cog).get_commands():
                            # if cog is not hidden
                            if not command.hidden:
                                if count == 24:
                                    pages.append(page)
                                    count = 0
                                    page = next_page
                                else:
                                    page.add_field(name=f"", value=f"`!{command.name}`\t{command.help}", inline=False)
                                count += 1
                        for command in self.bot.get_cog(cog).get_app_commands():
                            if count == 24:
                                pages.append(page)
                                count = 0
                                page = next_page
                            else:
                                page.add_field(name=f"", value=f"`/{command.name}`\t{command.description}", inline=False)
                            count += 1
                        pages.append(page)
                        # found cog - breaking loop
                        found = True
                        break

                # It is a command in a cog, iterate through and find the specific command within the cog
                if found is False:
                    for cog in self.bot.cogs:
                        for command in self.bot.get_cog(cog).get_commands():
                            if command.name.lower() == input[0].lower() or input[0].lower() in command.aliases:
                                if not command.hidden:
                                    # Check for aliases or not aliases
                                    if len(command.aliases) > 0:
                                        aliases = ""
                                        for alias in command.aliases:
                                            aliases += alias + ", "
                                        aliases = aliases[:-2]  # Cut off the last comma and whitespace
                                        emb = discord.Embed(title=f'{cog}: !{command} - aliases: {aliases}',
                                                            color=discord.Color.blurple())
                                    else:
                                        emb = discord.Embed(title=f'{cog}: !{command}', color=discord.Color.blurple())
                                    emb.add_field(name=f"", value=f"{command.help}", inline=False)
                                # found so break
                                    found = True
                                else:
                                    break
                        if not found:
                            for command in self.bot.get_cog(cog).get_app_commands():
                                if command.name.lower() == input[0].lower():
                                    # Check for aliases or not aliases
                                    emb = discord.Embed(title=f'{cog}: /{command.name}', color=discord.Color.blurple())
                                    emb.add_field(name=f"", value=f"{command.description}", inline=False)
                                    # found so break
                                    found = True
                        if found is True:
                            break

                    # if input not found
                    # yes, for-loops have an else statement, it's called when no 'break' was issued

                    else:
                        emb = discord.Embed(title="Impossible. Perhaps the archives are incomplete?",
                                            description=f"I do not have a module or command called `{input[0]}`",
                                            color=discord.Color.orange())
                        emb.set_image(url='https://media.discordapp.net/attachments/911730032286785536/1073645138506694806/Incomplete.png')

            # too many cogs requested - only one at a time allowed
            elif len(input) > 1:
                emb = discord.Embed(title="That's too much",
                                    description="Please request only one module or command at once",
                                    color=discord.Color.orange())

            else:
                emb = discord.Embed(title="It's a magical place.",
                                    description="I don't know how you got here. By all accounts, this code is unreachable.",
                                    color=discord.Color.red())

            # sending reply embed using our own function defined above
            if pages is not None:
                for i in pages:
                    await send_embed(ctx, i)
            else:
                await send_embed(ctx, emb)
        except Exception as e:
            await ctx.send("I was unable to complete the help command")
            logging.error(f"Help command Error: {str(e)}")

    @commands.command(name="starter", aliases=["start"])
    async def send_starter_info(self, ctx: commands.Context):
        """DM's you some BOKBot starter information"""
        try:
            info = 'Welcome to learning BOKBot!\n' \
                   'There is a lot of things that I can do. In any channel you can make use of `!help` to get some command help.\n' \
                   'You can get further information for each section of commands, also called "cogs" or "modules" by calling ' \
                   'that specific cog/module or command `!help [command/cog/module]` (without the [] of course).\n' \
                   'BOKBot features its own system for Trial rosters which is the majority of its function. Something that ' \
                   'you would want to look into is the defaults system. You can set your default to be a healer, tank, or dps ' \
                   'via `!default [role]` which can be used to bypass having to specify your role when doing `!su` or `!bu` ' \
                   'in a roster. Otherwise when joining a roster you must specify your role then any optional comment you ' \
                   'may wish to add.\n' \
                   'I strongly advise checking out <#932438565009379358> for more information on what BOKBot can do.\n' \
                   'If you have any questions, feel free to ask for help in the discord, or ping/dm Drakador as he made me and ' \
                   'can easily help you out!'
            await ctx.author.send(info)
        except discord.Forbidden as e:
            await ctx.send(f"I do not have permission to DM you, please turn on DM's from non friends for this server.")
            logging.error(f"Starter Error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Helpers(bot))
