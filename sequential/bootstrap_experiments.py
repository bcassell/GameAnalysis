import Nash
import Regret
import GameIO as IO
import Bootstrap
from sequential.data import ObservationMatrix
import json
from argparse import ArgumentParser
import yaml_builder
    

def add_noise_sequentially(game, model, evaluator, samples_per_step):
    """
    Generate ObservationMatrix sequentially with bimodal gaussian noise added to each payoff.
    
    game: a RSG.Game or RSG.SampleGame
    model: noise model
    samples_per_step: the parameters passed to the noise function
    evaluator: the method used to determine when to stop sampling
    """
    matrix = ObservationMatrix()
    count = 0
    while evaluator.continue_sampling(matrix) and count < 1000:
        for prof in game.knownProfiles():
            matrix.addObservations(prof, model.generate_samples(game, prof, samples_per_step))
        count += samples_per_step
    return [matrix, evaluator.equilibria()]

def main():
    parser = ArgumentParser(description='Sequential Bootstrap Experiments')
    parser.add_argument('input_file', metavar='input_file', help='a yaml file specifying the required details')
    parser.add_argument('output_file', metavar='output_file', help='output json suitable for use with the plotting script')
    args = parser.parse_args()
    input = json.loads(open(args.input_file))
    results = [{s:{} for s in input['stdevs']} for i in range(input['num_games'])]

    for i in range(input['num_games']):
        base_game = yaml_builder.construct_game(input['game'])
        stopping_rule = yaml_builder.construct_stopping_rule(input['stopping_rule'], base_game)
        for stdev in input['stdevs']:
            noise_model = yaml_builder.construct_model(stdev, input['noise_model'])
            matrix, equilibria = add_noise_sequentially(base_game, noise_model, stopping_rule, input['samples_per_step'])
            sample_game = matrix.toGame()
            results[i][stdev][0] = [{"profile": eq, "statistic": Regret.regret(base_game, eq),
                                  "bootstrap" : Bootstrap.bootstrap(sample_game, eq, Regret.regret, "resample", ["game"]),
                                  "sample_count": sample_game.max_samples
                    } for eq in equilibria]
    f = open(args.output_file, 'w')
    f.write(IO.to_JSON_str(results, indent=None))

if __name__ == "__main__":
    main()
