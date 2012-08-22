#! /usr/bin/env python2.7

from BasicFunctions import leading_zeros
from RoleSymmetricGame import Game, SampleGame, PayoffData
from GameIO import io_parser

from itertools import combinations
from numpy.random import uniform as U, normal
from numpy import array, arange

def uniform_zero_sum(S):
	roles = ["row", "column"]
	players = {r:1 for r in roles}
	strategies = {"row":["r" + leading_zeros(i,S) for i in range(S)], \
			"column":["c" + leading_zeros(i,S) for i in range(S)]}
	g = Game(roles, players, strategies)
	for prof in g.allProfiles():
		row_strat = prof["row"].keys()[0]
		row_val = U(-1,1)
		col_strat = prof["column"].keys()[0]
		p = {"row":[PayoffData(row_strat, 1, row_val)], \
				"column":[PayoffData(col_strat, 1, -row_val)]}
		g.addProfile(p)
	return g


def uniform_symmetric(N, S):
	roles = ["All"]
	players = {"All":N}
	strategies = {"All":["s" + leading_zeros(i,S) for i in range(S)]}
	g = Game(roles, players, strategies)
	for prof in g.allProfiles():
		payoffs = []
		for strat, count in prof["All"].items():
			payoffs.append(PayoffData(strat, count, U(-1,1)))
		g.addProfile({"All":payoffs})
	return g


def congestion(N, facilities, required):
	roles = ["All"]
	players = {"All":N}
	strategies = {'+'.join(["f"+str(f) for f in strat]):strat for strat in \
			combinations(range(facilities), required)}
	facility_values = [array([U(facilities), U(-required), U(-1)]) for i in \
			range(facilities)]
	g = Game(roles, players, {"All":strategies.keys()})
	for prof in g.allProfiles():
		payoffs = []
		useage = [0]*facilities
		for strat, count in prof["All"].items():
			for facility in strategies[strat]:
				useage[facility] += count
		for strat, count in prof["All"].items():
			payoffs.append(PayoffData(strat, count, congestion_payoff(useage, \
					facility_values, strategies[strat])))
		g.addProfile({"All":payoffs})
	return g

def congestion_payoff(useage, facility_values, facility_set):
	value = 0
	for f in facility_set:
		value += sum(useage[f]**arange(3) * facility_values[f])
	return value


def normal_noise(game, stdev, samples):
	sg = SampleGame(game.roles, game.players, game.strategies)
	for prof in game.knownProfiles():
		sg.addProfile({r:[PayoffData(s, prof[r][s], normal(0, stdev, samples)) \
				for s in prof[r]] for r in game.roles})
	return sg


from GameIO import to_JSON_str
from argparse import ArgumentParser
import sys

def parse_args():
	parser = io_parser(description="Generate random games.")
	parser.add_argument("type", choices=["uZS", "uSym", "CG"], help= \
			"Type of random game to generate. uZS = uniform zero sum. " +\
			"uSym = uniform symmetric. CG = congestion game.")
	parser.add_argument("count", type=int, help="Number of random games " +\
			"to create.")
	parser.add_argument("-samples", type=int, default=1, help="Number of " +\
			"noisy samples to give for each profile. -stdev must also be " +\
			"specified.")
	parser.add_argument("-stdev", type=float, default=0, help="Standard " +\
			"deviation of normal noise added to each sample. -samples must " +\
			"also be specified.")
	parser.add_argument("game_args", nargs="*", help="Additional arguments " +\
			"for game generator function.")
	assert "-input" not in sys.argv, "no input JSON required"
	sys.argv = sys.argv[:3] + ["-input", None] + sys.argv[3:]
	return parser.parse_args()


def main():
	args = parse_args()
	game_args = map(int, args.game_args)
	if args.type == "uZS":
		game_func = uniform_zero_sum
		assert len(game_args) == 1, "one game_arg specifies strategy count"
	elif args.type == "uSym":
		game_func = uniform_symmetric
		assert len(game_args) == 2, "game_args specify player and strategy "+\
				"counts"
		game_args = map(int, args.game_args[:2])
	elif args.type == "CG":
		game_func = congestion
		assert len(game_args) == 3, "game_args specify player, facility, and"+\
				" required facility counts"
	games = [game_func(*game_args) for i in range(args.count)]
	if args.samples > 1 and args.stdev > 0:
		noisy = map(lambda g: normal_noise(g, args.stdev, args.samples), games)
		games = zip(games, noisy)
	if len(games) == 1:
		print to_JSON_str(games[0])
	else:
		print to_JSON_str(games)


if __name__ == "__main__":
	main()
