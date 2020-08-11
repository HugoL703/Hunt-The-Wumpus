import discord
from discord import Message

import bat, pit, player, wumpus
import random
import os
import game
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='w!')
current_player = None
playing = False


@client.event
async def on_ready():
    print(f'{client.user} connected.')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="w!help"))


@client.command(help='Shows how to play the game')
async def rules(ctx):
    print('LOG: ' + str(ctx.author) + ' requested "Ruleset"')
    help_embed = discord.Embed(
        title='How To Play',
        description='w!ogrules will provide you with the (mostly) Original ruleset from the TI game.',
        colour=discord.Colour.from_rgb(0, 255, 208)
    )

    help_embed.set_footer(text='Requested by ' + str(ctx.author))
    help_embed.set_author(name='How To Play Hunt the Wumpus')
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


@client.command(help='Shows a mostly original ruleset')
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

# TODO: Player queue?


@client.command(help='Start playing a game!')
async def start(ctx):
    global current_player
    global playing
    g = game.Game(client)
    playing = True
    print('LOG: ' + str(ctx.author) + ' requested "start"')
    while playing:
        if current_player is None:
            current_player = ctx.author
            g.pl1.isAlive = True
            g.pl1.isWinner = False
            await ctx.send('*DEBUG:* ' + str(ctx.author) + ' is playing.')
            while playing:
                g.initial()
                while g.pl1.isAlive and not g.pl1.isWinner:
                    await g.gameloop(ctx)
                if g.endgame:
                    current_player = None
                    playing = False
        elif current_player != ctx.author:
            await ctx.send('Sorry, ' + str(current_player) + ' is currently playing. Please wait for them to finish!')
        elif ctx.author == current_player:
            await ctx.send('You are already playing!')


@client.command(help='End your game prematurely')
async def end(ctx):
    global current_player
    global playing
    g = game.Game(client)
    print('LOG: ' + str(ctx.author) + ' requested "end"')
    if current_player is None:
        await ctx.send('No one is playing!')
    elif current_player != ctx.author:
        await ctx.send('You are not playing!')
    else:
        await ctx.send('Game ended')
        current_player = None
        playing = False
        g.pl1.isAlive = False


@client.command(name='sudoend', help='Forces the current game to end, needs Admin permissions')
@has_permissions(administrator=True)
async def _sudoend(ctx):
    global current_player
    global playing
    g = game.Game(client)
    if playing:
        print('LOG: ' + str(ctx.author) + ' requested "sudo end". This ended the game of ' + str(current_player))
        playing = False
        g.pl1.isAlive = False
        await ctx.send('The admin, ' + str(ctx.author) + ', has ended the current game (' + str(current_player) + ')')
        current_player = None
    else:
        print('LOG: ' + str(ctx.author) + ' requested "sudo end", but no game was active')
        await ctx.send('No active game!')


@_sudoend.error
async def sudoend_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        print('LOG: ' + str(ctx.author) + ' requested "sudo end", but have insufficient perms ')
        await ctx.send('You don\'t have the permissions to do this!')


@client.command()
async def reacttest(ctx):
    emoji1 = '👍'
    emoji2 = '👎'
    msg = await ctx.send('Test message for reactions')
    await msg.add_reaction(emoji1)
    await msg.add_reaction(emoji2)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['👍', '👎']

    loop = 0
    while loop == 0:
            reaction, user = await client.wait_for('reaction_add', check=check)
            if reaction.emoji == emoji1:
                await ctx.send('Yes')
                loop = 1
            elif reaction.emoji == emoji2:
                await ctx.send('No')
                loop = 1




client.run(token)
