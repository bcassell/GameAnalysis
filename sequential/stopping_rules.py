from scipy.stats import stats
from numpy import linalg
import numpy as np
import Nash
import Regret
from data import Hashable

class StandardErrorEvaluator:
    def __init__(self, standard_err_threshold, target_set):
        self.standard_err_threshold = standard_err_threshold
        self.target_set = target_set
        
    def continue_sampling(self, matrix):
        self.matrix = matrix
        print 'more sampling'
        if matrix.profile_dict == {}:
            return True
        for profile in self.target_set:
            for role, strategies in profile.items():
                for strategy in strategies.keys():
                    if stats.sem(matrix.getPayoffData(profile, role, strategy)) >= self.standard_err_threshold:
                        return True
        return False
    
    def equilibria(self):
        return Nash.mixed_nash(self.matrix.toGame())

class EquilibriumCompareEvaluator:
    def __init__(self, compare_threshold, regret_threshold=1e-4, dist_threshold=None, 
                 random_restarts=0, iters=10000, converge_threshold=1e-8):
        self.compare_threshold = compare_threshold
        self.regret_threshold = regret_threshold
        self.dist_threshold = dist_threshold or compare_threshold/2.0
        self.random_restarts = random_restarts
        self.iters = iters
        self.converge_threshold = converge_threshold
        self.old_equilibria = []
        
    def continue_sampling(self, matrix):
        if matrix.profile_dict == {}:
            return True
        game = matrix.toGame()
        decision = False
        equilibria = []
        all_eq = []
        print decision
        print 'comparing old equilibria'
        for old_eq in self.old_equilibria:
            new_eq = Nash.replicator_dynamics(game, old_eq, self.iters, self.converge_threshold)
            decision = decision or linalg.norm(new_eq-old_eq, 2) > self.compare_threshold
            print decision
            distances = map(lambda e: linalg.norm(e-new_eq, 2), equilibria)
            if Regret.regret(game, new_eq) <= self.regret_threshold and \
                    all([d >= self.dist_threshold for d in distances]):
                equilibria.append(new_eq)
            all_eq.append(new_eq)
        print 'testing for new equilibria'
        for m in game.biasedMixtures() + [game.uniformMixture()] + \
                [game.randomMixture() for __ in range(self.random_restarts)]:
            eq = Nash.replicator_dynamics(game, m, self.iters, self.converge_threshold)
            distances = map(lambda e: linalg.norm(e-eq,2), equilibria)
            if Regret.regret(game, eq) <= self.regret_threshold and \
                    all([d >= self.dist_threshold for d in distances]):
                equilibria.append(eq)
                decision = True
                print decision
            all_eq.append(eq)
        print 'testing that some equilibria were found'
        if len(equilibria) == 0:
            decision = True
            print decision
            self.old_equilibria = [min(all_eq, key=lambda e: Regret.regret(game, e))]
        else:
            if len(self.old_equilibria) == 0:
                decision = True
            self.old_equilibria = equilibria
        print 'Final:', decision
        return decision
    
    def equilibria(self):
        return self.old_equilibria
    

class EquilibriumConfidenceEvaluator:
    def __init__(self, delta, alpha, confidence_interval_calculator, random_restarts=0, iters=10000, converge_threshold=1e-8):
        self.delta = delta
        self.alpha = alpha
        self.ci_calculator = confidence_interval_calculator
        self.eq = []
        self.random_restarts = random_restarts
        self.iters = iters
        self.converge_threshold = converge_threshold
        
    def continue_sampling(self, matrix):
        if matrix.profile_dict == {}:
            return True
        game = matrix.toGame()
        decision = True
        for m in game.biasedMixtures() + [game.uniformMixture()] + \
                [game.randomMixture() for __ in range(self.random_restarts)]:
            eq = Nash.replicator_dynamics(game, m, self.iters, self.converge_threshold)
            confidence_interval = self.ci_calculator.one_sided_interval(matrix, eq, self.alpha)
            if confidence_interval < self.delta:
                self.eq.append(eq)
                decision = False
        return decision
    
    def equilibria(self):
        return self.eq

class ConfidenceIntervalEvaluator:
    def __init__(self, game, target_set, delta, alpha, confidence_interval_calculator):
        self.target_set = target_set
        self.target_hash = {}
        for profile in target_set:
            if type(profile) is np.ndarray:
                self.target_hash[self._convert_profile(profile)] = "Undetermined"
            else:
                self.target_hash[profile] = "Undetermined"
        self.delta = delta
        self.alpha = alpha
        self.ci_calculator = confidence_interval_calculator
        
    def continue_sampling(self, matrix):
        if matrix.profile_dict == {}:
            return True
        flag = False
        for profile in self.target_hash.keys():
            self.confidence_interval = self.ci_calculator.two_sided_interval(matrix, self._interval_input(profile), self.alpha)
            if self.delta >= self.confidence_interval[0]:
                if self.delta > self.confidence_interval[1]:
                    self.target_hash[profile] = "Yes"
                else:
                    self.target_hash[profile] = "Undetermined"
                    flag = True
            else:
                self.target_hash[profile] = "No"
        return flag

    def get_decision(self, matrix, profile):
        return self.target_hash[self._convert_profile(profile)]


    def _convert_profile(self, profile):
        if type(profile) is np.ndarray:
            return Hashable(profile, True)
        return profile
    
    def _interval_input(self, profile):
        if type(profile) is Hashable:
            return profile.unwrap()
        else:
            return profile

class BestEffortCIEvaluator(ConfidenceIntervalEvaluator):
    def get_decision(self, matrix, profile):
        if self.target_hash[self._convert_profile(profile)] == "Undetermined":
            if self.ci_calculator.one_sided_interval(matrix, self._interval_input(profile), 0.5) < self.delta:
                return "Undetermined-Yes"
            else:
                return "Undetermined-No"
        else:
            return self.target_hash[self._convert_profile(profile)]

                