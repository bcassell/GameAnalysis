from sequential.data import ObservationMatrix, PayoffData, Profile
from sequential.stopping_rules import EquilibriumCompareEvaluator, StandardErrorEvaluator, ConfidenceIntervalEvaluator, Nash, Regret
from factories.GameFactory import create_observation_matrix
from numpy import array
from numpy.testing import assert_array_almost_equal


class describe_equilibrium_compare_evaluator:
    Regret.regret = lambda game, profile: 0
    
    def it_requests_further_sampling_when_given_an_empty_matrix(self):
        evaluator = EquilibriumCompareEvaluator(0.01)
        assert evaluator.continue_sampling(ObservationMatrix())
    
    def it_requests_further_sampling_when_there_is_data_but_no_old_equilibria(self):
        Nash.replicator_dynamics = lambda g, mix, iters, converge_threshold: array([0.1, 0.9])
        matrix = create_observation_matrix()
        evaluator = EquilibriumCompareEvaluator(0.01)
        assert evaluator.continue_sampling(matrix) == True
        assert_array_almost_equal(evaluator.old_equilibria[0], array([0.1, 0.9]))
    
    def it_requests_further_sampling_when_the_new_equilibrium_is_distant(self):
        Nash.replicator_dynamics = lambda g, mix, iters, converge_threshold: array([0.1, 0.9])
        matrix = create_observation_matrix()
        evaluator = EquilibriumCompareEvaluator(0.01)
        evaluator.old_equilibria = [array([0.5, 0.5])]
        assert evaluator.continue_sampling(matrix) == True
        
    def it_stops_sampling_when_the_new_equilibria_are_all_similar(self):
        Nash.replicator_dynamics = lambda g, mix, iters, converge_threshold: \
                array([0.110001, 0.899999]) if list(mix) == [0.11, 0.89] else array([0.9999, 0.0001])
        matrix = create_observation_matrix()
        evaluator = EquilibriumCompareEvaluator(0.05)
        evaluator.old_equilibria = [array([0.11, 0.89]), array([1.0, 0.0])]
        assert evaluator.continue_sampling(matrix) == False

    def it_requests_further_sampling_when_new_equilibria_are_found(self):
        Nash.replicator_dynamics = lambda g, mix, iters, converge_threshold: \
                array([0.1, 0.9]) if mix is array([0.11, 0.89]) else array([0.999, 0.001])
        matrix = create_observation_matrix()
        evaluator = EquilibriumCompareEvaluator(0.05)
        evaluator.old_equilibria = [array([0.11, 0.89])]
        assert evaluator.continue_sampling(matrix) == True
        for eq in evaluator.old_equilibria:
            assert [[0.1, 0.9], [0.999, 0.001]].count(list(eq)) == 1
        
class describe_standard_error_evaluator:
    def it_requests_sampling_when_given_an_empty_observation_matrix(self):
        matrix = ObservationMatrix()
        target_profile = Profile({'All': {'A': 2}})
        evaluator = StandardErrorEvaluator(1, [target_profile])
        assert evaluator.continue_sampling(matrix) == True
    
    def it_requests_sampling_when_profiles_in_target_set_have_too_much_variation_in_payoffs(self):
        matrix = ObservationMatrix()
        target_profile = Profile({'All': {'A': 2}})
        matrix.addObservations(target_profile, {'All': [PayoffData('A', 2, [10, 20, 45])]})
        evaluator = StandardErrorEvaluator(1, [target_profile])
        assert evaluator.continue_sampling(matrix) == True

    def it_does_not_request_sampling_when_profiles_in_target_set_do_not_have_too_much_variation_in_payoff(self):
        matrix = ObservationMatrix()
        target_profile = Profile({'All': {'A': 2}})
        matrix.addObservations(target_profile, {'All': [PayoffData('A', 2, [10, 10.1, 9.9])]})
        evaluator = StandardErrorEvaluator(1, [target_profile])
        assert evaluator.continue_sampling(matrix) == False        

    def it_does_not_request_sampling_when_only_profiles_outside_target_set_have_too_much_variation_in_payoffs(self):
        matrix = ObservationMatrix()
        target_profile = Profile({'All': {'A': 2}})
        non_target_profile = Profile({'All': {'B': 2}})
        matrix.addObservations(target_profile, {'All': [PayoffData('A', 2, [10, 10.1, 10.2])]})
        matrix.addObservations(non_target_profile, {'All': [PayoffData('B', 2, [10, 20, 45])]})
        evaluator = StandardErrorEvaluator(1, [target_profile])
        assert evaluator.continue_sampling(matrix) == False

class describe_confidence_interval_evaluator:
    def it_requests_sampling_when_given_an_empty_observation_matrix(self):
        matrix = ObservationMatrix()
        evaluator = ConfidenceIntervalEvaluator([], 0.5, None)
        assert evaluator.continue_sampling(matrix) == True
        
    def it_requests_sampling_when_delta_is_in_interval(self):
        class FakeCI:
            def regret_confidence_interval(self, matrix, profile):
                return [0.0, 1.0]
            
        ci_calculator = FakeCI()
        matrix = create_observation_matrix()
        evaluator = ConfidenceIntervalEvaluator(matrix.knownProfiles(), 0.5, ci_calculator)
        assert evaluator.continue_sampling(matrix) == True
        
    def it_does_not_request_sampling_when_delta_is_outside_all_intervals(self):
        class FakeCI:
            def __init__(self):
                self.count = 0
                
            def regret_confidence_interval(self, matrix, profile):
                self.count += 1
                if self.count % 2 == 0:
                    return [0.6, 1.0]
                else:
                    return [0.0, 0.4]

        ci_calculator = FakeCI()        
        matrix = create_observation_matrix()
        evaluator = ConfidenceIntervalEvaluator(matrix.knownProfiles(), 0.5, ci_calculator)
        assert evaluator.continue_sampling(matrix) == False
    
    def it_tracks_whether_or_not_a_profile_is_a_delta_nash(self):
        class FakeCI:
            def __init__(self):
                self.count = 0
                
            def regret_confidence_interval(self, matrix, profile):
                self.count += 1
                if self.count % 2 == 0:
                    return [0.6, 1.0]
                else:
                    return [0.0, 0.4]
        
        ci_calculator = FakeCI()        
        matrix = create_observation_matrix()
        evaluator = ConfidenceIntervalEvaluator(matrix.knownProfiles(), 0.5, ci_calculator)
        evaluator.continue_sampling(matrix)
        count = 0
        print evaluator.target_set.items()
        for result in evaluator.target_set.values():
            count += 1
            if count % 2 == 0:
                assert result == "No"
            else:
                assert result == "Yes"