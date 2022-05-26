from nextcord.ext import commands
import logging


class Gif(commands.Cog, name="Gifs"):
    """Receives gif commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logging.info("Gifs Cog loaded")

    @commands.command()
    async def arma(self, ctx: commands.Context):
        """Arma Rolls"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730134044794930/Arma.gif')

    @commands.command()
    async def lissa(self, ctx: commands.Context):
        """Lissa Does A Padme"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730138276855818/Lissa.gif')

    @commands.command()
    async def rng(self, ctx: commands.Context):
        """RNG In vAA HM"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730139770019921/RNG.gif')

    @commands.command()
    async def vundees(self, ctx: commands.Context):
        """Vundees Splooges"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730140604678204/Vundees.gif')

    @commands.command()
    async def drak(self, ctx: commands.Context):
        """He will never forgive you all for this"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730136628461589/Drak.gif')

    @commands.command()
    async def fishing(self, ctx: commands.Context):
        """Glub Glub"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/976527850524016650/Fishing.gif')

    @commands.command()
    async def dance(self, ctx: commands.Context):
        """Jaeger does his thing"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730135919628328/Dance.gif')

    @commands.command()
    async def logz(self, ctx: commands.Context):
        """Actual gif of him"""
        await ctx.send("LISTEN HERE SHITHEADS!")
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730138935349308/Logz.gif')

    @commands.command()
    async def f(self, ctx: commands.Context):
        """F"""
        await ctx.send('https://tenor.com/view/keyboard-hyperx-rgb-hyperx-family-hyperx-gaming-gif-17743649')

    @commands.command()
    async def jabs(self, ctx: commands.Context):
        """The Templars do be like that"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911837712196173824/jabs.gif')

    @commands.command()
    async def facepalm(self, ctx: commands.Context):
        """Arma every other second"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/912569604973404160/Facepalm.gif')

    @commands.command()
    async def hummus(self, ctx: commands.Context):
        """It's what Drak likes"""
        await ctx.send('https://tenor.com/view/hummus-hummusyes-hummushappy-gif-8630288')

    @commands.command()
    async def gabe(self, ctx: commands.Context):
        """Gabe did a thing"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/932432680178569276/Gabe.gif')

    @commands.command()
    async def maja(self, ctx: commands.Context):
        """How she be after we kick her butt"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/932433681992278088/Creed.gif')

    @commands.command()
    async def arty(self, ctx: commands.Context):
        """For Arty!"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/939988909352431666/For_Arty.gif')

    @commands.command()
    async def fly(self, ctx: commands.Context):
        """Pretty Fly for a Fly Guy"""
        await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/974769151774195733/Fly.gif')

    @commands.command()
    async def lost(self, ctx: commands.Context):
        """Then he was lost!"""
        await ctx.send('https://media.discordapp.net/attachments/911730032286785536/975825818506903562/Lost_died.gif')

    @commands.command()
    async def dungeons(self, ctx: commands.Context):
        """DUNGEONS"""
        await ctx.send('https://images-ext-1.discordapp.net/external/6E1zJYhVfv1WR1d4SNz1jPmLk0ZgOxTZ8GFrWO5M0G8/https/media.tenor.com/J1z4eDRIgl0AAAPo/dungeons.mp4')


def setup(bot: commands.Bot):
    bot.add_cog(Gif(bot))
