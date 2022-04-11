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
class afk(commands.Cog):

  def __init__(self,client):
    self.client = client

  # Start of afk command
  @commands.command()
  async def afk(self, ctx, message = None):
    try:
        # Variable will be true if user was afk previously, false if they weren't
        afkCheck = getAfk(ctx.author.id)
        
        # If user wasnt afk
        if not afkCheck:
            # Checks if user entered a message after running (prefix)afk
            if message == None:
                message = None
                #await ctx.send(f"{ctx.author.mention} has gone afk.")
                afkEmbed = discord.Embed(description=f"{ctx.author.mention} has gone afk. ",color=0x000FF)
                await ctx.send(embed=afkEmbed)
            else:
                # Prints more than the first word of the message a user enters if contains more than one word
                message = ctx.message.content.split(' ', 1)[1]
                #await ctx.send(f"{ctx.author.mention} has gone afk `{message}`.")
                afkEmbed2 = discord.Embed(description=f"{ctx.author.mention} has gone afk `{message}`.",color=0x000FF)
                await ctx.send(embed=afkEmbed2)
                
            # Adds [AFK] to users name
            current_nick = ctx.author.nick

            if current_nick == None:
                current_nick = ctx.author.nick

            try:
                await ctx.author.edit(nick = f"[AFK] {ctx.author.name}")
            except:
                #await ctx.send("Unable to change your name")
                print("Unable to change user name")

            # Adds user to afk list
            afkOn(ctx.author.id,message)
        else:
            removeAfk(ctx.author.id)
            newNick = ctx.author.nick.replace('[AFK]', '')
            await ctx.author.edit(nick=newNick)
            #await ctx.send("you are not afk anymore")
            afkEmbed3 = discord.Embed(title="You are no longer AFK",color=0x000FF)
            await ctx.send(embed=afkEmbed3)
            

    except Exception:
        await ctx.send(f"```{traceback.format_exc()}```")

  # Reads all messages from all users
  @commands.Cog.listener()
  async def on_message(self,message):
    # Ignores bots own messages
    if message.author.id == self.client.user.id:
        return

    '''First Check if the author of the message was previously AFK
       If they were, take them off the afk list'''
    
    afkCheck = getAfk(message.author.id)

    if afkCheck:
        removeAfk(message.author.id)
        #await message.reply("You are not AFK anymore")
        afkEmbed4 = discord.Embed(title="You are no longer AFK",color=0x000FF)
        await message.reply(embed=afkEmbed4)
        newNick = message.author.nick.replace('[AFK]', '')
        await message.author.edit(nick=newNick)
    
    '''Then check if the message contains a reply or ping mention'''
    mention = message.mentions

    if mention:
        # Loops through all users in the message 
        for user in mention:
            userID = user.id

            # Checks if user that was pinged was AFK
            afkCheck = getAfk(userID)

            if afkCheck:
                afkMessage = getMessage(userID)

                # If the user didnt leave any message
                if len(afkMessage) == 0:
                    #await message.reply(f"<@{userID}> is AFK")
                    afkEmbed5 = discord.Embed(description=f"<@{userID}> is AFK",color=0x000FF)
                    await message.reply(embed=afkEmbed5)
                else:
                    #await message.reply(f"<@{userID}> is AFK: {afkMessage}")
                    afkEmbed6 = discord.Embed(description=f"<@{userID}> is AFK: {afkMessage}",color=0x000FF)
                    await message.reply(embed=afkEmbed6)



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
    # Converts userID from int to string
    userID = str(userID)
    
    with open("afk.json", mode='r+') as file:
        # Returns current file data as a dict
        afkList = json.load(file)
        
        if userID in afkList:
            return True
        else: 
            return False

# Function that takes off the user from the AFK list      
def removeAfk(userID):
    # Converts userID from int to string
    userID = str(userID)
    
    with open("afk.json", mode='r+') as file:
        # Returns current file data as a dict
        afkList = json.load(file)

        # Removes current user from dictionary
        del afkList[userID]
        
    with open("afk.json", mode='w') as file:
        # Writes dictionary back to file
        file.seek(0)
        json.dump(afkList, file)
        
def getMessage(userID):
    userID = str(userID)
    
    with open("afk.json", mode='r+') as file:
        # Returns current file data as a dict
        afkList = json.load(file)
        
        message = afkList[userID]
        
        return message


def setup(client):
  client.add_cog(afk(client))