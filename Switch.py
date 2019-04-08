from Action import Action

class Switch(Action):
    def __init__(self, pokemonIndex):
        super().__init__("switch")
        self.pokemonToSwitch = pokemonIndex

    def getPokemon(self):
        return self.pokemonToSwitch