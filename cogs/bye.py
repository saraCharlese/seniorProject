from discord import Guild
from discord.ext import commands
from discord.commands import slash_command

class bye(commands.Cog):

  def __init__(self,client):
    self.client = client

  @commands.command()
  async def bye(self, ctx):
    await ctx.send("bye")

  @commands.command()
  async def hi(self, ctx): 
    await ctx.send("hi")

def setup(client):
  client.add_cog(bye(client))