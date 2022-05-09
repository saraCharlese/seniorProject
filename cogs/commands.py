# Necessary imports
import discord
import random
import asyncio
from discord import embeds
from discord.ext import commands

# Start of commandslist class
class commands(commands.Cog):

  def __init__(self,client):
    self.client = client

  # Command that will show the user the active commands and provide a description of what they do
  @commands.command()
  async def commands(self, ctx):
    # Help Pages
    page1 = discord.Embed(title="**__Commands List__**", description="Use the buttons below to navigate between pages. \n Work Commands", color=0x000FF)
    page1.set_author(name = "EZ Bot")
    page1.set_thumbnail(url="https://i.postimg.cc/G2W5RsLD/ezbot.png")
    page1.add_field(name = "**!register**", value= "Register into the database so you can track your hours! Run this command in server and the bot will DM you for your information.", inline=False)
    page1.add_field(name = "**!in**", value= "Clock in to work.", inline=False)
    page1.add_field(name = "**!out**", value= "Clock out of work.", inline=False)
    page1.add_field(name = "**!fix**", value= "Run this command if you need to fix a shifts time. Run this command in server and the bot will DM you asking which shift needs to be fixed, then it will send the manager on duty a request to either approve or deny.", inline=False)    
    page1.add_field(name = "**!afk (optional message)**", value= "Tell your colleagues that you will be away for a while. Insert an optional message if you want! Typing in any channel will remove you from AFK mode.", inline=False)
    
    page2 = discord.Embed(title="**__Comands List__**", description="Page 2", color=0x000FF)
    page2.add_field(name = "**!reminder**", value= "Set a reminder for yourself, run the command in server and the bot will DM you to ask what you want to be reminded of and ask for a time (in minutes).", inline=False)
    page2.add_field(name = "**!pomodoro**", value= "A focus timer! Set this up to focus on tasks that need to be completed. Timer is set at 25 minute intervals and 5 minute breaks.", inline=False)
    page2.add_field(name = "**!quitpomodoro**", value= "Run this command to stop the focus timer.", inline=False)
    page2.add_field(name = "**!weather**", value= "Check the weather for a specific area (opens a browser after entering a city).", inline=False)
    
    page3 = discord.Embed(title= "**__Fun Commands__**", description = "List of games added to the bot", color=0x000FF)
    page3.add_field(name = "**!coinflip**", value= "Flip a coin and choose heads or tails. Will you guess correctly?", inline=False)
    page3.add_field(name = "**!magic8ball**", value= "Ask the magic 8 ball a yes or no question.", inline=False)
    page3.add_field(name = "**!weekend**", value= "Show your excitement for the weekend!", inline=False)

    # Sends the pages embed to discord and adds the react buttons
    self.client.help_pages = [page1, page2, page3]
    buttons = [u"\u2B05", u"\u27A1"] # skip to start, left, right, skip to end
    current = 0
    msg = await ctx.send(embed=self.client.help_pages[current])
    
    # Loop that allows for navigating back and forth through pages with a command time out of 60 seconds.
    for button in buttons:
        await msg.add_reaction(button)
            
    while True:
        try:
            reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

        except asyncio.TimeoutError:
            return 

        else:
            previous_page = current
                    
            if reaction.emoji == u"\u2B05":
                if current > 0:
                    current -= 1
                        
            elif reaction.emoji == u"\u27A1":
                if current < len(self.client.help_pages)-1:
                    current += 1
            # Loop that allows to press the left and right arrows more than once depending on navigation direction. 
            for button in buttons:
                await msg.remove_reaction(button, ctx.author)

            if current != previous_page:
                await msg.edit(embed=self.client.help_pages[current])
    


def setup(client):
  client.add_cog(commands(client))