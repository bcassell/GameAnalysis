from RoleSymmetricGame import PayoffData
import Nash
import Regret
import GameIO as IO
import RandomGames
import Bootstrap
from data import ObservationMatrix
from stopping_rules import ConfidenceIntervalEvaluator, EquilibriumCompareEvaluator, StandardErrorEvaluator
from functools import partial
from numpy.random import normal, beta
import yaml
from random import choice
from argparse import ArgumentParser

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
                sample_game = add_bimodal_noise_sequentially(base_game, stdev, StandardErrorEvaluator(5.0, base_game.knownProfiles()), 10).toGame()
            else:
                sample_game = add_noise_sequentially(base_game, partial(normal, 0, stdev),
                                                 StandardErrorEvaluator(5.0, base_game.knownProfiles()), 10).toGame()
            a_profile = sample_game.knownProfiles()[0]
            a_role = a_profile.asDict().keys()[0]
            a_strategy = a_profile.asDict()[a_role].keys()[0]
            subsample_game = Bootstrap.subsample(sample_game, len(sample_game.getPayoffData(a_profile, a_role, a_strategy)))
            equilibria = Nash.mixed_nash(subsample_game)
            results[i][stdev][0] = [{"profile": eq, "statistic": Regret.regret(base_game, eq),
                                  "bootstrap" : Bootstrap.bootstrap(subsample_game, eq, Regret.regret, "resample", ["profile"]),
                                  "sample_count": subsample_game.max_samples
                    } for eq in equilibria]
    f = open(args.output_file, 'w')
    f.write(IO.to_JSON_str(results, indent=None))

if __name__ == "__main__":
    main()
