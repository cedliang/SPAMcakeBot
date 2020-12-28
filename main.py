import discord
from discord.ext import commands
import config
import os

intents = discord.Intents().all()
client = commands.Bot(command_prefix = '.', intents = intents)

@client.event
async def on_ready():
    print('Bot initialised.')

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