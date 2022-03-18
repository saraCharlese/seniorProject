from datetime import datetime
import time
from discord.ext import commands
from discord import DMChannel
import asyncio


class reminder(commands.Cog):

  def __init__(self,client):
    self.client = client

  async def guild_null(slef, ctx):
    if ctx.guild == None:
      await ctx.send("this command does not work in DM's")
      return True
    return False
    
  @commands.command(name='reminder')
  async def reminder(self, ctx):
    dm = await ctx.author.create_dm()
    if await self.guild_null(ctx):
      return
    

    def check(msg):
      return msg.author == ctx.author and msg.channel == dm
    

    await dm.send("When would you like your reminder(in minutes?) ")
    rt = await self.client.wait_for("message", check=check)
    reminder_time = rt.content    
    await dm.send("what would you like to be reminded of?")
    rc = await self.client.wait_for("message", check=check)
    reminder_content = rc.content
    await dm.send("you will be reminded to " + reminder_content + " in " + reminder_time + " minutes! ")
    convertedTime = (int(reminder_time) * 60)#might need to convert to float
    await asyncio.sleep(convertedTime)
    await dm.send("EZ-Bot was set to remind you to: ")
    await dm.send(reminder_content)
    if await self.guild_null(ctx):
      return


    

def setup(client):
  client.add_cog(reminder(client))