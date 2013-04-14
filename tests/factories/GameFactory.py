from RoleSymmetricGame import Game, PayoffData
from sequential.data import ObservationMatrix
from itertools import product, combinations_with_replacement as CwR
import random

def create_symmetric_game(number_of_players=2, strategy_set=['C', 'D'], payoff_data=None):
    payoff_data = payoff_data or create_payoff_data(['All'], {'All': number_of_players},
                                                    {'All': strategy_set})    
    return Game(['All'], {'All': number_of_players}, {'All': strategy_set}, payoff_data)

def create_observation_matrix(number_of_players=2, strategy_set=['C', 'D'], payoff_data=None, sample_count=1):
    payoff_data = payoff_data or create_payoff_data(['All'], {'All': number_of_players},
                                                    {'All': strategy_set}, sample_count)    
    return ObservationMatrix(payoff_data)

def create_payoff_data(roles, players, strategies, count=1):
    return [{r: [PayoffData(s, p[index].count(s), [random.random() for __ in range(count)]) for s in set(p[index])] \
            for index, r in enumerate(roles)} \
            for p in product(*[CwR(strategies[r], players[r]) for r in roles])]