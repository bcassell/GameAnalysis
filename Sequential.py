from RoleSymmetricGame import Profile, PayoffData, SampleGame
from BasicFunctions import flatten
import Nash
from numpy.linalg import norm
import Regret
from scipy.stats.stats import sem
import GameIO as IO
import RandomGames
import Bootstrap
from functools import partial
from numpy.random import normal, beta
import yaml
from random import choice
from argparse import ArgumentParser

class ObservationMatrix:
    def __init__(self, payoff_data=[]):
        self.profile_dict = {}
        for profile_data_set in payoff_data:
            self.addObservations(Profile({role: {payoff.strategy: payoff.count for payoff in payoffs}
                                         for role, payoffs in profile_data_set.items()}), profile_data_set)

    def addObservations(self, profile, role_payoffs):
        profile_entry = self.profile_dict.get(profile, {role: {strategy: [] for strategy in strategies}
                                        for role, strategies in profile.items()})
        for role, strategies in profile_entry.items():
            for payoff in role_payoffs[role]:
                strategies[payoff.strategy].extend(payoff.value)
        self.profile_dict[profile] = profile_entry
    
    def getPayoffData(self, profile, role, strategy):
        return self.profile_dict[profile][role][strategy]
    
    def toGame(self):
        sample_profile = self.profile_dict.keys()[0]
        g_roles = sample_profile.keys()
        g_players = {role: sum(strategies.values()) for role, strategies in sample_profile.items()}
        g_strategies = {role: flatten([profile[role].keys() for profile in self.profile_dict.keys()]) for role in g_roles}
        g_payoff_data = [{role: [PayoffData(strategy, profile[role][strategy], observations)
                        for strategy, observations in strategies.items()]
                        for role, strategies in role_strategies.items()} 
                        for profile, role_strategies in self.profile_dict.items()]
        return SampleGame(g_roles, g_players, g_strategies, g_payoff_data)

def add_bimodal_noise_sequentially(game, max_stdev, evaluator, samples_per_step):
    """
    Generate ObservationMatrix sequentially with bimodal gaussian noise added to each payoff.
    
    game: a RSG.Game or RSG.SampleGame
    samples_per_step: the parameters passed to the noise function
    evaluator: the method used to determine when to stop sampling
    """
    matrix = ObservationMatrix()
    
    # Setup the info for each payoff
    dist_info = {}
    for prof in game.knownProfiles():
        dist_info[prof] = {r: {s: {'offset': normal(0, max_stdev), 'stdev': beta(2,1) * max_stdev} 
                               for s in prof[r]} for r in game.roles}
    
    print 'dist_info set'
    while evaluator.continue_sampling(matrix):
        for prof in game.knownProfiles():
            matrix.addObservations(prof, {r:[PayoffData(s, prof[r][s], game.getPayoff(prof,r,s) +
                [normal(choice([-1, 1])*dist_hash['offset'], dist_hash['stdev'])
                 for _ in range(samples_per_step)]) for s, dist_hash in dist_info[prof][r].items()] for r in game.roles})
    return matrix        

def add_noise_sequentially(game, model, evaluator, samples_per_step):
    """
    Generate ObservationMatrix sequentially with random noise added to each payoff.
    
    game: a RSG.Game or RSG.SampleGame
    model: a 2-parameter function that generates mean-zero noise
    samples_per_step: the parameters passed to the noise function
    evaluator: the method used to determine when to stop sampling
    """
    matrix = ObservationMatrix()
    while evaluator.continue_sampling(matrix):
        for prof in game.knownProfiles():
            matrix.addObservations(prof, {r:[PayoffData(s, prof[r][s], game.getPayoff(prof,r,s) + \
                model(samples_per_step)) for s in prof[r]] for r in game.roles})
    return matrix

class StandardErrorEvaluator:
    def __init__(self, standard_err_threshold, target_set):
        self.standard_err_threshold = standard_err_threshold
        self.target_set = target_set
        
    def continue_sampling(self, matrix):
        if matrix.profile_dict == {}:
            return True
        for profile in self.target_set:
            for role, strategies in profile.items():
                for strategy in strategies.keys():
                    if sem(matrix.getPayoffData(profile, role, strategy)) >= self.standard_err_threshold:
                        return True
        return False

class EquilibriumCompareEvaluator:
    def __init__(self, compare_threshold, regret_threshold=1e-4, dist_threshold=None, 
                 random_restarts=0, iters=10000, converge_threshold=1e-8):
        self.compare_threshold = compare_threshold
        self.regret_threshold = regret_threshold
        self.dist_threshold = dist_threshold or compare_threshold/2.0
        self.random_restarts = random_restarts
        self.iters = iters
        self.converge_threshold = converge_threshold
        self.old_equilibria = []
        
    def continue_sampling(self, matrix):
        if matrix.profile_dict == {}:
            return True
        game = matrix.toGame()
        decision = False
        equilibria = []
        all_eq = []
        for old_eq in self.old_equilibria:
            new_eq = Nash.replicator_dynamics(game, old_eq, self.iters, self.converge_threshold)
            decision = decision or norm(new_eq-old_eq, 2) > self.compare_threshold
            distances = map(lambda e: norm(e-new_eq, 2), equilibria)
            if Regret.regret(game, new_eq) <= self.regret_threshold and \
                    all([d >= self.dist_threshold for d in distances]):
                equilibria.append(new_eq)
            all_eq.append(new_eq)
        for m in game.biasedMixtures() + [game.uniformMixture()] + \
                [game.randomMixture() for __ in range(self.random_restarts)]:
            eq = Nash.replicator_dynamics(game, m, self.iters, self.converge_threshold)
            distances = map(lambda e: norm(e-eq,2), equilibria)
            if Regret.regret(game, eq) <= self.regret_threshold and \
                    all([d >= self.dist_threshold for d in distances]):
                equilibria.append(eq)
                decision = True
            all_eq.append(eq)
        if len(equilibria) == 0:
            decision = True
            self.old_equilibria = [min(all_eq, key=lambda e: Regret.regret(game, e))]
        else:
            self.old_equilibria = equilibria
        return decision


def main():
    parser = ArgumentParser(description='Sequential Bootstrap Experiments')
    parser.add_argument('input_file', metavar='input_file', help='a yaml file specifying the required details')
    parser.add_argument('output_file', metavar='output_file', help='output json suitable for use with the plotting script')
    args = parser.parse_args()
    input = yaml.safe_load(open(args.input_file))
    results = [{s:{} for s in input['stdevs']} for i in range(input['num_games'])]
    for i in range(input['num_games']):
        print i
        base_game = RandomGames.local_effect(6, 4)
        for stdev in input['stdevs']:
            if input['model'] == 'bimodal':
                sample_game = add_bimodal_noise_sequentially(base_game, stdev, EquilibriumCompareEvaluator(0.001), 10).toGame()
            else:
                sample_game = add_noise_sequentially(base_game, partial(normal, 0, stdev),
                                                 EquilibriumCompareEvaluator(0.001), 10).toGame()
            a_profile = sample_game.knownProfiles()[0]
            a_role = a_profile.asDict().keys()[0]
            a_strategy = a_profile.asDict()[a_role].keys()[0]
            subsample_game = Bootstrap.subsample(sample_game, len(sample_game.getPayoffData(a_profile, a_role, a_strategy)))
            equilibria = Nash.mixed_nash(subsample_game)
            results[i][stdev][0] = [{"profile": eq, "statistic": Regret.regret(base_game, eq),
                                  "bootstrap" : Bootstrap.bootstrap(subsample_game, eq, Regret.regret, "resample", ["profile"])
                    } for eq in equilibria]
    f = open(args.output_file, 'w')
    f.write(IO.to_JSON_str(results, indent=None))

if __name__ == "__main__":
    main()
