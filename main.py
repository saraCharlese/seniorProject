""" Senior Project Discord Bot - Sara White"""

# Libraries Used
import discord
import json
import os
from discord.commands import slash_command

# Gets commands class from discord library
from discord.ext import commands

# Initializes client all commands start with ';'
# case_inseitive ensures case doesn't matter
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix=";", case_insensitive = True, intents=intents)

# Event: prints when bot goes online 
@client.event
async def on_ready():
  print("Login as {0.user} Sucessful!".format(client))

'''Commands To Load/Unload/Reload Cogs'''
# Command to load cogs to bot
@client.command()
async def load(ctx, filename): 
  client.load_extension(f"cogs.{filename}")
  await ctx.send(f"Loaded {filename}")

# Command to unload cogs from bot
@client.command()
async def unload(ctx, filename): 
  client.unload_extension(f"cogs.{filename}")
  await ctx.send(f"Unloaded {filename}")

# Command to reload cogs to bot
@client.command()
async def reload(ctx, filename): 
  client.unload_extension(f"cogs.{filename}")
  client.load_extension(f"cogs.{filename}")
  await ctx.send(f"Reloaded {filename}")

# Loads all files in the 'cogs' folder that has the .py extension
for cogfile in os.listdir("./cogs"):
  if cogfile.endswith(".py"):
    if cogfile.startswith("__init__"):
      pass
    else: 
      # Gets file name minus the last 3 characters ().py) and loads the cog
      client.load_extension(f"cogs.{cogfile[:-3]}")

# Gets token value from token.json file (Used for starting bot)
with open("token.json") as f: 
  data = json.load(f)
  token = data["TOKEN"]

client.run(token)