import discord
from discord.ext import commands
import asyncio
from emoji import UNICODE_EMOJI

class QuitException(Exception):
    """Exception to facilitate easy exit from client.wait_for in the event that 'quit' is typed"""
    pass

class RoleAssignment(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.roleassocdict = {}

    @commands.command()
    async def createroleassignmentpost(self, ctx, message_id):
        try:
            takingOptions = True
            while takingOptions:
                await ctx.send("Load the role associations with the command \'emoji rolename\'.\nFor example:\n```👍 rolename\n👎 rolename```Don't tag the role.")
                emojiassocmessage = await self.client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 180.0)
                assoclist = emojiassocmessage.content.split('\n')
                #check correctness of assoclist
                acceptable = True
                emojisDone = []
                for element in assoclist:
                    if (element[0] not in UNICODE_EMOJI) or len(element) < 2 or element[1] != ' ' or ord(element[0]) in emojisDone:
                        acceptable = False
                    else:
                        emojisDone.append(ord(element[0]))
                if not acceptable:
                    await ctx.send("Format not correct. Try again.")
                else:
                    splitassoclist = []
                    for element in assoclist:
                        splitassoclist.append(element.split(' ', 1))
                    takingOptions = False
            self.roleassocdict[message_id] = splitassoclist
            await ctx.send(self.roleassocdict)

        except asyncio.TimeoutError:
            await ctx.send('Post creation timed out.')
            return
        except QuitException:
            await ctx.send('Post creation cancelled.')
            return

    @createroleassignmentpost.error
    async def roleassignment_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing an argument. Format is ```.createroleassignmentpost {message_id}```')

# TODO: implement on message delete event to remove message id from roleassoclist to end tracking

def setup(client):
    client.add_cog(RoleAssignment(client))
