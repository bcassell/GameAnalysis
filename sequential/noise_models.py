from random import choice, sample
import numpy.random as rand
import numpy
from RoleSymmetricGame import PayoffData


class MultimodalNormalNoise:
    def __init__(self, max_stdev, modes=2, spread_mult=2):
        self.max_stdev = max_stdev
        self.multipliers = numpy.arange(float(modes)) - float(modes-1)/2
        self.spread_mult = spread_mult
        self.profile_info = {}
        
    def generate_samples(self, game, profile, sample_count):
        if profile not in self.profile_info:
            self.profile_info[profile] = {r: {s: {'offset': rand.normal(0, self.max_stdev*self.spread_mult), 
                    'stdev': rand.beta(2,1) * self.max_stdev} for s in profile[r]} for r in profile.keys()}
        return {r: [PayoffData(s, profile[r][s], game.getPayoff(profile, r, s) +
                    [rand.normal(choice(self.multipliers)*self.profile_info[profile][r][s]['offset'],
                                 self.profile_info[profile][r][s]['stdev'])
                     for __ in range(sample_count)]) for s in profile[r].keys()] for r in profile.keys()}

class SimulationBasedGame:
    def __init__(self, sample_game):
        self.sample_game = sample_game
        # Assume there are the same number of observations for each role and strategy in a profile
        self.counter_dict = { profile: set(range(len(sample_game.getPayoffData(profile, profile.keys()[0], profile.values()[0].keys()[0]))))
                             for profile in sample_game.knownProfiles() }
        
    def get_observations(self, profile, indexes):
        return {r: [PayoffData(s, count, [self.sample_game.getPayoffData(profile, r, s)[x] for x in indexes])
                    for s, count in s_hash.items()] for r, s_hash in profile.items()}
    
    def generate_samples(self, game, profile, sample_count):
        indexes = sample(self.counter_dict[profile], sample_count)
        self.counter_dict[profile] = self.counter_dict[profile].difference(indexes)
        return self.get_observations(profile, indexes)
    