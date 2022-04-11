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

  def __init__(self,client):
    self.client = client

  async def guild_null(self, ctx):
    if ctx.guild == None:
      await ctx.send("this command does not work in DM's")
      return True
    return False

  @commands.command(name='pomodoro')
  async def pomodoro(self, ctx):
    dm = await ctx.author.create_dm()
    if await self.guild_null(ctx):
      return
    
    def check(msg):
      return msg.author == ctx.author and msg.channel == dm

    await ctx.send("Now entering Pomodoro timer, Please select a task to focus on for 25 minutes!")

    converted_25 = (int(1) * 60)
    converted_5 = (int(1) * 60)
    i = 0
    while i < 16:
      await asyncio.sleep(converted_25)
      await dm.send("please take a 5 minute break")
      await asyncio.sleep(converted_5)
      await dm.send("Your 5 minute pomodoro break is over, please choose another task to focus on for 25 minutes")
      i = i + 1

  @commands.command(name = 'quitpomodoro')
  async def quitpomodoro(self, ctx):
    dm = await ctx.author.create_dm()
    if await self.guild_null(ctx):
      return
    
    def check(msg):
      return msg.author == ctx.author and msg.channel == dm
    qrembed = discord.Embed(description="Would you like to end your pomodoro session?", color=0x000FF)

    await ctx.send(embed=qrembed, components=[
      Button(label="Yes", style="3", custom_id="yes"),
      Button(label="No", style="4", custom_id="no")])
    try:
      qr = await self.client.wait_for("button_click", timeout=300, check=lambda i: i.custom_id == "yes" or "no")
      if qr.content == "yes":
        qrembed = discord.Embed(description="You have now exited the Pomodoro Timer!", color=0x000FF)
        await ctx.send(embed=qrembed)
        quit()
      elif qr.component.custom_id == "no":
        qrembed = discord.Embed(description="You are still using the Pomodoro timer!", color=0x000FF)
        await ctx.send(embed=qrembed)
      else:
        return
    except asyncio.TimeoutError:
      await self.clear_last_msg(dm)
      return

    if await self.guild_null(ctx):
      return
    

    

def setup(client):
  client.add_cog(pomodoro(client))