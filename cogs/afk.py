# Necessary imports
import discord
from discord.ext import commands
from discord.message import Message
import traceback
import datetime
import random
import asyncio
import json

intents = discord.Intents.default()
intents.members = True

# Start of afk command class
class afkCog(commands.Cog):

  def __init__(self,client):
    self.client = client

  # Start of afk command
  @commands.command()
  async def afk(self, ctx, message = None):
    current_nick = ctx.author.nick

    # Saves users default name as their nick if they do not already have one
    if current_nick == None:
      current_nick = ctx.author.name

    # Checks if user was previously AFK and is trying to run the command again
    # If they were, it takes out the [AFK] and exits the command
    if "[AFK]" in current_nick:
      await ctx.send(f"{ctx.author.mention} is no longer AFK")
      newNick = ctx.author.nick.replace('[AFK]', '')
      await ctx.author.edit(nick=newNick)
      return

    # Checks if user entered a message after running (prefix)afk
    if message == None:
      message = None
      await ctx.send(f"{ctx.author.mention} has gone afk.")
    else:
      # Prints more than the first word of the message a user enters if contains more than one word
      message = ctx.message.content.split(' ', 1)[1]
      await ctx.send(f"{ctx.author.mention} has gone afk {message}.")

    try:
      await ctx.author.edit(nick = f"{ctx.author.name} [AFK]")
    except:
      await ctx.send("Unable to change your name")

  # Reads all messages from all users
  @commands.Cog.listener()
  async def on_message(self,message):
    # Gets users nickname
    userName = message.author.nick

    if userName != None:
      # Checks if user has [AFK] in their name
      if "[AFK]" in userName:
        # Checks if user was trying to run the afk command again
        if ";afk" in message.content:
          pass
        else:
          # Takes out the [AFK] from the users name
          newNick = message.author.nick.replace('[AFK]', '')
          await message.author.edit(nick=newNick)

          await message.channel.send(f"{message.author.mention} is no longer AFK")

# Function which adds users ID and message to json file
def afkOn(userID,message):
    # If there is no message store an empty message
    if message == None:
        message = ""

    # Creates dictionary that stores usersID and message
    entry = {userID:message}

    # Opens afk.json file
    with open("afk.json", mode='r+') as file:
        # Returns current file data as a dict
        afkList = json.load(file)

        # Updates dict with new entry
        afkList.update(entry)

        # Writes to file
        file.seek(0)
        json.dump(afkList, file)

# Function that returns users message if user is in AFK list else returns False
def getAfk(userID):
    with open("afk.json", mode='r+') as file:
        # Returns current file data as a dict
        afkList = json.load(file)

        if userID in afkList:
            return afkList[userID]
        else: 
            print(False)
            return False

# Function that takes off the user from the AFK list
def removeAfk(userID):
    with open("afk.json", mode='r+') as file:
        # Returns current file data as a dict
        afkList = json.load(file)

        # Removes current user from dictionary
        del afkList[userID]
        
    with open("afk.json", mode='w') as file:
        # Writes dictionary back to file
        file.seek(0)
        json.dump(afkList, file)

    




def setup(client):
  client.add_cog(afkCog(client))