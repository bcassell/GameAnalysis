from factories.GameFactory import create_symmetric_game
from RoleSymmetricGame import Profile

class describe_game:
    def it_can_be_converted_to_asymmetric(self):
        game = create_symmetric_game()
        asym_game = game.to_asymmetric_game()
        assert asym_game.roles == ["p"+str(i) for i in range(sum([c for c in game.players.values()]))]
        for role in asym_game.roles:
            assert asym_game.strategies[role] == game.strategies['All']
        assert asym_game.getPayoffData(Profile({"p0": {"C": 1}, "p1": {"D": 1}}), "p0", "C") == game.getPayoffData(
                Profile({"All": {"C": 1, "D": 1}}), "All", "C")
        assert asym_game.getPayoffData(Profile({"p0": {"C": 1}, "p1": {"D": 1}}), "p0", "C") == asym_game.getPayoffData(
                Profile({"p0": {"D": 1}, "p1": {"C": 1}}), "p1", "C")