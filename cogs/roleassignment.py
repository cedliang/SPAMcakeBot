import discord
from discord.ext import commands


class RoleAssignment(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def createroleassignmentpost(self, ctx):
        ctx.send('hi')


def setup(client):
    client.add_cog(RoleAssignment(client))
