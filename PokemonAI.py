from Attack import *
import numpy as np
from CONSTANTS import Constants
from Switch import Switch

class PokemonAI(object):
    def __init__(self, currentPokemon, pokemons):
        self.pokemons = pokemons
        self.currentPokemon = currentPokemon

    def selectNextAction(self, playerCurrentPokemon):
        # Want to select the edge that has min cost
        # Cost(action) = max damage could receive in current round + -(max damage could give in current round)

        # Total out edge = 4(moves of current pokemon) + numPokemonAlive(switches to the rest alive pokemon)
        numRemainingAlivePokemon = 0
        remainingAliveIndexList = []
        for pokemonNum in range(Constants.NUM_POKEMON_PER_PLAYER):
            if self.pokemons[pokemonNum] != self.currentPokemon:
                if self.pokemons[pokemonNum].isAlive():
                    numRemainingAlivePokemon += 1
                    remainingAliveIndexList.append(pokemonNum)

        costList = np.zeros(4 + numRemainingAlivePokemon)

        # Calculate what is the max damage AI could receive
        damageReceivedList = np.array([calculateDamage(playerCurrentPokemon.getMove1().getName(), playerCurrentPokemon, self.currentPokemon),
                              calculateDamage(playerCurrentPokemon.getMove2().getName(), playerCurrentPokemon, self.currentPokemon),
                              calculateDamage(playerCurrentPokemon.getMove3().getName(), playerCurrentPokemon, self.currentPokemon),
                              calculateDamage(playerCurrentPokemon.getMove4().getName(), playerCurrentPokemon, self.currentPokemon)])
        maxDamageReceived = np.max(damageReceivedList)
        maxDamageReceived = np.ones(4)*maxDamageReceived

        # Calculate what is the max damage the AI can do
        damageGiveList = np.array([calculateDamage(self.currentPokemon.getMove1().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove2().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove3().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove4().getName(), self.currentPokemon, playerCurrentPokemon)])

        costList[:4] = maxDamageReceived - damageGiveList # (4,)

        damageReceivedSwitchList = np.zeros(numRemainingAlivePokemon)
        indexInCostList = 4
        for index in remainingAliveIndexList:
            pokemonToSwitch = self.pokemons[index]
            damageReceivedList = np.array(
                                [calculateDamage(playerCurrentPokemon.getMove1().getName(), playerCurrentPokemon, pokemonToSwitch),
                                 calculateDamage(playerCurrentPokemon.getMove2().getName(), playerCurrentPokemon, pokemonToSwitch),
                                 calculateDamage(playerCurrentPokemon.getMove3().getName(), playerCurrentPokemon, pokemonToSwitch),
                                 calculateDamage(playerCurrentPokemon.getMove4().getName(), playerCurrentPokemon, pokemonToSwitch)])
            maxDamageReceived = np.max(damageReceivedList)
            costList[indexInCostList] = maxDamageReceived
            indexInCostList+=1

        # Select the min cost edge
        minEdgeIndex = np.argmin(costList)
        if minEdgeIndex <= 3: # If the best action is one of the current pokemon moves
            moveOptions = [self.currentPokemon.getMove1(), self.currentPokemon.getMove2(), self.currentPokemon.getMove3(), self.currentPokemon.getMove4()]
            return moveOptions[minEdgeIndex]
        else: # If the best action is switching
            offset = minEdgeIndex - 4
            pokemonToSwitchIndex = remainingAliveIndexList[offset]
            self.currentPokemon = self.pokemons[pokemonToSwitchIndex]
            return Switch(pokemonToSwitchIndex)

    def forceSwitch(self, pokemonIndex):
        self.currentPokemon = self.pokemons[pokemonIndex]