""" Senior Project Discord Bot - Sara White"""

import discord
import json
import os
# gets commands class from discord library
from discord.ext import commands

# initializes client all commands start with !
# case_inseitive ensures case doesn't matter
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix=";", case_insensitive=True, intents=intents)

# Removes built in help command
client.remove_command('help')


@client.event
# event: prints when bot goes online
async def on_ready():
    print("Login as {0.user} Sucessful!".format(client))

# gets token value from .json file to start bot
with open("token.json") as f:
    data = json.load(f)
    token = data["TOKEN"]

# cogs (custom command files)


@client.command()
# command to load cogs to bot
async def load(ctx, filename):
    client.load_extension(f"cogs.{filename}")
    await ctx.send(f"Loaded {filename}")


@client.command()
# command to unload cogs to bot
async def unload(ctx, filename):
    client.unload_extension(f"cogs.{filename}")
    await ctx.send(f"Unloaded {filename}")


@client.command()
# command to reload cogs to bot
async def reload(ctx, filename):
    client.unload_extension(f"cogs.{filename}")
    client.load_extension(f"cogs.{filename}")
    await ctx.send(f"Reloaded {filename}")

# looks for cogs file in directory
for cogfile in os.listdir("./cogs"):
    if cogfile.endswith(".py"):
        if cogfile.startswith("__init__"):
            pass
        else:
            # gets file name minus the last 3 characters ().py) and loads the cog
            client.load_extension(f"cogs.{cogfile[:-3]}")


client.run(token)