from RoleSymmetricGame import Profile, PayoffData, SampleGame
import BasicFunctions

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

    def knownProfiles(self):
        return self.profile_dict.keys()

    def toGame(self):
        sample_profile = self.profile_dict.keys()[0]
        g_roles = sample_profile.keys()
        g_players = {role: sum(strategies.values()) for role, strategies in sample_profile.items()}
        g_strategies = {role: BasicFunctions.flatten([profile[role].keys() for profile in self.profile_dict.keys()]) for role in g_roles}
        g_payoff_data = [{role: [PayoffData(strategy, profile[role][strategy], observations)
                        for strategy, observations in strategies.items()]
                        for role, strategies in role_strategies.items()} 
                        for profile, role_strategies in self.profile_dict.items()]
        return SampleGame(g_roles, g_players, g_strategies, g_payoff_data)