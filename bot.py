import discord
import bat, pit, player, wumpus
import random
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='w!')


@client.event
async def on_ready():
    print(f'{client.user} connected.')


@client.command
async def rules(ctx):
    await ctx.send()