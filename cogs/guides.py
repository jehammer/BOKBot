import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


class Guides(commands.Cog, name="Guides"):
    """Receives trial guide commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='hrc', aliases=['vhrc', 'hrchm', 'vhrchm'])
    async def send_hrc_gif(self, ctx: commands.Context):
        """A helpful gif for vHRC HM"""
        try:
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/1043799209771548683/HRC_HM.gif')
        except Exception as e:
            await ctx.send("Unable to send the message")
            logging.error(f"HRC gif error: {str(e)}")

    @commands.command(name="as", aliases=["nas", "vas"])
    async def as_gif(self, ctx: commands.Context):
        """Kite gif for AS"""
        try:
            await ctx.send("https://media.discordapp.net/attachments/911730032286785536/1076198685232353360/vAS.gif")
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"AS Gif error: {str(e)}")

    @commands.command(name="reef")
    async def reef_image(self, ctx: commands.Context):
        """Helpful image for DSR"""
        try:
            await ctx.send("https://media.discordapp.net/attachments/911730032286785536/990441515979505714/Reef.png")
        except Exception as e:
            await ctx.send("Unable to send the image")
            logging.error(f"Reef error: {str(e)}")

    @commands.command(name="abbr")
    async def dm_trial_abbreviations(self, ctx: commands.Context):
        """DMs the User the Trial abbreviations"""
        message = f"n - Normal\n" \
                  f"v - Veteran\n" \
                  f"+[#] - How many Minis are up for the Arena type Trials\n" \
                  f"hm - Hard Mode\n" \
                  f"hrc - Hel Ra Citadel\n" \
                  f"aa - Atherian Archive\n" \
                  f"so - Sanctum Ophidia\n" \
                  f"mol - Maw of Lorkhaj\n" \
                  f"hof - Halls of Fabrication\n" \
                  f"as - Asylum Sanctorium\n" \
                  f"cr - Cloud Rest\n" \
                  f"ss - Sunspire\n" \
                  f"ka - Kyne's Aegis\n" \
                  f"rg - Rockgrove\n" \
                  f"dsr - Dreadsail Reef"
        author = ctx.author
        await author.send(message)

    @commands.command(name="ka", aliases=["vka", "nka"])
    async def vka(self, ctx: commands.Context):
        """Something you wanna see for KA"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911837688141856768/congaline.png')

    @commands.command(name="backyard", aliases=["yard", "back", "milkshake"])
    async def send_backyard_image(self, ctx: commands.Context):
        """MOL Backyard Guide"""
        try:
            await ctx.send(
                "https://media.discordapp.net/attachments/911730032286785536/1060063970284818452/Running_Gif.gif")
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"Backyard Error: {str(e)}")

    @commands.command(name="zhaj", aliases=["mol1"])
    async def send_zhaj_image(self, ctx: commands.Context):
        """MOL Zhaj positioning good for Yandir and Vrol too"""
        try:
            await ctx.send(
                "https://cdn.discordapp.com/attachments/911730032286785536/1060064086416691200/vMoL-Zhaj-Positioning.png")
        except Exception as e:
            await ctx.send("Unable to send the image")
            logging.error(f"Zhaj Error: {str(e)}")

    @commands.command(name="mol", aliases=["nmol", "vmol"])
    async def send_mol_images(self, ctx: commands.Context):
        """Both MOL guide images"""
        try:
            await ctx.send(
                "https://cdn.discordapp.com/attachments/911730032286785536/1060064086416691200/vMoL-Zhaj-Positioning.png")
            await ctx.send(
                "https://media.discordapp.net/attachments/911730032286785536/1060063970284818452/Running_Gif.gif")
        except Exception as e:
            await ctx.send("Unable to send the image and gif")
            logging.error(f"MOL Error: {str(e)}")

    @commands.command(name="twins")
    async def send_twins_commands(self, ctx: commands.Context):
        """Tells you the two twin commands, just in case"""
        try:
            await ctx.send(f"For the MOL Twins, use `!mtwins`\n"
                           f"For the DSR Twins, use `!dtwins`")
        except Exception as e:
            await ctx.send("Unable to send information.")
            logging.error(f"Twins error: {str(e)}")

    @commands.command(name="mtwins")
    async def send_mol_twins_gif(self, ctx: commands.Context):
        """Gif for MOL Twins"""
        try:
            await ctx.send(f"https://media.discordapp.net/attachments/911730032286785536/1115423531006705664/Twins_Rotate.gif")
        except Exception as e:
            await ctx.send("Unable to send information.")
            logging.error(f"Twins error: {str(e)}")

    @commands.command(name="dtwins")
    async def send_dsr_twins_img(self, ctx: commands.Context):
        """Img for DSR Twins"""
        try:
            await ctx.send(f"https://media.discordapp.net/attachments/911730032286785536/1115423536404770957/vDSRTwins.png")
        except Exception as e:
            await ctx.send("Unable to send information.")
            logging.error(f"Twins error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Guides(bot))
