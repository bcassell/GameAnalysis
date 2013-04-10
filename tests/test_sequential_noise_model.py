from sequential.noise_models import MultimodalNormalNoise
import tests.factories.GameFactory as Factory

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