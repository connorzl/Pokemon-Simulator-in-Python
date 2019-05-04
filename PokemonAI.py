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

    def selectNextActionDefensive(self, playerCurrentPokemon):
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

        costList = np.zeros(1 + numRemainingAlivePokemon)

        currTotalHP = 0
        for pokemonNum in range(Constants.NUM_POKEMON_PER_PLAYER):
            if self.pokemons[pokemonNum].isAlive():
                currTotalHP += self.pokemons[pokemonNum].getBattleHP()

        # Calculate what is the max damage AI could receive
        damageReceivedList = np.array([calculateDamage(playerCurrentPokemon.getMove1().getName(), playerCurrentPokemon, self.currentPokemon),
                              calculateDamage(playerCurrentPokemon.getMove2().getName(), playerCurrentPokemon, self.currentPokemon),
                              calculateDamage(playerCurrentPokemon.getMove3().getName(), playerCurrentPokemon, self.currentPokemon),
                              calculateDamage(playerCurrentPokemon.getMove4().getName(), playerCurrentPokemon, self.currentPokemon)])
        for i in range(0, len(damageReceivedList)):
            damageReceivedList[i] = min(damageReceivedList[i], self.currentPokemon.getBattleHP())
        maxDamageReceived = np.max(damageReceivedList)
        
        g = maxDamageReceived

        maxHeuristicCurr = 0
        # compute heuristic
        for aiPoke in self.pokemons:
            if not(aiPoke.isAlive()):
                continue

            heuristic = 0
            for oppPoke in allPlayerPokemon:
                if not(oppPoke.isAlive()):
                    continue

                # Calculate what is the max damage the AI can do
                damageGiveList = np.array([calculateDamage(self.currentPokemon.getMove1().getName(), self.currentPokemon, oppPoke),
                                calculateDamage(self.currentPokemon.getMove2().getName(), self.currentPokemon, oppPoke),
                                calculateDamage(self.currentPokemon.getMove3().getName(), self.currentPokemon, oppPoke),
                                calculateDamage(self.currentPokemon.getMove4().getName(), self.currentPokemon, oppPoke)])
                maxDamageDealt = np.max(damageGiveList)

                # to incentivize staying in, skip current pokemon if you can kill it
                if oppPoke.getBattleHP() - maxDamageDealt <= 0:
                    continue

                oppMultiplierList = np.array([getMultiplier(oppPoke.getMove1().getName(), oppPoke, aiPoke),
                                getMultiplier(oppPoke.getMove2().getName(), oppPoke, aiPoke),
                                getMultiplier(oppPoke.getMove3().getName(), oppPoke, aiPoke),
                                getMultiplier(oppPoke.getMove4().getName(), oppPoke, aiPoke)])
                maxOppMultiplier = np.max(oppMultiplierList)

                aiMultiplierList = np.array([getMultiplier(aiPoke.getMove1().getName(), aiPoke, oppPoke),
                                getMultiplier(aiPoke.getMove2().getName(), aiPoke, oppPoke),
                                getMultiplier(aiPoke.getMove3().getName(), aiPoke, oppPoke),
                                getMultiplier(aiPoke.getMove4().getName(), aiPoke, oppPoke)])
                maxAIMultiplier = np.max(aiMultiplierList)

                diff = maxAIMultiplier - maxOppMultiplier
                if diff >= 1.0:
                    heuristic += 1.0
                elif (0 >= diff and diff < 1.0):
                    heuristic += 2.0
                else:
                    heuristic += 4.0

            minHeuristicCurr = min(minHeuristicCurr, heuristic)
        costList[0] = g + heuristic

        damageReceivedSwitchList = np.zeros(numRemainingAlivePokemon)
        indexInCostList = 1
        for index in remainingAliveIndexList:
            pokemonToSwitch = self.pokemons[index]
            damageReceivedList = np.array(
                                [calculateDamage(playerCurrentPokemon.getMove1().getName(), playerCurrentPokemon, pokemonToSwitch),
                                 calculateDamage(playerCurrentPokemon.getMove2().getName(), playerCurrentPokemon, pokemonToSwitch),
                                 calculateDamage(playerCurrentPokemon.getMove3().getName(), playerCurrentPokemon, pokemonToSwitch),
                                 calculateDamage(playerCurrentPokemon.getMove4().getName(), playerCurrentPokemon, pokemonToSwitch)])
            for i in range(0, len(damageReceivedList)):
                damageReceivedList[i] = min(damageReceivedList[i], pokemonToSwitch.getBattleHP())
            
            maxDamageReceived = np.max(damageReceivedList)
            g = maxDamageReceived
            heuristic = -currTotalHP
            costList[indexInCostList] = g + heuristic
            indexInCostList+=1

        # Select the min cost edge
        minEdgeIndex = np.argmin(costList)
        if minEdgeIndex == 0: # If the best action is one of the current pokemon moves
            
            # Calculate what is the max damage the AI can do
            damageGiveList = np.array([calculateDamage(self.currentPokemon.getMove1().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove2().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove3().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove4().getName(), self.currentPokemon, playerCurrentPokemon)])            

            moveOptions = [self.currentPokemon.getMove1(), self.currentPokemon.getMove2(), self.currentPokemon.getMove3(), self.currentPokemon.getMove4()]
            return moveOptions[np.argmax(damageGiveList)]
        else: # If the best action is switching
            offset = minEdgeIndex - 1
            pokemonToSwitchIndex = remainingAliveIndexList[offset]
            self.currentPokemon = self.pokemons[pokemonToSwitchIndex]
            return Switch(pokemonToSwitchIndex)

    def selectNextActionOffensive(self, playerCurrentPokemon, allPlayerPokemon):
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

        costList = np.zeros(1 + numRemainingAlivePokemon)

        opponentsHPLeft = 0
        for pokemonNum in range(Constants.NUM_POKEMON_PER_PLAYER):
            if allPlayerPokemon[pokemonNum].isAlive():
                opponentsHPLeft += allPlayerPokemon[pokemonNum].getBattleHP()

        # Calculate what is the max damage the AI can do
        damageGiveList = np.array([calculateDamage(self.currentPokemon.getMove1().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove2().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove3().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove4().getName(), self.currentPokemon, playerCurrentPokemon)])
        for i in range(0,len(damageGiveList)):
            damageGiveList[i] = min(damageGiveList[i], playerCurrentPokemon.getBattleHP())
        bestMoveIndex = np.argmax(damageGiveList)
        g = playerCurrentPokemon.getBattleHP() - np.max(damageGiveList)
        heuristic = opponentsHPLeft
        costList[0] = g + heuristic

        damageReceivedSwitchList = np.zeros(numRemainingAlivePokemon)
        indexInCostList = 1
        for index in remainingAliveIndexList:
            pokemonToSwitch = self.pokemons[index]
            damageGivenList = np.array(
                                [calculateDamage(pokemonToSwitch.getMove1().getName(), pokemonToSwitch, playerCurrentPokemon),
                                 calculateDamage(pokemonToSwitch.getMove2().getName(), pokemonToSwitch, playerCurrentPokemon),
                                 calculateDamage(pokemonToSwitch.getMove3().getName(), pokemonToSwitch, playerCurrentPokemon),
                                 calculateDamage(pokemonToSwitch.getMove4().getName(), pokemonToSwitch, playerCurrentPokemon)])
            for i in range(0,len(damageGivenList)):
                damageGivenList[i] = min(damageGivenList[i], playerCurrentPokemon.getBattleHP())
            g = playerCurrentPokemon.getBattleHP() - np.max(damageGivenList)
            heuristic = opponentsHPLeft 
            costList[indexInCostList] = g + heuristic
            indexInCostList+=1

        # Select the min cost edge
        minEdgeIndex = np.argmin(costList)
        if minEdgeIndex == 0: # If the best action is one of the current pokemon moves
            moveOptions = [self.currentPokemon.getMove1(), self.currentPokemon.getMove2(), self.currentPokemon.getMove3(), self.currentPokemon.getMove4()]
            return moveOptions[bestMoveIndex]
        else: # If the best action is switching
            offset = minEdgeIndex - 1
            pokemonToSwitchIndex = remainingAliveIndexList[offset]
            self.currentPokemon = self.pokemons[pokemonToSwitchIndex]
            return Switch(pokemonToSwitchIndex)

    def selectNextActionTyping(self, playerCurrentPokemon, allPlayerPokemon):
        numRemainingAlivePokemon = 0
        remainingAliveIndexList = []
        for pokemonNum in range(Constants.NUM_POKEMON_PER_PLAYER):
            if self.pokemons[pokemonNum] != self.currentPokemon:
                if self.pokemons[pokemonNum].isAlive():
                    numRemainingAlivePokemon += 1
                    remainingAliveIndexList.append(pokemonNum)

        costList = np.zeros(1 + numRemainingAlivePokemon)

        oppMultiplierList = np.array([getMultiplier(playerCurrentPokemon.getMove1().getName(), playerCurrentPokemon, self.currentPokemon),
                              getMultiplier(playerCurrentPokemon.getMove2().getName(), playerCurrentPokemon, self.currentPokemon),
                              getMultiplier(playerCurrentPokemon.getMove3().getName(), playerCurrentPokemon, self.currentPokemon),
                              getMultiplier(playerCurrentPokemon.getMove4().getName(), playerCurrentPokemon, self.currentPokemon)])
        maxOppMultiplier = np.max(oppMultiplierList)

        # Calculate what is the max damage the AI can do
        aiMultiplierList = np.array([getMultiplier(self.currentPokemon.getMove1().getName(), self.currentPokemon, playerCurrentPokemon),
                          getMultiplier(self.currentPokemon.getMove2().getName(), self.currentPokemon, playerCurrentPokemon),
                          getMultiplier(self.currentPokemon.getMove3().getName(), self.currentPokemon, playerCurrentPokemon),
                          getMultiplier(self.currentPokemon.getMove4().getName(), self.currentPokemon, playerCurrentPokemon)])
        maxAIMultiplier = np.max(aiMultiplierList)

        # compute cost
        edgeCost = 0
        diff = maxAIMultiplier - maxOppMultiplier
        if diff >= 1.0:
            edgeCost = 1.0
        elif (0 >= diff and diff < 1.0):
            edgeCost = 2.0
        else:
            edgeCost = 4.0

        # compute heuristic
        minHeuristicCurr = 0
        for aiPoke in self.pokemons:
            if not(aiPoke.isAlive()):
                continue

            heuristic = 0
            for oppPoke in allPlayerPokemon:
                if not(oppPoke.isAlive()):
                    continue

                # Calculate what is the max damage the AI can do
                damageGiveList = np.array([calculateDamage(self.currentPokemon.getMove1().getName(), self.currentPokemon, oppPoke),
                                calculateDamage(self.currentPokemon.getMove2().getName(), self.currentPokemon, oppPoke),
                                calculateDamage(self.currentPokemon.getMove3().getName(), self.currentPokemon, oppPoke),
                                calculateDamage(self.currentPokemon.getMove4().getName(), self.currentPokemon, oppPoke)])
                maxDamageDealt = np.max(damageGiveList)

                # to incentivize staying in, skip current pokemon if you can kill it
                if oppPoke.getBattleHP() - maxDamageDealt <= 0:
                    continue

                oppMultiplierList = np.array([getMultiplier(oppPoke.getMove1().getName(), oppPoke, aiPoke),
                                getMultiplier(oppPoke.getMove2().getName(), oppPoke, aiPoke),
                                getMultiplier(oppPoke.getMove3().getName(), oppPoke, aiPoke),
                                getMultiplier(oppPoke.getMove4().getName(), oppPoke, aiPoke)])
                maxOppMultiplier = np.max(oppMultiplierList)

                aiMultiplierList = np.array([getMultiplier(aiPoke.getMove1().getName(), aiPoke, oppPoke),
                                getMultiplier(aiPoke.getMove2().getName(), aiPoke, oppPoke),
                                getMultiplier(aiPoke.getMove3().getName(), aiPoke, oppPoke),
                                getMultiplier(aiPoke.getMove4().getName(), aiPoke, oppPoke)])
                maxAIMultiplier = np.max(aiMultiplierList)

                diff = maxAIMultiplier - maxOppMultiplier
                if diff >= 1.0:
                    heuristic += 1.0
                elif (0 >= diff and diff < 1.0):
                    heuristic += 2.0
                else:
                    heuristic += 4.0

            minHeuristicCurr = min(minHeuristicCurr, heuristic)

        costList[0] = edgeCost + minHeuristicCurr

        minHeuristicRest = 0
        for aiPoke in self.pokemons:
            if not(aiPoke.isAlive()):
                continue

            heuristic = 0
            for oppPoke in allPlayerPokemon:
                if not(oppPoke.isAlive()):
                    continue

                oppMultiplierList = np.array([getMultiplier(oppPoke.getMove1().getName(), oppPoke, aiPoke),
                                getMultiplier(oppPoke.getMove2().getName(), oppPoke, aiPoke),
                                getMultiplier(oppPoke.getMove3().getName(), oppPoke, aiPoke),
                                getMultiplier(oppPoke.getMove4().getName(), oppPoke, aiPoke)])
                maxOppMultiplier = np.max(oppMultiplierList)

                aiMultiplierList = np.array([getMultiplier(aiPoke.getMove1().getName(), aiPoke, oppPoke),
                                getMultiplier(aiPoke.getMove2().getName(), aiPoke, oppPoke),
                                getMultiplier(aiPoke.getMove3().getName(), aiPoke, oppPoke),
                                getMultiplier(aiPoke.getMove4().getName(), aiPoke, oppPoke)])
                maxAIMultiplier = np.max(aiMultiplierList)

                diff = maxAIMultiplier - maxOppMultiplier
                if diff >= 1.0:
                    heuristic += 1.0
                elif (0 >= diff and diff < 1.0):
                    heuristic += 2.0
                else:
                    heuristic += 4.0

            minHeuristicRest = min(minHeuristicRest, heuristic)

        # repeat for switching
        indexInCostList = 1
        for i in remainingAliveIndexList:
            aiPoke = self.pokemons[i]

            oppMultiplierList = np.array([getMultiplier(playerCurrentPokemon.getMove1().getName(), playerCurrentPokemon, aiPoke),
                              getMultiplier(playerCurrentPokemon.getMove2().getName(), playerCurrentPokemon, aiPoke),
                              getMultiplier(playerCurrentPokemon.getMove3().getName(), playerCurrentPokemon, aiPoke),
                              getMultiplier(playerCurrentPokemon.getMove4().getName(), playerCurrentPokemon, aiPoke)])
            maxOppMultiplier = np.max(oppMultiplierList)

            # Calculate what is the max damage the AI can do
            aiMultiplierList = np.array([getMultiplier(aiPoke.getMove1().getName(), aiPoke, playerCurrentPokemon),
                            getMultiplier(aiPoke.getMove2().getName(), aiPoke, playerCurrentPokemon),
                            getMultiplier(aiPoke.getMove3().getName(), aiPoke, playerCurrentPokemon),
                            getMultiplier(aiPoke.getMove4().getName(), aiPoke, playerCurrentPokemon)])
            maxAIMultiplier = np.max(aiMultiplierList)
            
            edgeCost = 0
            diff = maxAIMultiplier - maxOppMultiplier
            if diff >= 1.0:
                edgeCost = 1.0
            elif (0 >= diff and diff < 1.0):
                edgeCost = 2.0
            else:
                edgeCost = 4.0
            costList[indexInCostList] = edgeCost + minHeuristicRest
            indexInCostList += 1
                
        # Select the min cost edge
        minEdgeIndex = np.argmin(costList)
        if minEdgeIndex == 0: # If the best action is one of the current pokemon moves
            moveOptions = [self.currentPokemon.getMove1(), self.currentPokemon.getMove2(), self.currentPokemon.getMove3(), self.currentPokemon.getMove4()]
            damageGiveList = np.array([calculateDamage(self.currentPokemon.getMove1().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove2().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove3().getName(), self.currentPokemon, playerCurrentPokemon),
                          calculateDamage(self.currentPokemon.getMove4().getName(), self.currentPokemon, playerCurrentPokemon)])
            bestMoveIndex = np.argmax(damageGiveList)
            return moveOptions[bestMoveIndex]
        else: # If the best action is switching
            offset = minEdgeIndex - 1
            pokemonToSwitchIndex = remainingAliveIndexList[offset]
            self.currentPokemon = self.pokemons[pokemonToSwitchIndex]
            return Switch(pokemonToSwitchIndex)

    def forceSwitch(self, pokemonIndex):
        self.currentPokemon = self.pokemons[pokemonIndex]