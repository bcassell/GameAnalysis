from random import choice
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
