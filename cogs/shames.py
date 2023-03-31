import discord
from discord.ext import commands
import logging
import asyncio
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


class Shames(commands.Cog, name="Shames"):
    """See peoples shames"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="vundees")
    async def vundees_moment(self, ctx: commands.Context):
        """He splooged."""
        try:
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730140604678204/Vundees.gif')
        except Exception as e:
            await ctx.send("Unable to send image")
            logging.error("Vundees error: " + str(e))

    @commands.command(name="lost")
    async def lost(self, ctx: commands.Context):
        """Then he was lost!"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/975825818506903562/Lost_died.gif')

    @commands.command(name="arma")
    async def get_arma_moment(self, ctx: commands.Context):
        """Arma Moments"""
        try:
            ran = random.randint(1, 2)
            match ran:
                case 1:
                    await ctx.send(
                        'https://media.discordapp.net/attachments/911730032286785536/911730134044794930/Arma.gif')
                case 2:
                    await ctx.send('https://youtu.be/SQ9oCUNNbxc')
        except Exception as e:
            await ctx.send("Unable to send image")
            logging.error("Arma error: " + str(e))

    @commands.command(name="drak")
    async def get_drak_moment(self, ctx: commands.Context):
        """Drak Moment"""
        try:
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730136628461589/Drak.gif')
        except Exception as e:
            await ctx.send("Unable to send gif")
            logging.error("Drak error: " + str(e))

    @commands.command(name="bever")
    async def bever_moment(self, ctx: commands.Context):
        """Bever stuff"""
        try:
            await ctx.send("https://media.discordapp.net/attachments/911730032286785536/987806807386894336/Bever.png")
        except Exception as e:
            await ctx.send("Unable to send the image")
            logging.error(f"Bever error: {str(e)}")

    @commands.command(name="auddy")
    async def auddy_moment(self, ctx: commands.Context):
        """It tickled the snoot"""
        try:
            await ctx.send("https://media.discordapp.net/attachments/911730032286785536/911730135034646558/Auddy.gif")
        except Exception as e:
            await ctx.send("Unable to send the gif")
            logging.error(f"Auddy error: {str(e)}")

    @commands.command(name="dracus", aliases=["drac"])
    async def send_dracus_image(self, ctx: commands.Context):
        """His joke was ruined"""
        try:
            await ctx.send('https://media.discordapp.net/attachments/911730032286785536/1046640340641271838/Dracus.png')
        except Exception as e:
            await ctx.send("Unable to send the image")
            logging.error(f"Dracus Image error: {str(e)}")

    @commands.command(name="rng")
    async def rng(self, ctx: commands.Context):
        """RNG In vAA HM"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730139770019921/RNG.gif')


async def setup(bot: commands.Bot):
    await bot.add_cog(Shames(bot))
