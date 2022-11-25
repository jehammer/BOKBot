import asyncio

import discord
from discord.ext import commands

import logging
from discord import FFmpegPCMAudio
from discord.utils import get

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


class Voice(commands.Cog, name="Voice"):
    """For Fun Voice Things"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # TODO: Convert these to check if the author is in voice, and if not then have it default to general voice

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
            logging.error("Nut error: " + str(e))

    @commands.command()
    async def cat(self, ctx: commands.Context):
        """Pop tart Cats"""
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
            logging.error("Pop tart Error: " + str(e))

    @commands.command()
    async def bob(self, ctx: commands.Context):
        """There is a certain thing to say"""
        try:
            # If user is in a voice channel, connect to channel, play audio, then leave
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice = await channel.connect()
                source = FFmpegPCMAudio('Audio/Bob.wav')
                voice.play(source)
                while voice.is_playing():
                    await asyncio.sleep(2)
                await ctx.guild.voice_client.disconnect()
            else:
                await ctx.send("You are not in a voice channel, you must be to use voice commands.")
        except Exception as e:
            logging.error("Bob Error: " + str(e))

    @commands.command()
    async def respect(self, ctx: commands.Context):
        """You will respect it!"""
        try:
            # If user is in a voice channel, connect to channel, play audio, then leave
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice = await channel.connect()
                source = FFmpegPCMAudio('Audio/Respect.wav')
                voice.play(source)
                while voice.is_playing():
                    await asyncio.sleep(2)
                await ctx.guild.voice_client.disconnect()
            else:
                await ctx.send("You are not in a voice channel, you must be to use voice commands.")
        except Exception as e:
            logging.error("Respect Error: " + str(e))

    @commands.command()
    async def laundry(self, ctx: commands.Context):
        """You should do it"""
        try:
            # If user is in a voice channel, connect to channel, play audio, then leave
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice = await channel.connect()
                source = FFmpegPCMAudio('Audio/Laundry.mp3')
                voice.play(source)
                while voice.is_playing():
                    await asyncio.sleep(2)
                await ctx.guild.voice_client.disconnect()
            else:
                await ctx.send("You are not in a voice channel, you must be to use voice commands.")
        except Exception as e:
            logging.error("Laundry Error: " + str(e))

    @commands.command()
    async def dc(self, ctx: commands.Context):
        """Force the bot to disconnect from a chat if it is in one"""
        try:
            if ctx.author.voice:
                await ctx.guild.voice_client.disconnect()
            else:
                await ctx.send("You are not in a voice channel, you must be to use voice commands.")
        except Exception as e:
            logging.error("DC error: " + str(e))


async def setup(bot: commands.Bot):
    await bot.add_cog(Voice(bot))
