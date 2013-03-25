from sequential.confidence import BootstrapConfidenceInterval
import tests.factories.GameFactory as Factory

class describe_bootstrap_confidence_interval:
    def it_provides_a_one_sided_confidence_interval(self):
        bootstrap_method = lambda *args: [i+1 for i in range(100)]
        ci = BootstrapConfidenceInterval(bootstrap_method)
        assert ci.one_sided_interval(Factory.create_observation_matrix(), "fake profile", 0.95) == 95
    
    def it_provides_a_two_sided_confidence_interval(self):
        bootstrap_method = lambda *args: [i+1 for i in range(100)]
        ci = BootstrapConfidenceInterval(bootstrap_method)
        print ci.two_sided_interval(Factory.create_observation_matrix(), "fake profile", 0.90)
        assert ci.two_sided_interval(Factory.create_observation_matrix(), "fake profile", 0.95) == [3, 97]