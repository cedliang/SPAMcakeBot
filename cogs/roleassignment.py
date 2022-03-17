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
    async def createroleassignment(self, ctx, message_id):
        """Configure an existing message to assign roles when a reaction is added to it. Argument is the message_id."""
        try:
            takingOptions = True
            while takingOptions:
                await ctx.send("Load the role associations with the command \'emoji rolename\'.\nFor example:\n```👍 rolename\n👎 rolename```Don't tag the role. Type 'quit' to cancel.")
                emojiassocmessage = await self.client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 180.0)
                if emojiassocmessage.content == 'quit':
                    raise QuitException()
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
                    splitassoclist = [element.split(' ', 1) for element in assoclist]
                    appenddict = {element[0]: element[1] for element in splitassoclist}
                    takingOptions = False
            self.roleassocdict[message_id] = appenddict
            await ctx.send(str(self.roleassocdict))
            await ctx.send("Role associations have been created. Please manually add the reactions to the message so that others can react to it.")

        except asyncio.TimeoutError:
            await ctx.send('Post creation timed out.')
            return
        except QuitException:
            await ctx.send('Post creation cancelled.')
            return
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.updateRoles(payload, True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.updateRoles(payload, False)

    async def updateRoles(self, payload, addRoleBool : bool):
        reactMessageId = str(payload.message_id)
        try:
            #not found is handled by KeyError except
            associations = self.roleassocdict[reactMessageId]

            guildId = payload.guild_id
            guild = self.client.get_guild(guildId)
            try:
                role = discord.utils.get(guild.roles, name = associations[payload.emoji.name])
            except KeyError:
                print("KeyError raised in emoji to role search")
                return
            if role is not None:
                member = guild.get_member(payload.user_id)
                if member is None:
                    print("Member not found")
                elif addRoleBool:
                    await member.add_roles(role)
                    print(f"{member.name}#{member.discriminator} was assigned the role {role.name}")
                else:
                    await member.remove_roles(role)
                    print(f"{member.name}#{member.discriminator} was unassigned the role {role.name}")
            else:
                print("Role not found")
        except KeyError:
            return
        except Exception as e:
            print(e)
            return

    @commands.command()
    async def clearroleassignments(self, ctx):
        """Delete current role assignment posts."""
        self.roleassocdict = {}
        await ctx.send(f"Role associations have been cleared. {self.roleassocdict}")

    @commands.command()
    async def showroleassignments(self, ctx):
        """Show current role assignment posts."""
        await ctx.send(str(self.roleassocdict))

    @createroleassignment.error
    async def roleassignment_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing an argument. Format is ```.createroleassignmentpost {message_id}```')

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        """Removes a deleted message from the list of messages that are tracked by updateRoles"""
        try:
            del self.roleassocdict[str(message.id)]
            print('poll was removed from tracking')
        except KeyError:
            pass

def setup(client):
    client.add_cog(RoleAssignment(client))
