import asyncio

import nextcord
from nextcord.ext import commands

import logging
from nextcord import FFmpegPCMAudio
from nextcord.utils import get

logging.basicConfig(level=logging.INFO)


class Voice(commands.Cog, name="Voice"):
    """For Fun Voice Things"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logging.info("Voice cog loaded")

    @commands.command()
    async def nut(self, ctx: commands.Context):
        """Nut hard"""
        try:
            # If user is in a voice channel, connect to channel, play audio, then leave
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice = await channel.connect()
                source = FFmpegPCMAudio('Audio/nut.wav')
                voice.play(source)
                while voice.is_playing():
                    await asyncio.sleep(2)
                await ctx.guild.voice_client.disconnect()
            else:
                await ctx.send("You are not in a voice channel, you must be to use voice commands.")
        except Exception as e:
            print(e)

    @commands.command()
    async def cat(self, ctx: commands.Context):
        """Poptart Cats"""
        try:
            # If user is in a voice channel, connect to channel, play audio, then leave
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice = await channel.connect()
                source = FFmpegPCMAudio('Audio/Nyan Cat.wav')
                voice.play(source)
                while voice.is_playing():
                    await asyncio.sleep(2)
                await ctx.guild.voice_client.disconnect()
            else:
                await ctx.send("You are not in a voice channel, you must be to use voice commands.")
        except Exception as e:
            print(e)


def setup(bot: commands.Bot):
    bot.add_cog(Voice(bot))
