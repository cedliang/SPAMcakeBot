import discord
from discord.ext import commands
import config
import os

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('Bot is ready.')


#returns the client ping
@client.command()
async def ping(ctx):
    await ctx.send(f'{round(client.latency*1000)}ms')


####MODERATION

#purges the last x messages, 5 by default
@client.command()
async def purge(ctx, amount = 5):
    await ctx.channel.purge(limit = amount + 1)
    if amount == 1:
        pluralstring = 'message was'
    else:
        pluralstring = 'messages were'
    await ctx.send(f'{amount} {pluralstring} purged.')


#COGS SETUP
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(config.token)
