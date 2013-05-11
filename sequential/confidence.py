import Bootstrap
import Regret

class BootstrapConfidenceInterval:
    def __init__(self, bootstrap_method=Bootstrap.bootstrap):
        self.bootstrap_method = bootstrap_method

    def one_sided_interval(self, matrix, profile, alpha=0.95):
        samples = self.bootstrap_method(matrix.toGame(), profile, Regret.regret, "resample", ["game"])
        return samples[int(len(samples)*alpha)-1]

    def two_sided_interval(self, matrix, profile, alpha=0.95):
        alpha1 = (1.0-alpha)/2.0
        alpha2 = 1.0-alpha1
        samples = self.bootstrap_method(matrix.toGame(), profile, Regret.regret, "resample", ["game"])
        return [samples[int(len(samples)*alpha1)], samples[int(len(samples)*alpha2)-1]]