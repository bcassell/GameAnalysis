'''
Created on Dec 17, 2013

@author: bcassell
'''

import GameIO as IO
import RandomGames

def main():
    parser = IO.io_parser('Create Data for Memory Experiments')
    parser.add_argument('players', type=int, help='number of players')
    parser.add_argument('strategies', type=int, help='number of strategies')
    IO.sys.argv = IO.sys.argv[:3] + ["-input", None] + IO.sys.argv[3:]
    args = parser.parse_args()
    game = RandomGames.uniform_symmetric_game(args.players, args.strategies, 0, 100).to_asymmetric_game()
    open(args.output + ".nfg", 'w').write(IO.to_NFG_asym(game))

if __name__ == "__main__":
    main()