from stopping_rules import StandardErrorEvaluator, EquilibriumCompareEvaluator
from noise_models import MultimodalNormalNoise
import RandomGames


def construct_stopping_rule(input, game):
    options = input.get('options', {})
    if input['type'] == 'stderr':
        return StandardErrorEvaluator(input['standard_err_threshold'], game.knownProfiles())
    elif input['type'] == 'equilibrium':
        return EquilibriumCompareEvaluator(input['compare_threshold'], **options)

def construct_model(stdev, input):
    options = input.get('options', {})
    if input['type'] == 'gaussian':
        return MultimodalNormalNoise(stdev, **options)
    
def construct_game(input):
    options = input.get('options', {})
    if input['type'] == 'local_effect':
        game = RandomGames.local_effect_game(**options)
    elif input['type'] == 'congestion':
        game = RandomGames.congestion_game(**options)
    elif input['type'] == 'uniform':
        game = RandomGames.uniform_symmetric_game(**options)
    RandomGames.rescale_payoffs(game)
    return game
