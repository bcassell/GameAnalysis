import yaml
import yaml_builder
from argparse import ArgumentParser
import GameIO
import Nash
import Regret
from data import ObservationMatrix
from stopping_rules import ConfidenceIntervalEvaluator
from confidence import BootstrapConfidenceInterval

def single_test(game, noise_model, samples_per_step, delta, alpha):
    matrix = ObservationMatrix()
    for prof in game.knownProfiles():
        matrix.addObservations(prof, noise_model.generate_samples(game, prof, samples_per_step))
    candidate = Nash.mixed_nash(matrix.toGame(), at_least_one=True)[0]
    regret = Regret.regret(game, candidate)
    data = {"candidate": candidate, "game_eq": regret < delta, "regret": regret, "ne-regrets": {role: 
                {strategy: Regret.regret(game, candidate, role, strategy) for strategy in game.strategies[role]} for role in game.roles}}
    evaluator = ConfidenceIntervalEvaluator(game, [candidate], delta, alpha, BootstrapConfidenceInterval())
    count = samples_per_step
    target_set = Regret.mixture_neighbors(game, candidate)
    while evaluator.continue_sampling(matrix) and count < 500:
        print "sample"
        for prof in target_set:
            matrix.addObservations(prof, noise_model.generate_samples(game, prof, samples_per_step))
        count += samples_per_step
    data["stopping_decision"] = evaluator.get_decision(game, candidate)
    data["sample_count"] = matrix.toGame().max_samples
    return data

def main():
    parser = ArgumentParser(description='Sequential CI Experiments')
    parser.add_argument('input_file', metavar='input_file', help='a yaml file specifying the required details')
    parser.add_argument('output_file', metavar='output_file', help='output json')
    args = parser.parse_args()
    input = yaml.safe_load(open(args.input_file))
    f = open(args.output_file, 'a')
    f.write("{")
    for stdev in input['stdevs']:
        f.write("\""+str(stdev)+"\""+":[")
        print stdev
        noise_model = yaml_builder.construct_model(stdev, input['noise_model'])
        for i in range(input['num_games']):
            print i
            base_game = yaml_builder.construct_game(input['game'])
            data = single_test(base_game, noise_model, input['samples_per_step'], input['delta'], input['alpha'])
            f.write(GameIO.to_JSON_str(data, indent=None))
            if i == input['num_games']-1:
                f.write("]")
            else:
                f.write(",")
        if stdev != input['stdevs'][-1]:
            f.write(",")
    f.write("}")

if __name__ == "__main__":
    main()