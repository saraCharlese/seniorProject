import discord
import random
from discord.ext import commands

class weekendgifs(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Command that will display a random gif when !weekend is called
    #@commands.cooldown(1, 15, commands.BucketType.member)
    @commands.command()
    async def weekend(self, ctx):
        weekendgif= [
            "https://tenor.com/view/weekend-friday-feeling-tgif-snoopy-friday-gif-16247074",
            "https://tenor.com/view/weekend-reaction-dog-smile-gif-19360238",
            "https://tenor.com/view/homer-simpsons-weekend-feels-mood-gif-11583609",
            "https://tenor.com/view/happy-weekend-puppy-cute-weekend-pet-gif-8481566",
            "https://tenor.com/view/the-simpsons-lisa-simpson-dance-dancing-happy-gif-4912459",
            "https://tenor.com/view/im-ready-im-excited-to-see-you-cat-sunglasses-cool-gif-14502281"
            ]
        ranweekend = random.choice(weekendgif)
        await ctx.send(ranweekend)

def setup(client):
    client.add_cog(weekendgifs(client))