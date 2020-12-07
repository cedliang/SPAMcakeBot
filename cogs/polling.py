import discord
from discord.ext import commands

class Polling(commands.Cog):
    def __init__(self, client):
        self.client = client
