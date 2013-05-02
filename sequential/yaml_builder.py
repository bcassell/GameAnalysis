from stopping_rules import StandardErrorEvaluator, EquilibriumCompareEvaluator, EquilibriumConfidenceEvaluator
from noise_models import MultimodalNormalNoise, SimulationBasedGame
from confidence import BootstrapConfidenceInterval
import RandomGames
import GameIO
import Reductions

def construct_stopping_rule(input, game):
    options = input.get('options', {})
    if input['type'] == 'stderr':
        return StandardErrorEvaluator(input['standard_err_threshold'], game.knownProfiles())
    elif input['type'] == 'equilibrium':
        return EquilibriumCompareEvaluator(input['compare_threshold'], **options)
    elif input['type'] == 'eq_ci':
        return EquilibriumConfidenceEvaluator(input['delta'], input['alpha'], BootstrapConfidenceInterval())

def construct_model(stdev, input):
    options = input.get('options', {})
    if input['type'] == 'gaussian':
        return MultimodalNormalNoise(stdev, **options)
    if input['type'] == 'file':
        return SimulationBasedGame(Reductions.deviation_preserving_reduction(GameIO.read(input['file']), {'All': 6}))
    
def construct_game(input):
    options = input.get('options', {})
    if input['type'] == 'local_effect':
        game = RandomGames.local_effect_game(**options)
        RandomGames.rescale_payoffs(game)
    elif input['type'] == 'congestion':
        game = RandomGames.congestion_game(**options)
        RandomGames.rescale_payoffs(game)
    elif input['type'] == 'uniform':
        game = RandomGames.uniform_symmetric_game(**options)
        RandomGames.rescale_payoffs(game)
    elif input['type'] == 'file':
        game = Reductions.deviation_preserving_reduction(GameIO.read(input['file']), {'All': 6})
    return game
