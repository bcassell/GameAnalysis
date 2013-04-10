from RoleSymmetricGame import Profile, PayoffData, SampleGame
import BasicFunctions

from hashlib import sha1

from numpy import all, array, uint8

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
    
class Hashable(object):
    '''Hashable wrapper for ndarray objects.

        Instances of ndarray are not hashable, meaning they cannot be added to
        sets, nor used as keys in dictionaries. This is by design - ndarray
        objects are mutable, and therefore cannot reliably implement the
        __hash__() method.

        The hashable class allows a way around this limitation. It implements
        the required methods for hashable objects in terms of an encapsulated
        ndarray object. This can be either a copied instance (which is safer)
        or the original object (which requires the user to be careful enough
        not to modify it).
    '''
    def __init__(self, wrapped, tight=False):
        '''Creates a new hashable object encapsulating an ndarray.

            wrapped
                The wrapped ndarray.

            tight
                Optional. If True, a copy of the input ndaray is created.
                Defaults to False.
        '''
        self.__tight = tight
        self.__wrapped = array(wrapped) if tight else wrapped
        self.__hash = int(sha1(wrapped.view(uint8)).hexdigest(), 16)

    def __eq__(self, other):
        return all(self.__wrapped == other.__wrapped)

    def __hash__(self):
        return self.__hash

    def unwrap(self):
        '''Returns the encapsulated ndarray.

            If the wrapper is "tight", a copy of the encapsulated ndarray is
            returned. Otherwise, the encapsulated ndarray itself is returned.
        '''
        if self.__tight:
            return array(self.__wrapped)

        return self.__wrapped
    