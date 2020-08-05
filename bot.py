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


@client.command()
async def rules(ctx):
    print('LOG: ' + str(ctx.author) + ' requested "Ruleset"')
    help_embed = discord.Embed(
        title='How To Play',
        description='w!ogrules will provide you with the (mostly) Original ruleset from the TI game.',
        colour=discord.Colour.from_rgb(0, 255, 208)
    )

    help_embed.set_footer(text='Requested by ' + str(ctx.author))
    help_embed.set_author(name='How To Play Hunt the Wumpus', icon_url='https://cdn.discordapp.com/emojis/732687928337104977.png?v=1')
    help_embed.add_field(name='Overview', value='The aim of the game is to shoot the Wumpus with one of your five '
                                                'arrows, however this is not as easy as it may sound. Each turn you '
                                                'can move into an adjacent cave or fire an arrow into the darkness.',
                         inline=False)
    help_embed.add_field(name='Hazards', value='The caves are dark, and you have to avoid falling into pits, running '
                                               'into bats, and startling the Wumpus! If you are near a hazard, '
                                               'you will be warned...', inline=False)
    help_embed.add_field(name='Winning', value='To win, you must shoot the Wumpus on your turn, however if you run '
                                               'out of arrows you lose!', inline=True)

    await ctx.send(embed=help_embed)


@client.command()
async def ogrules(ctx):
    print('LOG: ' + str(ctx.author) + ' requested "Texas Instruments Ruleset"')
    await ctx.send('These are the original instructions, only modified to better reflect the bot\'s rules')
    await ctx.send('```WELCOME TO \'HUNT THE WUMPUS\n\nTHE WUMPUS LIVES IN A CAVE OF 20 ROOMS: EACH ROOM HAS 3 '
                   'TUNNELS LEADING TO OTHER\nROOMS. (LOOK AT A DODECAHEDRON TO SEE HOW THIS WORKS. IF YOU DON\'T '
                   'KNOW WHAT A\nDODECAHEDRON IS, ASK SOMEONE)\n\n***\nHAZARDS:\n\nBOTTOMLESS PITS - TWO ROOMS HAVE '
                   'BOTTOMLESS PITS IN THEM\nIF YOU GO THERE: YOU FALL INTO THE PIT (& LOSE!)\n\nSUPER BATS  - TWO '
                   'OTHER ROOMS HAVE SUPER BATS. IF YOU GO THERE, A BAT GRABS YOU\nAND TAKES YOU TO SOME OTHER ROOM '
                   'AT RANDOM. (WHICH MIGHT BE TROUBLESOME)\n\nWUMPUS:\n\nTHE WUMPUS IS NOT BOTHERED BY THE HAZARDS ('
                   'HE HAS SUCKER FEET AND IS TOO BIG FOR\nA BAT TO LIFT). USUALLY HE IS ASLEEP. TWO THINGS WAKE HIM '
                   'UP: YOUR ENTERING HIS\nROOM OR YOUR SHOOTING AN ARROW.\n\nIF THE WUMPUS WAKES, HE MOVES (P=0.75) '
                   'ONE ROOM OR STAYS STILL (P=0.25). AFTER\nTHAT, IF HE IS WHERE YOU ARE, HE EATS YOU UP (& YOU '
                   'LOSE!)\n\nYOU:\n\nEACH TURN YOU MAY MOVE OR SHOOT A ARROW\nMOVING: YOU CAN GO ONE ROOM ('
                   'THRU ONE TUNNEL)\nARROWS: YOU HAVE 5 ARROWS. YOU LOSE WHEN YOU RUN OUT.\n\nIF THE ARROW '
                   'HITS THE WUMPUS: YOU WIN.\n\nWARNINGS:\n\nWHEN YOU ARE ONE '
                   'ROOM AWAY FROM WUMPUS OR ANY HAZARD, THE COMPUTER SAYS:\n\nWUMPUS - \'YOU CAN SMELL A HORRIBLE STENCH...\'\n\nBAT - '
                   '\'YOU HEAR FLAPPING IN THE DISTANCE...\'\n\nPIT - \'YOU CAN FEEL A GUST OF AIR NEARBY...\'```')


client.run(token)