import random
import bat
import pit
import wumpus
import player
import asyncio

# TODO: Embed all messages and tidy up
class Game:
    rooms = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    pl1 = player.Player()
    b1 = bat.Bat()
    b2 = bat.Bat()
    p1 = pit.Pit()
    p2 = pit.Pit()
    w1 = wumpus.Wumpus()

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

        if self.pl1.arrows == 0:  # Check if player can continue or if they are out of arrows
            await ctx.send('You ran out of arrows...')
            self.pl1.isAlive = False
            return
        # inform the player of their room, adjacent rooms, and adjacent hazards, and arrow count
        await ctx.send('You are in room ' + str(self.pl1.current_room))
        await ctx.send('The rooms next to you are ' + str(Game.adjacent_rooms(self.pl1.current_room)))
        await ctx.send('You have ' + str(self.pl1.arrows) + ' arrows')
        if self.p1.current_room in Game.adjacent_rooms(self.pl1.current_room) or self.p2.current_room in \
                Game.adjacent_rooms(self.pl1.current_room):
            await ctx.send('You can feel a gust of air nearby...')
        if self.b1.current_room in Game.adjacent_rooms(self.pl1.current_room) or self.b2.current_room in \
                Game.adjacent_rooms(self.pl1.current_room):
            await ctx.send('You hear flapping in the distance...')
        if self.w1.current_room in Game.adjacent_rooms(self.pl1.current_room):
            await ctx.send('You can smell a horrible stench...')

        action = None
        choice = None
        # Player's turn choice, shoot an arrow or move rooms
        while str.upper(str(action)) != 'M' and str.upper(str(action)) != 'S':
            await ctx.send('Shoot or Move? (S/M) ')
            message = await self.client.wait_for('message', check=lambda
                message: message.author == ctx.author and message.content.lower() in ['m', 's'])
            action = message.content

        if str.upper(str(action)) == 'M':
            while choice not in Game.adjacent_rooms(self.pl1.current_room):
                await ctx.send('Move to which room?')
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
                await ctx.send('A bat picked you up and moved you to a random room!')
                self.pl1.current_room = random.choice(self.rooms)

            elif choice == self.p1.current_room or choice == self.p2.current_room:
                print()
                await ctx.send('You fell down a pit...')
                self.pl1.isAlive = False

            elif choice == self.w1.current_room:
                await ctx.send('You stepped into the Wumpus\'s room and startled him!')
                print()
                self.pl1.isAlive = False

        elif str.upper(str(action)) == 'S':
            while choice not in Game.adjacent_rooms(self.pl1.current_room):
                await ctx.send('Fire an arrow into which room?')
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
                await ctx.send('You shot the Wumpus')
                self.pl1.isWinner = True

            else:
                self.pl1.arrows -= 1
                print()
                await ctx.send('You missed...\n' + str(self.pl1.arrows) + ' arrows left...')
                wumpusmove = random.randint(1, 4)
                if wumpusmove != 1:
                    rechoose = False
                    while not rechoose:
                        self.w1.current_room = random.choice(self.rooms)
                        if self.w1.current_room != self.pl1.current_room:
                            return
                        elif self.w1.current_room == self.pl1.current_room:
                            rechoose = True

    def replay(self):
        playagain = input('Play again? (Y/N)')
        if str.upper(playagain) == 'Y':
            self.pl1.isWinner = False
            self.pl1.isAlive = True
            self.pl1.arrows = 5
            self.reset()
            self.initial()
        elif str.upper(playagain) == 'N':
            exit()

    def endgamel(self):
        print('You Lose!')
        self.replay()

    def endgamew(self):
        print('You Won!')
        self.replay()