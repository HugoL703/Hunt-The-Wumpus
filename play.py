from game import Game

g = Game()

g.initial()

print('---= HUNT THE WUMPUS =---')
print()
rules = input('Would you like to read how to play before you begin? (Y/N) ')
if str.upper(rules) == 'Y':
    print('---= HOW TO PLAY =---')
    print()
    print('The Wumpus lives in a cave system, consisting of 20 different rooms\n'
          'Your goal is to shoot the Wumpus with one of your 5 arrows\n'
          'However, the cave is dark and full of danger...\n'
          '\n'
          'There are three Hazards you can find in the caves:\n'
          '-BATS: Will pick you up and move you to a random room\n'
          '-PITS: Will cause you to fall and lose\n'
          '-THE WUMPUS: Entering the Wumpus\'s room can\'t be good for your health!\n'
          '\n'
          'Additionally, if you run out of arrows, you lose!\n'
          'Each turn, you may move to or shoot an arrow into an adjacent room\n'
          'If you miss an arrow, the Wumpus has a 75% chance to wake up and move to another room\n'
          'If you are near a Hazard, a warning will be printed.')
elif str.upper(rules) == 'N':
    print('---==---')

elif str.upper(rules) != 'Y' or str.upper(rules) != 'N':
    print('I\'m not sure what that meant, starting game...')
while g.pl1.isAlive and not g.pl1.isWinner:
    g.gameloop()
    if not g.pl1.isAlive:
        g.endgamel()

    if g.pl1.isWinner:
        g.endgamew()