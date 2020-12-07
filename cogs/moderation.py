import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def purge(self, ctx, amount = 5):
        await ctx.channel.purge(limit = amount + 1)
        if amount == 1:
            pluralstring = 'message was'
        else:
            pluralstring = 'messages were'
        await ctx.send(f'{amount} {pluralstring} purged.')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'{round(self.client.latency*1000)}ms')

def setup(client):
    client.add_cog(Moderation(client))
