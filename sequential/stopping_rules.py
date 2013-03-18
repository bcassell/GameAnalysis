from scipy.stats import stats
from numpy import linalg
import Nash
import Regret

class StandardErrorEvaluator:
    def __init__(self, standard_err_threshold, target_set):
        self.standard_err_threshold = standard_err_threshold
        self.target_set = target_set
        
    def continue_sampling(self, matrix):
        print 'more sampling'
        if matrix.profile_dict == {}:
            return True
        for profile in self.target_set:
            for role, strategies in profile.items():
                for strategy in strategies.keys():
                    if stats.sem(matrix.getPayoffData(profile, role, strategy)) >= self.standard_err_threshold:
                        return True
        return False

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
        for old_eq in self.old_equilibria:
            new_eq = Nash.replicator_dynamics(game, old_eq, self.iters, self.converge_threshold)
            decision = decision or linalg.norm(new_eq-old_eq, 2) > self.compare_threshold
            distances = map(lambda e: linalg.norm(e-new_eq, 2), equilibria)
            if Regret.regret(game, new_eq) <= self.regret_threshold and \
                    all([d >= self.dist_threshold for d in distances]):
                equilibria.append(new_eq)
            all_eq.append(new_eq)
        for m in game.biasedMixtures() + [game.uniformMixture()] + \
                [game.randomMixture() for __ in range(self.random_restarts)]:
            eq = Nash.replicator_dynamics(game, m, self.iters, self.converge_threshold)
            distances = map(lambda e: linalg.norm(e-eq,2), equilibria)
            if Regret.regret(game, eq) <= self.regret_threshold and \
                    all([d >= self.dist_threshold for d in distances]):
                equilibria.append(eq)
                decision = True
            all_eq.append(eq)
        if len(equilibria) == 0:
            decision = True
            self.old_equilibria = [min(all_eq, key=lambda e: Regret.regret(game, e))]
        else:
            self.old_equilibria = equilibria
        return decision

class ConfidenceIntervalEvaluator:
    def __init__(self, target_set, delta, confidence_interval_calculator):
        self.target_set = {profile: "Undetermined" for profile in target_set}
        self.delta = delta
        self.ci_calculator = confidence_interval_calculator
        
    def continue_sampling(self, matrix):
        if matrix.profile_dict == {}:
            return True
        flag = False
        for profile in self.target_set.keys():
            print profile
            confidence_interval = self.ci_calculator.regret_confidence_interval(matrix, profile)
            print confidence_interval
            if self.delta >= confidence_interval[0]:
                if self.delta > confidence_interval[1]:
                    self.target_set[profile] = "Yes"
                else:
                    self.target_set[profile] = "Undetermined"
                    flag = True
            else:
                self.target_set[profile] = "No"
        return flag