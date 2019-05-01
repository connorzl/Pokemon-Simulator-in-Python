#!/usr/bin/env python3

# --------------
# The state of the graph only takes HP into consideration (no stats yet)
# --------------

import numpy as np
import CONSTANTS
import Attack
from heapdict import heapdict
from Pokemon import Pokemon
from copy import deepcopy

class PokemonGraph(object):
    # A data structure for storing graph generated for Pokemon battle
    # Each state is ((Team1 Pokemon1 HP, Team1 Pokemon2 HP, Team1 Pokemon3 HP, Team1 Pokemon4 HP, Team1 active Pokemon Number),
    #                (Team2 Pokemon1 HP, Team2 Pokemon2 HP, Team2 Pokemon3 HP, Team2 Pokemon4 HP, Team2 active Pokemon Number),
    #                 whoseTurn (0 for team1, 1 for team2))

    # Initialize the graph object to have a graph with the start node (state with initial team settings) and the neighbors of the start node
    def __init__(self, team1Pokemons, team2Pokemons, team1ActivatePokemonNum, team2ActivatePokemonNum, whoseTurn):
        self.team1Pokemons = team1Pokemons
        self.team2Pokemons = team2Pokemons # By default, team2 is AI's team
        self.pokemons = (team1Pokemons, team2Pokemons)
        activePokemons = (team1ActivatePokemonNum, team2ActivatePokemonNum)
        currentState1 = np.zeros(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER+1, dtype=int) # 4 for now
        currentState2 = np.zeros(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER+1, dtype=int) # 4 for now
        
        for i in range(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER):
            currentState1[i] = team1Pokemons[i].getHP() # This is getting the BASE HP for initialization, not battle HP
            currentState2[i] = team2Pokemons[i].getHP()

        currentState1[-1] = team1ActivatePokemonNum
        currentState2[-1] = team2ActivatePokemonNum

        currentState = (tuple(currentState1), tuple(currentState2), whoseTurn)

        self.initialState = deepcopy(currentState)

        # # Total out edge = 4(moves of current pokemon) + numPokemonAlive(switches to the rest alive pokemon)
        # nextStates = [0]*(4 + CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER-1)
        #
        # for i in range(4 + CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER-1):
        #     whoseNextTurn = int(1-whoseTurn)
        #     damageList = [Attack.calculateDamage(self.pokemons[whoseTurn][activePokemons[whoseTurn]].getMove1().getName(),
        #                                          self.pokemons[whoseTurn][activePokemons[whoseTurn]],
        #                                          self.pokemons[whoseNextTurn][activePokemons[whoseNextTurn]]),
        #                   Attack.calculateDamage(self.pokemons[whoseTurn][activePokemons[whoseTurn]].getMove2().getName(),
        #                                          self.pokemons[whoseTurn][activePokemons[whoseTurn]],
        #                                          self.pokemons[whoseNextTurn][activePokemons[whoseNextTurn]]),
        #                   Attack.calculateDamage(self.pokemons[whoseTurn][activePokemons[whoseTurn]].getMove3().getName(),
        #                                          self.pokemons[whoseTurn][activePokemons[whoseTurn]],
        #                                          self.pokemons[whoseNextTurn][activePokemons[whoseNextTurn]]),
        #                   Attack.calculateDamage(self.pokemons[whoseTurn][activePokemons[whoseTurn]].getMove4().getName(),
        #                                          self.pokemons[whoseTurn][activePokemons[whoseTurn]],
        #                                          self.pokemons[whoseNextTurn][activePokemons[whoseNextTurn]])]
        #
        #     # Create next states for the cases when current team chooses a move
        #     for j in range(4):
        #         modifiedOtherTeamState = list(deepcopy(currentState[whoseNextTurn]))
        #         modifiedOtherTeamState[activePokemons[whoseNextTurn]] = max(0, modifiedOtherTeamState[activePokemons[whoseNextTurn]] - damageList[j])  # Set the new HP of the pokemon being attacked
        #         nextStates[j] = [0]*3
        #         nextStates[j][whoseNextTurn] = modifiedOtherTeamState
        #         nextStates[j][whoseTurn] = currentState[whoseTurn]
        #         nextStates[j][2] = whoseNextTurn
        #
        #     # Create next states for the cases when current team switches to another pokemon
        #     pokemonToSwitch = list(range(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER))
        #     pokemonToSwitch.remove(activePokemons[whoseTurn])
        #     for j in range(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER - 1):
        #         pokemonToSwitchChosen = pokemonToSwitch[j]
        #         modifiedCurrentTeamState = list(deepcopy(currentState[whoseTurn]))
        #         modifiedCurrentTeamState[-1] = pokemonToSwitchChosen
        #         nextStates[4 + j] = [0]*3
        #         nextStates[4 + j][whoseNextTurn] = currentState[whoseNextTurn]
        #         nextStates[4 + j][whoseTurn] = modifiedCurrentTeamState
        #         nextStates[4 + j][2] = whoseNextTurn

        self.pokemonGraph = {}

    def get_graph(self):
        return self.pokemonGraph

    def get_initial_state(self):
        return self.initialState

    def end_term_process(self, nextStates):
        modifiedStates = np.array(deepcopy(nextStates))

        for i in range(len(nextStates)):
            state = np.array(nextStates[i])
            modifiedState = deepcopy(state)
            player1Active = state[0][-1]
            player2Active = state[1][-1]
            # Active pokemon loses 5% max HP
            player1ActiveHP = state[0][player1Active]
            player2ActiveHP = state[1][player2Active]
            player1ActiveHP -= 0.05 * self.team1Pokemons[player1Active].getHP()
            player2ActiveHP -= 0.05 * self.team2Pokemons[player2Active].getHP()

            # if any player's active pokemon dies due to this, automatically switch to first available
            if player1ActiveHP <= 0:
                modifiedState[0] = np.array(modifiedState[0])
                modifiedState[1] = np.array(modifiedState[1])
                modifiedState[0][player1Active] = 0
                switchTo = -1
                for j in range(4):
                    if modifiedState[0][j] > 0:
                        modifiedState[0][-1] = j
                        switchTo = j
                        break
                modifiedState[0] = tuple(modifiedState[0])
                modifiedState[1] = tuple(modifiedState[1])
                modifiedStates[i] = tuple(modifiedState)
                #print("Player 1's active pokemon {0} dies due to end of turn. Switched to {1}".format(player1Active,
                                                                                                      #switchTo))

            if player2ActiveHP <= 0:
                modifiedState = np.array(modifiedState)
                modifiedState[0] = np.array(modifiedState[0])
                modifiedState[1] = np.array(modifiedState[1])
                modifiedState[1][player2Active] = 0
                switchTo = -1
                for j in range(4):
                    if modifiedState[1][j] > 0:
                        modifiedState[1][-1] = j
                        switchTo = j
                        break
                modifiedState[0] = tuple(modifiedState[0])
                modifiedState[1] = tuple(modifiedState[1])
                modifiedStates[i] = tuple(modifiedState)
                #print("Player 2's active pokemon {0} dies due to end of turn. Switched to {1}".format(player2Active, switchTo))
        newModifiedStates = []
        for i in range(len(modifiedStates)):
            tmp = tuple(modifiedStates[i])
            newModifiedStates.append(tmp)
        modifiedStates = tuple(newModifiedStates)
        return modifiedStates


    # Add neighbors of the given state to the graph. Return the new states added
    # Make sure stateToExpand is passed in as tuple
    def expand_state(self, stateToExpand):
        if stateToExpand in self.pokemonGraph:
            return ()
        whoseTurn = stateToExpand[-1]
        whoseNextTurn = int(1-whoseTurn)
        activePokemons = (stateToExpand[0][-1], stateToExpand[1][-1])

        # If the current move pokemon is alive, total out edge = 4(moves of current pokemon) + numPokemonAlive(switches to the rest alive pokemon)
        if stateToExpand[whoseTurn][activePokemons[whoseTurn]] > 0:
            nextStates = [0]*(4 + CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER - 1)

            for i in range(4 + CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER - 1):
                damageList = [
                    Attack.calculateDamage(self.pokemons[whoseTurn][activePokemons[whoseTurn]].getMove1().getName(),
                                           self.pokemons[whoseTurn][activePokemons[whoseTurn]],
                                           self.pokemons[whoseNextTurn][activePokemons[whoseNextTurn]]),
                    Attack.calculateDamage(self.pokemons[whoseTurn][activePokemons[whoseTurn]].getMove2().getName(),
                                           self.pokemons[whoseTurn][activePokemons[whoseTurn]],
                                           self.pokemons[whoseNextTurn][activePokemons[whoseNextTurn]]),
                    Attack.calculateDamage(self.pokemons[whoseTurn][activePokemons[whoseTurn]].getMove3().getName(),
                                           self.pokemons[whoseTurn][activePokemons[whoseTurn]],
                                           self.pokemons[whoseNextTurn][activePokemons[whoseNextTurn]]),
                    Attack.calculateDamage(self.pokemons[whoseTurn][activePokemons[whoseTurn]].getMove4().getName(),
                                           self.pokemons[whoseTurn][activePokemons[whoseTurn]],
                                           self.pokemons[whoseNextTurn][activePokemons[whoseNextTurn]])]

                # Create next states for the cases when current team chooses a move
                for j in range(4):
                    modifiedOtherTeamState = list(deepcopy(stateToExpand[whoseNextTurn]))
                    modifiedOtherTeamState[activePokemons[whoseNextTurn]] = max(0, modifiedOtherTeamState[activePokemons[whoseNextTurn]] - damageList[j])  # Set the new HP of the pokemon being attacked
                    nextStates[j] = [0]*3
                    nextStates[j][whoseNextTurn] = tuple(modifiedOtherTeamState)
                    nextStates[j][whoseTurn] = stateToExpand[whoseTurn]
                    nextStates[j][2] = whoseNextTurn
                    nextStates[j] = tuple(nextStates[j])

                # Create next states for the cases when current team switches to another ALIVE pokemon
                pokemonToSwitch = list(range(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER))
                for pokemonNum in range(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER):
                    if pokemonNum == activePokemons[whoseTurn] or (stateToExpand[whoseTurn][pokemonNum] == 0):
                        pokemonToSwitch.remove(pokemonNum)
                extraCount = 0
                for j in range(len(pokemonToSwitch)):
                    pokemonToSwitchChosen = pokemonToSwitch[j]
                    modifiedCurrentTeamState = list(deepcopy(stateToExpand[whoseTurn]))
                    modifiedCurrentTeamState[-1] = pokemonToSwitchChosen
                    nextStates[4 + j] = [0]*3
                    nextStates[4 + j][whoseNextTurn] = stateToExpand[whoseNextTurn]
                    nextStates[4 + j][whoseTurn] = tuple(modifiedCurrentTeamState)
                    nextStates[4 + j][2] = whoseNextTurn
                    nextStates[4 + j] = tuple(nextStates[4 + j])
                    extraCount += 1

            nextStates = nextStates[:4+extraCount]

            # if player 2 (AI)'s turn has finished, every player's active pokemon loses 5% max HP
            if whoseTurn == 1:
                processedNextStates = self.end_term_process(nextStates)
                nextStates = processedNextStates
            nextStates = tuple(nextStates)
            self.pokemonGraph[stateToExpand] = nextStates
            return nextStates

        # If the current move pokemon is dead, total out edge = numPokemonAlive(switches to the rest alive pokemon)
        else:
            nextStates = [0]*(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER - 1)

            # Create next states for the cases when current team switches to another ALIVE pokemon
            pokemonToSwitch = list(range(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER))
            for pokemonNum in range(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER):
                if pokemonNum == activePokemons[whoseTurn] or (stateToExpand[whoseTurn][pokemonNum] == 0):
                    pokemonToSwitch.remove(pokemonNum)

            # If all dead, return nothing
            if len(pokemonToSwitch) == 0:
                print("player {}'s pokemons all dead!".format(whoseTurn))
                return (["dead"])

            extraCount = 0
            for j in range(len(pokemonToSwitch)):
                pokemonToSwitchChosen = pokemonToSwitch[j]
                modifiedCurrentTeamState = list(deepcopy(stateToExpand[whoseTurn]))
                modifiedCurrentTeamState[-1] = pokemonToSwitchChosen
                nextStates[j] = [0]*3
                nextStates[j][whoseNextTurn] = stateToExpand[whoseNextTurn]
                nextStates[j][whoseTurn] = tuple(modifiedCurrentTeamState)
                nextStates[j][2] = whoseNextTurn
                nextStates[j] = tuple(nextStates[j])
                extraCount += 1

            nextStates = nextStates[:extraCount]

            # if player 2 (AI)'s turn has finished, every player's active pokemon loses 5% max HP
            if whoseTurn == 1:
                processedNextStates = self.end_term_process(nextStates)
                nextStates = processedNextStates
            nextStates = tuple(nextStates)
            self.pokemonGraph[stateToExpand] = nextStates
            return nextStates

def main(team1Pokemons, team2Pokemons, team1ActivatePokemonNum, team2ActivatePokemonNum, whoseTurn):
    pokemonGraph = PokemonGraph(team1Pokemons, team2Pokemons, team1ActivatePokemonNum, team2ActivatePokemonNum, whoseTurn)
    initialGraph = pokemonGraph.get_graph()
    initialState = pokemonGraph.get_initial_state()
    heap = heapdict()
    count = 0
    heap[count] = (count,[initialState])
    count += 1
    while len(heap) != 0:
        print(len(heap))
        if (len(heap) == 34337):
            print("here")
        popCount1, (popCount2, popStates) = heap.popitem()

        for popState in popStates:
            nextStates = pokemonGraph.expand_state(popState)
            if len(nextStates) == 1:
                print("One possible end")
                np.savez("/Volumes/U/graphs/pokemon_graph_dead_{}.npz".format(str(popCount1)), team1Pokemons=team1Pokemons,
                        team2Pokemons=team2Pokemons, team1ActivatePokemonNum=team1ActivatePokemonNum,
                        team2ActivatePokemonNum=team2ActivatePokemonNum, whoseTurn=whoseTurn, pokemonGraph=pokemonGraph)
                continue
            if len(nextStates) == 0:
                continue
            heap[count] = (count, nextStates)
            count += 1


    print("Graph is built!")
    np.save("pokemon_graph.npz", team1Pokemons=team1Pokemons,
            team2Pokemons=team2Pokemons, team1ActivatePokemonNum=team1ActivatePokemonNum,
            team2ActivatePokemonNum=team2ActivatePokemonNum, whoseTurn=whoseTurn, pokemonGraph=pokemonGraph)

team1PokemonNames = ["moltres","squirtle","bulbasaur","pikachu"]
team1ActivatePokemonNum = 0
team2PokemonNames = ["beedrill","rattata","pidgey","caterpie"]

# Check if the entered data conflicts with the macros
if not len(team1PokemonNames) == len(team2PokemonNames):
    raise Exception('team1 has size {}, team2 has size {}, mismatch'.format(len(team1PokemonNames), len(team2PokemonNames)))

if not len(team1PokemonNames) == CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER:
    raise Exception('Macro has size {}, team has size {}, mismatch'.format(CONSTANTS.Constants.NUM_POKEMON_PER_PLAYER, len(team1PokemonNames)))

team2ActivatePokemonNum = 0
whoseTurn = 0

team1Pokemons = []
team2Pokemons = []
for i in range(len(team1PokemonNames)):
    team1Pokemons.append(Pokemon(team1PokemonNames[i]))
    team2Pokemons.append(Pokemon(team2PokemonNames[i]))

main(team1Pokemons, team2Pokemons, team1ActivatePokemonNum, team2ActivatePokemonNum, whoseTurn)