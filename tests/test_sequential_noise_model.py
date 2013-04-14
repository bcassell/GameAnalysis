from sequential.noise_models import MultimodalNormalNoise, SimulationBasedGame
import tests.factories.GameFactory as Factory
from RoleSymmetricGame import PayoffData

class describe_multi_modal_noise:
    def it_stores_profile_info(self):
        noise_model = MultimodalNormalNoise(1)
        game = Factory.create_symmetric_game()
        profile = game.knownProfiles()[0]
        noise_model.generate_samples(game, profile, 1)
        profile_info = noise_model.profile_info.get(profile, None)
        assert profile_info != None
        profile_info = profile_info.values()[0].values()[0]
        assert profile_info.get('offset', None) != None
        assert profile_info.get('stdev', None) != None
    
    def it_does_not_overwrite_profile_info(self):
        noise_model = MultimodalNormalNoise(1)
        game = Factory.create_symmetric_game()
        profile = game.knownProfiles()[0]
        noise_model.generate_samples(game, profile, 1)
        profile_info = noise_model.profile_info.get(profile, None)
        noise_model.generate_samples(game, profile, 1)
        profile_info2 = noise_model.profile_info.get(profile, None)
        r = profile.keys()[0]
        s = profile[r].keys()[0]
        assert profile_info[r][s]['offset'] == profile_info2[r][s]['offset']
        assert profile_info[r][s]['stdev'] == profile_info2[r][s]['stdev']

    def it_returns_the_correct_number_of_samples(self):
        noise_model = MultimodalNormalNoise(1)
        game = Factory.create_symmetric_game()
        profile = game.knownProfiles()[0]
        samples = noise_model.generate_samples(game, profile, 5)
        for role, strategy_hash in profile.items():
            counters = {s: 0 for s in strategy_hash.keys()}
            for payoff_data in samples[role]:
                counters[payoff_data.strategy] += 1
                assert payoff_data.count == strategy_hash[payoff_data.strategy]
                assert len(payoff_data.value) == 5
            for s in strategy_hash.keys():
                assert counters[s] == 1
    
class describe_simulation_based_game:
    def it_stores_available_indices_in_a_counter_dict(self):
        matrix = Factory.create_observation_matrix()
        temp = matrix.knownProfiles()[0]
        matrix.addObservations(temp, {r: [PayoffData(s, count, [23.0]) for s, count in s_hash.items()] for r, s_hash in temp.items()})
        game = matrix.toGame()
        sbg = SimulationBasedGame(game)
        assert sbg.counter_dict[temp] == set(range(game.max_samples))
        assert sbg.counter_dict[matrix.knownProfiles()[1]] == set(range(game.max_samples - 1))
    
    def it_reduces_the_availabe_indices_when_samples_are_gathered(self):
        matrix = Factory.create_observation_matrix(sample_count=5)
        game = matrix.toGame()
        sbg = SimulationBasedGame(game)
        target_profile = game.knownProfiles()[0]
        observations = sbg.generate_samples(game, target_profile, 2)
        assert len(sbg.counter_dict[target_profile]) == game.max_samples - 2
        assert observations == {r: [PayoffData(s, count, [game.getPayoffData(target_profile, r, s)[x]
                    for x in set(range(game.max_samples)).difference(sbg.counter_dict[target_profile])])
                    for s, count in s_hash.items()] for r, s_hash in target_profile.items()}
    
    def it_gives_the_requested_observations(self):
        matrix = Factory.create_observation_matrix(sample_count=5)
        game = matrix.toGame()
        sbg = SimulationBasedGame(game)
        target_profile = game.knownProfiles()[0]
        observations = sbg.get_observations(target_profile, [0, 2])
        assert observations == {r: [PayoffData(s, count, [game.getPayoffData(target_profile, r, s)[0], game.getPayoffData(target_profile, r, s)[2]])
                    for s, count in s_hash.items()] for r, s_hash in target_profile.items()}