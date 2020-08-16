import random

import discord

import bat
import pit
import wumpus
import player


class Game:
    rooms = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    pl1 = player.Player()
    b1 = bat.Bat()
    b2 = bat.Bat()
    p1 = pit.Pit()
    p2 = pit.Pit()
    w1 = wumpus.Wumpus()
    pitwarn = False
    batwarn = False
    wumpuswarn = False
    sendembed = False
    noarrows = False
    choice_move = None
    choice_shoot = None
    wumpusshot = False
    pitdeath = False
    wumpusdeath = False
    endgame = False
    replay = True
    batmove = False
    earlyend = False

    def __init__(self, client):
        self.client = client

    def reset(self):  # used on new game
        self.pl1.current_room = -1
        self.w1.current_room = -1
        self.b1.current_room = -1
        self.b2.current_room = -1
        self.p1.current_room = -1
        self.p2.current_room = -1

    # Place everything in rooms. Two of the same hazard cannot exist in the same room, and the player starts safe
    def initial(self):
        self.reset()
        self.pl1.current_room = random.choice(self.rooms)

        while self.b1.current_room == self.pl1.current_room or self.b1.current_room < 0:
            self.b1.current_room = random.choice(self.rooms)
        while self.b2.current_room == self.pl1.current_room or self.b2.current_room == self.b1.current_room or \
                self.b2.current_room < 0:
            self.b2.current_room = random.choice(self.rooms)

        while self.p1.current_room == self.pl1.current_room or self.p1.current_room < 0:
            self.p1.current_room = random.choice(self.rooms)
        while self.p2.current_room == self.pl1.current_room or self.p2.current_room == self.p1.current_room or \
                self.p2.current_room < 0:
            self.p2.current_room = random.choice(self.rooms)

        while self.w1.current_room == self.pl1.current_room or self.w1.current_room < 0:
            self.w1.current_room = random.choice(self.rooms)

        self.pl1.isAlive = True
        self.pl1.isWinner = False
        self.pl1.arrows = 5
        self.batwarn = False
        self.pitwarn = False
        self.wumpuswarn = False
        self.sendembed = False
        self.noarrows = False
        self.choice_move = None
        self.choice_shoot = None
        self.wumpusshot = False
        self.pitdeath = False
        self.wumpusdeath = False
        self.endgame = False
        self.replay = True
        self.batmove = False
        self.earlyend = False

    @staticmethod
    def adjacent_rooms(current_room):
        rmap = [[2, 5, 8],
                [1, 3, 10],
                [2, 4, 12],
                [3, 5, 14],
                [4, 6, 1],
                [5, 7, 15],
                [6, 8, 17],
                [7, 9, 1],
                [8, 10, 18],
                [9, 11, 2],
                [10, 12, 19],
                [11, 13, 3],
                [12, 14, 20],
                [13, 15, 4],
                [14, 16, 6],
                [15, 17, 20],
                [16, 18, 7],
                [17, 19, 9],
                [18, 20, 11],
                [19, 13, 16]]
        return rmap[current_room - 1]

    ''' How a turn should work:

        End game if in pit/wumpus/out of arrows
        Move player if in bat
        Warn player of adjacent hazards
        Get input
        > Move player by choice
        >> Which Room
        > Shoot arrows by choice
        >> How Many Arrows?
        >> Which Room
        >>> Check if arrow hits
        >>>> Player, miss, wumpus?
        '''

    async def gameloop(self, ctx):
        if not self.earlyend:
            if self.pl1.arrows == 0:  # Check if player can continue or if they are out of arrows
                # await ctx.send('You ran out of arrows...')
                self.noarrows = True
                self.pl1.isAlive = False
                await self.endgamel(ctx)
                return
            # inform the player of their room, adjacent rooms, and adjacent hazards, and arrow count
            # await ctx.send('You are in room ' + str(self.pl1.current_room))
            # await ctx.send('The rooms next to you are ' + str(Game.adjacent_rooms(self.pl1.current_room)))
            # await ctx.send('You have ' + str(self.pl1.arrows) + ' arrows')
            if self.p1.current_room in Game.adjacent_rooms(self.pl1.current_room) or self.p2.current_room in \
                    Game.adjacent_rooms(self.pl1.current_room):
                # await ctx.send('You can feel a gust of air nearby...')
                self.pitwarn = True
            if self.b1.current_room in Game.adjacent_rooms(self.pl1.current_room) or self.b2.current_room in \
                    Game.adjacent_rooms(self.pl1.current_room):
                # await ctx.send('You hear flapping in the distance...')
                self.batwarn = True
            if self.w1.current_room in Game.adjacent_rooms(self.pl1.current_room):
                # await ctx.send('You can smell a horrible stench...')
                self.wumpuswarn = True

            await self.embed(ctx)

            action = None
            choice = None

            # Player's turn choice, shoot an arrow or move rooms
            # while str.upper(str(action)) != 'M' and str.upper(str(action)) != 'S':
            #     await ctx.send('Shoot or Move? (S/M) ')
            #     message = await self.client.wait_for('message', check=lambda
            #         message: message.author == ctx.author and message.content.lower() in ['m', 's'])
            #     action = message.content

            if self.choice_move:
                while choice not in Game.adjacent_rooms(self.pl1.current_room) and self.pl1.isAlive:
                    embed = discord.Embed(
                        colour=discord.Colour.greyple()
                    )
                    embed.set_author(name='Hunt The Wumpus')
                    embed.add_field(name=str(ctx.author) + '\'s game',
                                    value='Type the room you would like move to:')
                    await ctx.send(embed=embed)
                    message = await self.client.wait_for('message', check=lambda message: message.author == ctx.author)
                    choice = message.content
                    try:
                        int(choice)
                    except ValueError:
                        choice = -1
                    else:
                        choice = int(choice)
                self.pl1.current_room = int(choice)

                if choice == self.b1.current_room or choice == self.b2.current_room:
                    print()
                    # await ctx.send('A bat picked you up and moved you to a random room!')
                    self.batmove = True
                    self.pl1.current_room = random.choice(self.rooms)

                elif choice == self.p1.current_room or choice == self.p2.current_room:
                    print()
                    await ctx.send('You fell down a pit...')
                    self.pl1.isAlive = False
                    self.pitdeath = True
                    await self.endgamel(ctx)
                    return

                elif choice == self.w1.current_room:
                    await ctx.send('You stepped into the Wumpus\'s room and startled him!')
                    print()
                    self.pl1.isAlive = False
                    self.wumpusdeath = True
                    await self.endgamel(ctx)
                    return

            elif self.choice_shoot:
                while choice not in Game.adjacent_rooms(self.pl1.current_room) and self.pl1.isAlive:
                    embed = discord.Embed(
                        colour=discord.Colour.greyple()
                    )
                    embed.set_author(name='Hunt The Wumpus')
                    embed.add_field(name=str(ctx.author) + '\'s game',
                                    value='Type the room you would like to fire an arrow into:')
                    await ctx.send(embed=embed)
                    message = await self.client.wait_for('message', check=lambda message: message.author == ctx.author)
                    choice = message.content
                    try:
                        int(choice)
                    except ValueError:
                        choice = -1
                    else:
                        choice = int(choice)

                if choice == self.w1.current_room:
                    print()
                    # await ctx.send('You shot the Wumpus')
                    self.wumpusshot = True
                    self.pl1.isWinner = True
                    await self.endgamew(ctx)
                    return

                else:
                    self.pl1.arrows -= 1
                    print()
                    # await ctx.send('You missed...\n' + str(self.pl1.arrows) + ' arrows left...')
                    embed = discord.Embed(
                        colour=discord.Colour.dark_red()
                    )
                    embed.set_author(name='Hunt The Wumpus')
                    embed.add_field(name=str(ctx.author) + '\'s game',
                                    value='You missed your shot!')
                    await ctx.send(embed=embed)
                    wumpusmove = random.randint(1, 4)
                    if wumpusmove != 1:
                        rechoose = False
                        while not rechoose:
                            self.w1.current_room = random.choice(self.rooms)
                            if self.w1.current_room != self.pl1.current_room:
                                return
                            elif self.w1.current_room == self.pl1.current_room:
                                rechoose = True

            self.choice_shoot = None
            self.choice_move = None

    async def embed(self, ctx):
        if self.pl1.isAlive:
            warn = 0  # 0=none, 1=pit, 2=bat, 3=pitbat. 4=wump, 5=wumppit, 6=wumpbat, 7=all
            if self.pitwarn:
                warn += 1
                self.pitwarn = False
            if self.batwarn:
                warn += 2
                self.batwarn = False
            if self.wumpuswarn:
                warn += 4
                self.wumpuswarn = False
            message = {
                1: 'You can feel a gust of air nearby...',
                2: 'You hear flapping in the distance...',
                3: 'You can feel a gust of air nearby...\nYou hear flapping in the distance...',
                4: 'You can smell a horrible stench...',
                5: 'You can smell a horrible stench...\nYou can feel a gust of air nearby...',
                6: 'You can smell a horrible stench...\nYou hear flapping in the distance...',
                7: 'You can smell a horrible stench...\nYou can feel a gust of air nearby...\nYou hear flapping in the distance... '
            }

            game_embed = discord.Embed(
                colour=discord.Colour.greyple()
            )
            game_embed.set_author(name='Hunt The Wumpus')
            if self.batmove:
                game_embed.add_field(name=str(ctx.author) + '\'s game',
                                     value='A bat moved you to a random room!\nYou are in room ' + str(
                                         self.pl1.current_room) + '\nThe rooms next to you are ' + str(
                                         self.adjacent_rooms(self.pl1.current_room)) + '\nYou have ' + str(
                                         self.pl1.arrows) + ' arrows')
            else:
                game_embed.add_field(name=str(ctx.author) + '\'s game',
                                     value='You are in room ' + str(
                                         self.pl1.current_room) + '\nThe rooms next to you are ' + str(
                                         self.adjacent_rooms(self.pl1.current_room)) + '\nYou have ' + str(
                                         self.pl1.arrows) + ' arrows')
            if warn > 0:
                game_embed.add_field(name='Warnings:', value=message[warn])

            shoot = '🏹'
            move = '🧭'
            msg = await ctx.send(embed=game_embed)
            await msg.add_reaction(shoot)
            await msg.add_reaction(move)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['🏹', '🧭']

            loop = 0
            while loop == 0:
                reaction, user = await self.client.wait_for('reaction_add', check=check)
                if reaction.emoji == shoot:
                    self.choice_shoot = True
                    loop = 1
                elif reaction.emoji == move:
                    self.choice_move = True
                    loop = 1

    async def endgamel(self, ctx):
        replay_embed = discord.Embed(
            colour=discord.Colour.red()
        )
        replay_embed.set_author(name='Hunt The Wumpus')
        if self.pitdeath:
            replay_embed.add_field(name=str(ctx.author) + '\'s game',
                                   value='You Lose!\n'
                                         'You fell into a pit!\n'
                                         'Play again?')
        elif self.wumpusdeath:
            replay_embed.add_field(name=str(ctx.author) + '\'s game',
                                   value='You Lose!\n'
                                         'You startled the Wumpus!\n'
                                         'Play again?')
        elif self.noarrows:
            replay_embed.add_field(name=str(ctx.author) + '\'s game',
                                   value='You Lost!\n'
                                         'You ran out of arrows!\n'
                                         'Play again?')
        else:
            replay_embed.add_field(name=str(ctx.author) + '\'s game',
                                   value='You Lost!\n')

        if self.noarrows or self.pitdeath or self.wumpusdeath:
            y = '✅'
            n = '❌'
            msg = await ctx.send(embed=replay_embed)
            await msg.add_reaction(y)
            await msg.add_reaction(n)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

            loop = 0
            while loop == 0:
                reaction, user = await self.client.wait_for('reaction_add', check=check)
                if reaction.emoji == y:
                    self.pl1.isAlive = False
                    loop = 1
                elif reaction.emoji == n:
                    self.replay = False
                    self.endgame = True
                    loop = 1
        else:
            await ctx.send(embed=replay_embed)
            self.replay = False
            self.endgame = True

    async def endgamew(self, ctx):
        replay_embed = discord.Embed(
            colour=discord.Colour.green()
        )
        replay_embed.set_author(name='Hunt The Wumpus')
        replay_embed.add_field(name=str(ctx.author) + '\'s game',
                               value='You have Won!\n'
                                     'You shot the Wumpus!\n'
                                     'Play again?')
        y = '✅'
        n = '❌'
        msg = await ctx.send(embed=replay_embed)
        await msg.add_reaction(y)
        await msg.add_reaction(n)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

        loop = 0
        while loop == 0:
            reaction, user = await self.client.wait_for('reaction_add', check=check)
            if reaction.emoji == y:
                self.pl1.isAlive = False
                loop = 1
            elif reaction.emoji == n:
                self.replay = False
                self.endgame = True
                loop = 1
