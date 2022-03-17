import discord
from discord.ext import commands
import asyncio
from emoji import UNICODE_EMOJI
from datetime import datetime, timedelta


class QuitException(Exception):
    """Exception to facilitate easy exit from client.wait_for in the event that 'quit' is typed"""
    pass


class Polling(commands.Cog):

    def __init__(self, client):
        self.client = client
        #holds the message IDs of all active polls
        self.activePollMessageIDs = set()

    #Prompts a user to create a poll.
    #Prompts must be submitted by the .createpoll caller, times out in 120 seconds.
    @commands.command()
    async def createpoll(self, ctx, channel : discord.TextChannel):
        """Creates a poll and adds it to self.activePollMessageIDs to be monitored by the reaction watcher function, waits for the specified timeout, then removes the poll from self.activePollMessageIDs"""
        try:
            await ctx.send("Type your poll question, or type 'quit' anytime to cancel.")
            #prompt for question
            pollquestion = await self.client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 120.0)
            if pollquestion.content == 'quit':
                raise QuitException()
            question = pollquestion.content

            #prompt for poll description
            await ctx.send("Type your poll description, or type skip if the question is self explanatory.")
            polldescription = await self.client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 180.0)
            if polldescription.content == 'quit':
                raise QuitException()
            elif polldescription.content == 'skip':
                description = None
            else:
                description = polldescription.content

            #PROMPT FOR OPTIONS
            options = []
            takingOptions = True
            emojisDone = []
            while takingOptions:
                echoOptionsString = ''.join(f"{option[0]} {option[1]}\n" for option in options)
                await ctx.send(f"Type your poll answer.\nType the emote corresponding to the option first, then add a space, then type the answer. For example, \'👍 Yes\'.\nIf you are done with your options, type 'done'.\nCurrent options:\n{echoOptionsString}")
                try:
                    option = await self.client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 120.0)
                    if option.content == 'done':
                        if options:
                            takingOptions = False
                        else:
                            await ctx.send("At least one option must be provided!")
                    elif option.content == 'quit':
                        raise QuitException()
                    else:
                        optionEmote = option.content[0]
                        if (optionEmote not in UNICODE_EMOJI):
                            raise IndexError
                        elif ord(optionEmote) in emojisDone:
                            await ctx.channel.purge(limit = 2)
                            await ctx.send('This emoji has already been used! Use a unique emoji.')
                        else:
                            optionText = option.content[2:]
                            options.append([optionEmote, optionText])
                            emojisDone.append(ord(optionEmote))
                            await ctx.channel.purge(limit = 2)
                except IndexError:
                    await ctx.channel.purge(limit = 2)
                    await ctx.send("Invalid option format. Option has not been added, please try again.")

            #options taken successfully
            await ctx.send("Enter the duration for the poll to be open in a whole number of seconds. Valid values from 1 to 2592000 (30 days)")
            takingTime = True
            while takingTime:
                try:
                    timereply = await self.client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 120.0)
                    if timereply.content == 'quit':
                        raise QuitException()
                    duration = int(timereply.content)
                    if duration < 1 or duration > 2592000:
                        await ctx.send("Invalid time entered. Please try again.")
                    else:
                        takingTime = False
                except ValueError:
                    await ctx.send("Invalid time entered. Please try again.")

            optionsString = ''.join(
                f'{optionTuple[0]} {optionTuple[1]}\n' for optionTuple in options
            )

            pollEmbed = discord.Embed(title = f'Poll: {question}', description = description, color = discord.Colour.from_rgb(254, 254, 254))
            pollEmbed.add_field(name = 'Options (react to vote)', value = optionsString, inline = True)
            #blank fields to force new line
            pollEmbed.add_field(name = chr(173), value = chr(173), inline = True)
            pollEmbed.add_field(name = chr(173), value = chr(173), inline = True)
            endtime = datetime.now() + timedelta(seconds = duration)
            endtimestring = endtime.strftime("%m/%d/%Y, %H:%M:%S")
            pollEmbed.set_footer(text = f"Poll closes at {endtimestring}\nPoll created by {ctx.author.name}#{ctx.author.discriminator}", icon_url = ctx.author.avatar_url)

            resultsstring = ''.join(
                f'{option[0]} ░░░░░░░░░░ 0% (0)\n' for option in options
            )

            pollEmbed.add_field(name = 'Results', value = resultsstring, inline = True)

            await channel.send(embed = pollEmbed)

            #pollmessage contains the discord.Message which contains the embed
            async for message in channel.history(limit = 1):
                pollMessage = message
            for option in options:
                await pollMessage.add_reaction(option[0])
            await ctx.send("Poll has been created.")
            self.activePollMessageIDs.add(pollMessage.id)

            #TIMES OUT FOR TIMEOUT TIME
            await asyncio.sleep(duration)

            closeMessage = await channel.fetch_message(pollMessage.id)
            closeEmbed = closeMessage.embeds[0]
            closeEmbed.title = f'[Closed] {closeEmbed.title}'
            #change 'closes' in the footer to 'closed'
            currentFooterText = closeEmbed.footer.text
            authoriconurl = closeEmbed.footer.icon_url
            newFooterText = f'{currentFooterText[:10]}d{currentFooterText[11:]}'
            closeEmbed.set_footer(text = newFooterText, icon_url = authoriconurl)
            await message.edit(embed = closeEmbed)
            self.activePollMessageIDs.remove(pollMessage.id)

        except asyncio.TimeoutError:
            await ctx.send('Poll creation timed out.')
            return
        except QuitException:
            await ctx.send('Poll creation cancelled.')
            return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        """Event to call updatePollResults upon reaction removal, which will update the results section of the poll embed"""
        await self.updatePollResults(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        """Event to call updatePollResults upon reaction addition, which will update the results section of the poll embed"""
        await self.updatePollResults(payload)

    async def updatePollResults(self, payload):
        """Performs a count of the reactions of the message in which the poll is contained, and updates the Results field of the corresponding embed."""
        if payload.message_id not in self.activePollMessageIDs:
            return
        channel = await self.client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        pollembed = message.embeds[0]

        #makes shallow copy of reaction list and ensure entries are sorted in descending order
        reactionslist = sorted(message.reactions[:], key = lambda reaction: reaction.count, reverse = True)
        totalreactions = 0
        #remove the bot's count to get the 'true' polling numbers
        for reaction in reactionslist:
            reaction.count -= 1
            totalreactions += reaction.count
        #removes existing embed
        pollembed.remove_field(-1)

        #add new embed
        resultsstring = ''
        for reaction in reactionslist:
            if totalreactions > 0:
                reactPercentage = 100*(reaction.count / totalreactions)
            else:
                reactPercentage = 0
            nearestPercentage = round(reactPercentage)
            fullBlocks = nearestPercentage // 10
            rem = nearestPercentage - 10*fullBlocks
            partialBlocks = 1 if rem >= 5 else 0
            totalBlocks = partialBlocks + fullBlocks
            blocksString = '█' * fullBlocks + partialBlocks*'▓' + (10-totalBlocks)*'░'
            resultsstring += f'{reaction.emoji} {blocksString} {round(reactPercentage,1)}% ({reaction.count})\n'
        pollembed.add_field(name = 'Results', value = resultsstring, inline = True)

        await message.edit(embed = pollembed)

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        """Removes a deleted message from the list of messages that are tracked by updatePollResults"""
        try:
            self.activePollMessageIDs.remove(message.id)
            print('poll was removed from tracking')
        except ValueError:
            pass

    @createpoll.error
    async def createpoll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing an argument.')

    #for debugging purposes
    @commands.command()
    async def checkactivepolls(self, ctx):
        """Prints current active polls in terminal."""
        print(self.activePollMessageIDs)

def setup(client):
    client.add_cog(Polling(client))
