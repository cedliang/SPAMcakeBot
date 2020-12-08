import discord
from discord.ext import commands
import asyncio
from emoji import UNICODE_EMOJI

class Polling(commands.Cog):
    def __init__(self, client):
        self.client = client



    #Prompts a user to create a poll.
    #Prompts must be submitted by the .createpoll caller, times out in 120 seconds.
    @commands.command()
    async def createpoll(self, ctx, channel : discord.TextChannel):
        await ctx.send("Type your poll question, or type 'quit' anytime to cancel.")


        try:
            #PROMPT FOR QUESTION
            pollquestion = await self.client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 120.0)


            if pollquestion.content == 'quit':
                await ctx.send('Poll creation cancelled.')
                return

            question = pollquestion.content

            #prompt for poll description
            await ctx.send("Type your poll description, or type skip if the question is self explanatory.")
            polldescription = await self.client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 180.0)


            if polldescription.content == 'quit':
                await ctx.send('Poll creation cancelled.')
                return
            elif polldescription.content == 'skip':
                description = None
            else:
                description = polldescription.content


            #PROMPT FOR OPTIONS
            options = []
            takingOptions = True

            while takingOptions:
                await ctx.send("Type your poll answer.\nType the emote corresponding to the option first, then add a space, then type the answer. For example, \'👍 Yes\'.\nIf you are done with your options, type 'done'.")
                await ctx.send("Current options:")
                for option in options:
                    await ctx.send(f"\t{option[0]} {option[1]}")

                try:
                    option = await self.client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 120.0)

                    if option.content == 'done':
                        if len(options) > 0:
                            takingOptions = False
                        else:
                            await ctx.send("At least one option must be provided!")
                    elif option.content == 'quit':
                        await ctx.send('Poll creation cancelled.')
                        return
                    else:
                        optionEmote = option.content[0]
                        if (optionEmote not in UNICODE_EMOJI):
                            raise IndexError

                        optionText = option.content[2:]
                        options.append([optionEmote, optionText])

                except IndexError:
                    await ctx.send("Invalid option format. Option has not been added, please try again.")


            #options taken successfully
            await ctx.send("Next step.")

        #timeout
        except asyncio.TimeoutError:
            await ctx.send('Poll creation timed out.')
            return











    @createpoll.error
    async def createpoll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing an argument.')










def setup(client):
    client.add_cog(Polling(client))
