from datetime import datetime
from http import client
from msilib.schema import Component
import time
from discord.ext import commands
from discord import DMChannel
import discord
import asyncio
from discord_components import DiscordComponents, Button, SelectOption, Select


class pomodoro(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def guild_null(self, ctx):
        if ctx.guild == None:
            await ctx.send("this command does not work in DM's")
            return True
        return False

    @commands.command(name="pomodoro")
    async def pomodoro(self, ctx):
        if await self.guild_null(ctx):
            return
        qrembed4 = discord.Embed(
            description="Now entering Pomodoro timer, Please select a task to focus on for 25 minutes!",
            color=0x000FF,
        )

        await ctx.send(embed=qrembed4)

        converted_25 = int(25) * 60
        converted_5 = int(5) * 60

        i = 0

        def check(msg):
            return msg.author == ctx.author and msg.channel

        while i < 16:

            qrembed = discord.Embed(
                description="You have now exited the Pomodoro Timer!", color=0x000FF
            )
            qrembed5 = discord.Embed(
                description="You are still using the Pomodoro Timer!", color=0x000FF
            )
            qrembed6 = discord.Embed(
                description="you must enter: ' YES '... otherwise you are still using the Pomodoro timer!",
                color=0x000FF,
            )
            await asyncio.sleep(converted_25)
            qrembed2 = discord.Embed(
                description="please take a 5 minute break, or would you like to end Pomodoro Session? (YES/NO)",
                color=0x000FF,
            )
            await ctx.send(embed=qrembed2)
            qr = await self.client.wait_for("message", check=check)
            if str(qr.content) == "yes":
                await ctx.send(embed=qrembed)
                i = 16
                break
            elif str(qr.content) == "Yes":
                await ctx.send(embed=qrembed)
                i = 16
                break
            elif str(qr.content) == "YES":
                await ctx.send(embed=qrembed)
                i = 16
                break
            elif qr.content == "NO":
                await ctx.send(embed=qrembed5)
            elif qr.content == "no":
                await ctx.send(embed=qrembed5)
            elif qr.content == "No":
                await ctx.send(embed=qrembed5)
            else:
                await ctx.send(embed=qrembed6)

            await asyncio.sleep(converted_5)
            qrembed3 = discord.Embed(
                description="Your 5 minute pomodoro break is over, please choose another task to focus on for 25 minutes, or would you like to end your pomodoro session?(YES/NO)",
                color=0x000FF,
            )
            await ctx.send(embed=qrembed3)
            qr = await self.client.wait_for("message", check=check)
            if str(qr.content) == "yes":
                await ctx.send(embed=qrembed)
                i = 16
                break
            elif str(qr.content) == "Yes":
                await ctx.send(embed=qrembed)
                i = 16
                break
            elif str(qr.content) == "YES":
                await ctx.send(embed=qrembed)
                i = 16
                break
            elif qr.content == "NO":
                await ctx.send(embed=qrembed5)
            elif qr.content == "no":
                await ctx.send(embed=qrembed5)
            elif qr.content == "No":
                await ctx.send(embed=qrembed5)
            else:
                await ctx.send(embed=qrembed6)
            i = i + 1

        if await self.guild_null(ctx):
            return


def setup(client):
    client.add_cog(pomodoro(client))