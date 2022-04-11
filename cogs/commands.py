# Necessary imports
import discord
from discord import Guild
from discord.ext import commands

# Start of commandslist class
class commandslist(commands.Cog):

  def __init__(self,client):
    self.client = client

  # Command that will show the user the active commands and provide a description of what they do
  @commands.command()
  async def commands(self, ctx):
    List = ["**__Work Commands: Commands to simplify work!__**",
            "**!register:** Register yourself in the database so you can track your hours! Run this command in server and the bot will DM you for your information.",
            "**!clockin:** Clock in to work so you can be paid!",
            "**!clockout:** Don't forget to clock out for the day!",
            "**!fix:** If you forget to clock out don't worry run this command in server and the bot will DM you asking which shift needs to be fixed, then send the manager on duty a request to either approve or deny.",
            "**!afk (optional message):** Tell your colleagues that you will be away from your keyboard and insert an optional message if you want! Just type in any channel and the afk will be removed.",
            "**!reminder:** Set a reminder for yourself, run the command in sever and the bot will DM you to ask what you want to be reminded of and ask for a time.",
            "**!pomodoro:** A focus timer! Run this command in server and the bot will DM you to set up a focus task.",
            "**!weather:** Check the weather for a specific area.",
            "**__Game Commands: Have some fun!__**",
            "**!flipcoin:** Flip a coin and choose heads or tails"]
    Desc = '\n\n'.join(List)
    commandsEmbed = discord.Embed(title = "List of Commands", description = Desc ,color = 0x000FF)
    await ctx.send(embed=commandsEmbed)


def setup(client):
  client.add_cog(commandslist(client))