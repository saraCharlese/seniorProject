from datetime import datetime
from http import client
import time
from discord.ext import commands
from discord import DMChannel
import asyncio
import random
import discord


class magic8ball(commands.Cog):

  def __init__(self,client):
    self.client = client

  async def guild_null(self, ctx):
    if ctx.guild == None:
      await ctx.send("this command does not work in DM's")
      return True
    return False
    
      

  @commands.command(name='magic8ball')
  async def magic8ball(self, ctx):
    if await self.guild_null(ctx):
      return
    
    def check(msg):
      return msg.author == ctx.author and msg.channel
    qrembed0 = discord.Embed(title="Ask the almighty 8 ball a question to recieve your fortune", color=0x000FF)

    await ctx.send(embed=qrembed0)
    eight_ball = await self.client.wait_for("message", check=check)

    Eightball_answers = [
        "It is certain",
        "Outlook good",
        "You may rely on it",
        "Ask again later",
        "Concentrate and ask again",
        "Reply hazy, try again",
        "My reply is no",
        "My sources say no",
        "not a chance",
        "How dare you percieve me",
        "Ask someone else",
        "look within for answers",
        "nope",
        "no",
        "Totes",
        "perhaps",
        "every dog has its day..."
        ]
    eight_ball_reply = random.choice(Eightball_answers)
    qrembed = discord.Embed(title="The magic 8-Ball in all its glory, says:", color=0x000FF)
    await ctx.send(embed=qrembed)
    await ctx.send(file=discord.File(''))
    qrembed1 = discord.Embed(title= eight_ball_reply, color=0x000FF)
    await ctx.send(embed=qrembed1)


    if await self.guild_null(ctx):
      return
    

    

def setup(client):
  client.add_cog(magic8ball(client))