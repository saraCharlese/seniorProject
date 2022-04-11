from datetime import datetime
from http import client
import time
from discord.ext import commands
from discord import DMChannel
import asyncio
import random


class flipcoin(commands.Cog):

  def __init__(self,client):
    self.client = client

  async def guild_null(self, ctx):
    if ctx.guild == None:
      await ctx.send("this command does not work in DM's")
      return True
    return False
    
      

  @commands.command(name='flipcoin')
  async def flipcoin(self, ctx):
    dm = await ctx.author.create_dm()
    if await self.guild_null(ctx):
      return
    
    def check(msg):
      return msg.author == ctx.author and msg.channel == dm

    await dm.send("Heads or Tails?")
    ht = await self.client.wait_for("message", check=check)
    heads_or_tails = ht.content
    if heads_or_tails != "Heads" or "heads" or "Tails" or "tails":
      await dm.send("Please enter either: Heads or Tails")
      flipcoin(self, ctx)
      return

    num = random.randint(1,2)

    if num == 1:
        coin_result = "Heads"
    else:
        coin_result = "Tails"

    if heads_or_tails == coin_result:
        await dm.send(" Your guess is right! YOU WIN!")
    else:
        await dm.send(" Your guess is wrong! You LOSE! Wamp Wamp")
        return
    if await self.guild_null(ctx):
      return
    

    

def setup(client):
  client.add_cog(flipcoin(client))