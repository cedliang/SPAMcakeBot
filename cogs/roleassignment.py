import discord
from discord.ext import commands
import asyncio

class QuitException(Exception):
    """Exception to facilitate easy exit from client.wait_for in the event that 'quit' is typed"""
    pass

class RoleAssignment(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def createroleassignmentpost(self, ctx):
        try:
            await ctx.send("Type the text to appear in the body of your message, or type quit to cancel.")
            bodytextmessage = await self.client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 120.0)
            if bodytextmessage.content == 'quit':
                raise QuitException()
            bodytext = bodytextmessage.content




        except asyncio.TimeoutError:
            await ctx.send('Post creation timed out.')
            return
        except QuitException:
            await ctx.send('Post creation cancelled.')
            return


def setup(client):
    client.add_cog(RoleAssignment(client))
