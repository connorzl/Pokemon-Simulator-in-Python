from Attack import *
from tkinter import *
from Pokedex import *
from PokemonAI import PokemonAI
from CONSTANTS import Constants
import numpy as np

class ApplicationAutomated(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid()

        self.battleBtn = Button(self, text="Begin Battle", state=NORMAL, command=self.beginBattle)
        self.battleBtn.grid(row=2, column=1)

        # Sprites
        tempImg = PhotoImage(file="Sprites/white.gif")  # first putting a blank image for each sprite, will replace later after pressing "Begin Battle"

        # Creating an image label object for each sprite
        self.sprite1Label = Label(self, image=tempImg)
        self.sprite1Label.image = tempImg
        self.sprite1Label.grid(row=3, column=0)

        self.sprite2Label = Label(self, image=tempImg)
        self.sprite2Label.image = tempImg
        self.sprite2Label.grid(row=3, column=2)

        self.currTurn = 0

        self.currRun = 0

        self.log = ""

        self.totalRun = 100

        self.player1WinTimes = 0
        self.player2WinTimes = 0

        self.player1PokemonLeft = 0
        self.player2PokemonLeft = 0

        self.player1AverageHP = 0
        self.player2AverageHP = 0

        self.player1WinTurns = 0
        self.player2WinTurns = 0

        self.winner = 0

    # Creating a method to print the list of all Pokemon
    def seePokedex(self):
        self.txtStats.config(state=NORMAL)
        self.txtStats.delete(0.0, END)
        for pokemon in pokedex:
            self.txtStats.insert(END, "\n" + pokemon)
        self.txtStats.config(state=DISABLED)

    def printPokemon(self, isPlayer):
        msg = ""
        if isPlayer:
            for i in range(0,len(self.userPokemon)):
                if i != self.userActive and self.userPokemon[i].isAlive():
                    msg += "\nSwitch to " + self.userPokemon[i].printHP()
        else:
            for i in range(0,len(self.cpuPokemon)):
                if i != self.cpuActive and self.cpuPokemon[i].isAlive():
                    msg += "\nSwitch to " + self.cpuPokemon[i].printHP()
        return msg

    def alive(self, isPlayer):
        alive = False
        if isPlayer:
            for poke in self.userPokemon:
                if poke.isAlive():
                    alive = True 
        else:
            for poke in self.cpuPokemon:
                if poke.isAlive():
                    alive = True 
        return alive

    def saveLog(self, logGiven):
        pass
        # file1 = open("log.txt", "a")
        # file1.write(logGiven)
        # file1.close()

    def restart(self):
        self.currRun += 1
        self.currTurn = 0
        self.log += "\n" + "--- A new battle begins! ---"
        self.log += "\n"
        # print("--- A new battle begins! ---")
        # print()
        self.battleBtn.config(state=DISABLED)
        # Pokemon Objects

        pokemons = []
        for i in range(Constants.NUM_POKEMON_PER_PLAYER):
            index = int(np.random.uniform(0, len(pokedex)))
            pokemons.append(pokedex[index])

        self.userPokemonNames = pokemons
        self.userActive = 0;
        self.cpuPokemonNames = pokemons
        self.cpuActive = 0;
        self.userPokemon = []
        self.cpuPokemon = []
        for i in range(len(self.userPokemonNames)):
            self.userPokemon.append(Pokemon(self.userPokemonNames[i]))
            self.cpuPokemon.append(Pokemon(self.cpuPokemonNames[i]))

        # Initialize the AI
        self.pokemonAI1 = PokemonAI(self.userPokemon[self.userActive], self.userPokemon)
        self.pokemonAI2 = PokemonAI(self.cpuPokemon[self.cpuActive], self.cpuPokemon)
        self.currTurn = 0

        # Replacing the blank image with the actual sprites of the appropriate Pokemon
        # Using the user-input string to determine which sprite image to use
        self.sprite1 = PhotoImage(file="Sprites/" + self.userPokemon[self.userActive].name + ".gif")
        self.sprite1Label.configure(image=self.sprite1)
        self.sprite1Label.image = self.sprite1

        self.sprite2 = PhotoImage(file="Sprites/" + self.cpuPokemon[self.cpuActive].name + ".gif")
        self.sprite2Label.configure(image=self.sprite2)
        self.sprite2Label.image = self.sprite2

        self.winner = 0
        # By default player 1 always go first
        self.selectMove1()

        # If player 1 wins the current game
        if self.winner == 1:
            self.player1WinTimes += 1
            localTotalHP = 0
            localPokemonAlive = 0
            for i in range(0,len(self.userPokemon)):
                localTotalHP += self.userPokemon[i].getBattleHP() / self.userPokemon[i].getMaxHP()
                if self.userPokemon[i].isAlive():
                    localPokemonAlive += 1
            localTotalHP = localTotalHP / len(self.userPokemon)
            self.player1PokemonLeft += localPokemonAlive
            self.player1AverageHP += localTotalHP
            self.player1WinTurns += self.currTurn
        else:
            self.player2WinTimes += 1
            localTotalHP = 0
            localPokemonAlive = 0
            for i in range(0, len(self.cpuPokemon)):
                localTotalHP += self.cpuPokemon[i].getBattleHP() / self.cpuPokemon[i].getMaxHP()
                if self.cpuPokemon[i].isAlive():
                    localPokemonAlive += 1
            localTotalHP = localTotalHP / len(self.cpuPokemon)
            self.player2PokemonLeft += localPokemonAlive
            self.player2AverageHP += localTotalHP
            self.player2WinTurns += self.currTurn
        return

    def switchPokemon(self, isPlayer, switch=True):
        if isPlayer:
            self.sprite1 = PhotoImage(file="Sprites/" + self.userPokemon[self.userActive].name + ".gif")
            self.sprite1Label.configure(image=self.sprite1)
            self.sprite1Label.image = self.sprite1

            # Updating the info for both Pokemon after switching
            # self.moveText1.config(state=NORMAL)
            # self.moveText2.config(state=NORMAL)
            # self.moveText1.delete(0.0, END)
            # self.moveText2.delete(0.0, END)
            # self.moveText1.insert(0.0, self.userPokemon[self.userActive].printHP() + "\n" + self.userPokemon[self.userActive].printMoves() + self.printPokemon(True))
            # self.moveText2.insert(0.0, self.cpuPokemon[self.cpuActive].printHP() + "\n" + self.cpuPokemon[self.cpuActive].printMoves() + self.printPokemon(False))
            # self.moveText1.config(state=DISABLED)
            # self.moveText2.config(state=DISABLED)

            # if switch:
            #     self.moveEnt1.delete(0, END)
            #     self.moveEnt1.config(state=DISABLED)
            #     self.moveBtn1.config(state=DISABLED)
            #     self.moveEnt2.config(state=NORMAL)
            #     self.moveBtn2.config(state=NORMAL)
            # else:
            #     self.moveEnt2.delete(0, END)
            #     self.moveEnt2.config(state=DISABLED)
            #     self.moveBtn2.config(state=DISABLED)
            #     self.moveEnt1.config(state=NORMAL)
            #     self.moveBtn1.config(state=NORMAL)
        else:
            self.sprite2 = PhotoImage(file="Sprites/" + self.cpuPokemon[self.cpuActive].name + ".gif")
            self.sprite2Label.configure(image=self.sprite2)
            self.sprite2Label.image = self.sprite2

            # # Updating the info for the other Pokemon
            # self.moveText1.config(state=NORMAL)
            # self.moveText2.config(state=NORMAL)
            # self.moveText1.delete(0.0, END)
            # self.moveText2.delete(0.0, END)
            # self.moveText1.insert(0.0, self.userPokemon[self.userActive].printHP() + "\n" + self.userPokemon[self.userActive].printMoves() + self.printPokemon(True))
            # self.moveText2.insert(0.0, self.cpuPokemon[self.cpuActive].printHP() + "\n" + self.cpuPokemon[self.cpuActive].printMoves() + self.printPokemon(False))
            # self.moveText1.config(state=DISABLED)
            # self.moveText2.config(state=DISABLED)
            #
            # if switch:
            #     self.moveEnt2.delete(0, END)
            #     self.moveEnt2.config(state=DISABLED)
            #     self.moveBtn2.config(state=DISABLED)
            #     self.moveEnt1.config(state=NORMAL)
            #     self.moveBtn1.config(state=NORMAL)
            # else:
            #     self.moveEnt1.delete(0, END)
            #     self.moveEnt1.config(state=DISABLED)
            #     self.moveBtn1.config(state=DISABLED)
            #     self.moveEnt2.config(state=NORMAL)
            #     self.moveBtn2.config(state=NORMAL)

    # Creating a method to actually start the battle
    def beginBattle(self):

        while self.currRun < self.totalRun:
            self.restart()
            print("-- A game ended --")
        print("-- All games ended. Now start logging the stats-- ")
        # Calculate the final statistics
        player1Message = ""
        player2Message = ""
        player1Message += "\n" + "Player1 has won {0} out of {1} games".format(self.player1WinTimes,self.totalRun)
        player2Message += "\n" + "Player2 has won {0} out of {1} games".format(self.player2WinTimes, self.totalRun)

        if self.player1WinTimes == 0:
            player1Message += "\n" + "Player1's average turns taken to win each game is 0"
        else:
            player1Message += "\n" + "Player1's average turns taken to win each game is {0}".format(self.player1WinTurns/self.player1WinTimes)

        if self.player2WinTimes == 0:
            player2Message += "\n" + "Player2's average turns taken to win each game is 0"
        else:
            player2Message += "\n" + "Player2's average turns taken to win each game is {0}".format(self.player2WinTurns / self.player2WinTimes)

        if self.player1WinTimes == 0:
            player1Message += "\n" + "Player1's average number of alive pokemon at the end of each win game is 0"
        else:
            player1Message += "\n" + "Player1's average number of alive pokemon at the end of each win game is {0}".format(self.player1PokemonLeft / self.player1WinTimes)

        if self.player2WinTimes == 0:
            player2Message += "\n" + "Player2's average number of alive pokemon at the end of each win game is 0"
        else:
            player2Message += "\n" + "Player2's average number of alive pokemon at the end of each win game is {0}".format(self.player2PokemonLeft / self.player2WinTimes)

        if self.player1WinTimes == 0:
            player1Message += "\n" + "Player1's average HP at the end of each win game is 0"
        else:
            player1Message += "\n" + "Player1's average HP at the end of each win game is {0}".format(self.player1AverageHP / self.player1WinTimes)
        if self.player2WinTimes == 0:
            player2Message += "\n" + "Player2's average HP at the end of each win game is 0"
        else:
            player2Message += "\n" + "Player2's average HP at the end of each win game is {0}".format(self.player2AverageHP / self.player2WinTimes)

        player1Message += "\n"
        player2Message += "\n"

        player1File = open("Player1.txt", "a")
        player2File = open("Player2.txt", "a")

        player1File.write(player1Message)
        player2File.write(player2Message)

        player1File.close()
        player2File.close()

        # # By default player 1 always go first
        # self.selectMove1()

    # Method takes the user-inputted string and plugs it into the attack function
    # Prints the result of the attack function to the center text box
    def selectMove1(self, event=None):
        self.currTurn += 1
        AIAction = self.pokemonAI1.selectNextActionDefensive(self.cpuPokemon[self.cpuActive])
        #AIAction = self.pokemonAI1.selectNextActionOffensive(self.cpuPokemon[self.cpuActive], self.cpuPokemon)
        #AIAction = self.pokemonAI1.selectNextActionTyping(self.cpuPokemon[self.cpuActive], self.cpuPokemon)
        if AIAction.actionName == "move":
            # self.txtStats.config(state=NORMAL)
            # self.txtStats.delete(0.0, END)
            # self.txtStats.insert(0.0, attack(AIAction.getName(), self.userPokemon[self.userActive], self.cpuPokemon[self.cpuActive]))
            # self.txtStats.config(state=DISABLED)
            tmpMessage = attack(AIAction.getName(), self.userPokemon[self.userActive], self.cpuPokemon[self.cpuActive])
            self.log += "\n" + "Player 1's move!"
            self.log += "\n"
            self.log += "\n" + tmpMessage
            self.log += "\n"
            #print("Player 1's move!")
            #print()
            #print(tmpMessage)
            #print()
            # # Updating the info for the other Pokemon
            # self.moveText1.config(state=NORMAL)
            # self.moveText2.config(state=NORMAL)
            # self.moveText1.delete(0.0, END)
            # self.moveText2.delete(0.0, END)
            # self.moveText1.insert(0.0, self.userPokemon[self.userActive].printHP() + "\n" + self.userPokemon[self.userActive].printMoves() + self.printPokemon(True))
            # self.moveText2.insert(0.0, self.cpuPokemon[self.cpuActive].printHP() + "\n" + self.cpuPokemon[self.cpuActive].printMoves() + self.printPokemon(False))
            # self.moveText1.config(state=DISABLED)
            # self.moveText2.config(state=DISABLED)
            tmpMessage = self.userPokemon[self.userActive].printHP() + "\n" + self.userPokemon[self.userActive].printMoves() + self.printPokemon(True)
            #print(tmpMessage)
            self.log += "\n" + tmpMessage
            self.log += "\n"
            #print()

            tmpMessage = self.cpuPokemon[self.cpuActive].printHP() + "\n" + self.cpuPokemon[self.cpuActive].printMoves() + self.printPokemon(False)
            self.log += "\n" + tmpMessage
            self.log += "\n"
            #print(tmpMessage)
            #print()
            # if the other player loses, end the game
            if not self.alive(False):
                # self.txtStats.config(state=NORMAL)
                # self.txtStats.insert(END, "\n" + self.cpuPokemon[self.cpuActive].faint())
                # self.txtStats.insert(END, "\nPlay again?")
                # self.txtStats.config(state=DISABLED)
                # self.moveEnt2.delete(0, END)
                # self.restartBtn.config(state=NORMAL)
                # self.moveText1.config(state=DISABLED)
                # self.moveText2.config(state=DISABLED)
                # self.moveEnt2.config(state=DISABLED)
                # self.moveBtn2.config(state=DISABLED)
                self.battleBtn.config(state=NORMAL)

                tmpMessage = self.cpuPokemon[self.cpuActive].faint()
                #print(tmpMessage)
                self.log += "\n" + tmpMessage
                self.log += "\n" + "Player 1 wins!"
                self.log += "\n" + "--- A game has ended! ---"
                self.log += "\n" + "Number of Turns: " + str(self.currTurn)
                self.log += "\n"
                self.saveLog(self.log)
                #print("Player 1 wins!")
                #print("--- A game has ended! ---")
                #print("Number of Turns: " + str(self.currTurn))
                #print()
                self.winner = 1
                return

            elif not self.cpuPokemon[self.cpuActive].isAlive():
                self.log += "\n" + "Player 2's {0} faints!".format(self.cpuPokemon[self.cpuActive].getName())
                #print("Player 2's {0} faints!".format(self.cpuPokemon[self.cpuActive].getName()))
                # other player still has at least 1 more pokemon alive, switch to first alive pokemon
                for i in range(0,len(self.cpuPokemon)):
                    if self.cpuPokemon[i].isAlive():
                        self.cpuActive = i
                        break
                self.switchPokemon(False,False)
                self.pokemonAI2.forceSwitch(self.cpuActive)
                self.log += "\n" + "Replaced with {0}.".format(self.cpuPokemon[self.cpuActive].getName())
                #print("Replaced with {0}.".format(self.cpuPokemon[self.cpuActive].getName()))
            # else:
            #     self.moveEnt1.delete(0, END)
            #     self.moveEnt2.config(state=NORMAL)
            #     self.moveBtn2.config(state=NORMAL)
            #     self.moveEnt1.config(state=DISABLED)
            #     self.moveBtn1.config(state=DISABLED)
        else:
            #  If AI decides to switch to another pokemon
            self.log += "\n" + "Player 1 takes back {0}".format(self.userPokemon[self.userActive].getName())
            #print("Player 1 takes back {0}".format(self.userPokemon[self.userActive].getName()))
            self.userActive = AIAction.getPokemon()
            self.switchPokemon(True)
            self.pokemonAI1.forceSwitch(self.userActive)
            self.log += "\n" + "Player 1 calls up {0}.".format(self.userPokemon[self.userActive].getName())
            #print("Player 1 calls up {0}.".format(self.userPokemon[self.userActive].getName()))

        # Turn switch to player 2
        self.selectMove2()

    # Does the same thing as selectMove1() just with respect to the other Pokemon
    def selectMove2(self, event=None):
        self.currTurn += 1
        #AIAction = self.pokemonAI2.selectNextAction(self.userPokemon[self.userActive])
        AIAction = self.pokemonAI2.selectNextActionTyping(self.userPokemon[self.userActive], self.userPokemon)
        if AIAction.actionName == "move":
            tmpMessage = attack(AIAction.getName(), self.cpuPokemon[self.cpuActive], self.userPokemon[self.userActive])
            # print("Player 2's move!")
            # print()
            # print(tmpMessage)
            # print()
            self.log += "\n" + "Player 2's move!"
            self.log += "\n"
            self.log += "\n" + tmpMessage
            self.log += "\n"

            tmpMessage = self.userPokemon[self.userActive].printHP() + "\n" + self.userPokemon[self.userActive].printMoves() + self.printPokemon(True)
            # print(tmpMessage)
            # print()
            self.log += "\n" + tmpMessage
            self.log += "\n"
            tmpMessage = self.cpuPokemon[self.cpuActive].printHP() + "\n" + self.cpuPokemon[self.cpuActive].printMoves() + self.printPokemon(False)
            # print(tmpMessage)
            # print()
            self.log += "\n" + tmpMessage
            self.log += "\n"
            # if the other player loses, end the game
            if not self.alive(True):
                self.battleBtn.config(state=NORMAL)

                tmpMessage = self.userPokemon[self.userActive].faint()
                # print(tmpMessage)
                self.log += "\n" + tmpMessage
                self.log += "\n"
                self.log += "\n" + "Player 2 wins!"
                self.log += "\n" + "--- A game has ended! ---"
                self.log += "\n" + "Number of Turns: " + str(self.currTurn)
                self.log += "\n"
                self.saveLog(self.log)
                #print("Player 2 wins!")
                #print("--- A game has ended! ---")
                #print("Number of Turns: " + str(self.currTurn))
                #print()
                self.winner = 2
                return

            elif not self.userPokemon[self.userActive].isAlive():
                self.log += "\n" + "Player 1's {0} faints!".format(self.userPokemon[self.userActive].getName())
                #print("Player 1's {0} faints!".format(self.userPokemon[self.userActive].getName()))
                # other player still has at least 1 more pokemon alive, switch to first alive pokemon
                for i in range(0,len(self.userPokemon)):
                    if self.userPokemon[i].isAlive():
                        self.userActive = i
                        break
                self.switchPokemon(True,False)
                self.pokemonAI1.forceSwitch(self.userActive)
                self.log += "\n" + "Replaced with {0}.".format(self.userPokemon[self.userActive].getName())
                #print("Replaced with {0}.".format(self.userPokemon[self.userActive].getName()))
        else:
            #  If AI decides to switch to another pokemon
            self.log += "\n" + "Player 2 takes back {0}".format(self.cpuPokemon[self.cpuActive].getName())
            #print("Player 2 takes back {0}".format(self.cpuPokemon[self.cpuActive].getName()))
            self.cpuActive = AIAction.getPokemon()
            self.switchPokemon(False)
            self.pokemonAI2.forceSwitch(self.cpuActive)
            self.log += "\n" + "Player 2 calls up {0}.".format(self.cpuPokemon[self.cpuActive].getName())
            #print("Player 2 calls up {0}.".format(self.cpuPokemon[self.cpuActive].getName()))


        # deduct 1 hp from both current pokemon
        self.userPokemon[self.userActive].loseHP(1)
        self.cpuPokemon[self.cpuActive].loseHP(1)

        # for player 1
        if not self.alive(True):
            self.battleBtn.config(state=NORMAL)

            tmpMessage = self.userPokemon[self.userActive].faint()
            self.log += "\n" + tmpMessage
            self.log += "\n"
            #print(tmpMessage)

            self.log += "\n" + "Player 2 wins!"
            self.log += "\n" + "--- A game has ended! ---"
            self.log += "\n" + "Number of Turns: " + str(self.currTurn)
            self.log += "\n"
            self.saveLog(self.log)

            self.winner = 2
            return
        elif not self.userPokemon[self.userActive].isAlive():
            self.log += "\n" + "Player 1's {0} faints!".format(self.userPokemon[self.userActive].getName())
            #print("Player 1's {0} faints!".format(self.userPokemon[self.userActive].getName()))
            # other player still has at least 1 more pokemon alive, switch to first alive pokemon
            for i in range(0,len(self.userPokemon)):
                if self.userPokemon[i].isAlive():
                    self.userActive = i
                    break
            self.switchPokemon(True,False)
            self.pokemonAI1.forceSwitch(self.userActive)
            self.log += "\n" + "Replaced with {0}.".format(self.userPokemon[self.userActive].getName())
            #print("Replaced with {0}.".format(self.userPokemon[self.userActive].getName()))
        
        # for player 2
        if not self.alive(False):
            self.battleBtn.config(state=NORMAL)

            tmpMessage = self.cpuPokemon[self.cpuActive].faint()
            self.log += "\n" + tmpMessage
            self.log += "\n" + "Player 1 wins!"
            self.log += "\n" + "--- A game has ended! ---"
            self.log += "\n" + "Number of Turns: " + str(self.currTurn)
            self.log += "\n"

            self.log += "\n" + "-- Total game summary --"
            tmpMessage = self.userPokemon[self.userActive].printHP() + "\n" + self.userPokemon[self.userActive].printMoves() + self.printPokemon(True)
            # print(tmpMessage)
            # print()
            self.log += "\n" + tmpMessage
            self.log += "\n"
            tmpMessage = self.cpuPokemon[self.cpuActive].printHP() + "\n" + self.cpuPokemon[self.cpuActive].printMoves() + self.printPokemon(False)
            # print(tmpMessage)
            # print()
            self.log += "\n" + tmpMessage
            self.log += "\n"

            self.saveLog(self.log)
            # print(tmpMessage)
            #
            # print("Player 1 wins!")
            # print("--- A game has ended! ---")
            # print("Number of Turns: " + str(self.currTurn))
            # print()
            self.winner = 1
            return
        elif not self.cpuPokemon[self.cpuActive].isAlive():
            self.log += "\n" + "Player 2's {0} faints!".format(self.cpuPokemon[self.cpuActive].getName())
            #print("Player 2's {0} faints!".format(self.cpuPokemon[self.cpuActive].getName()))
            # other player still has at least 1 more pokemon alive, switch to first alive pokemon
            for i in range(0,len(self.cpuPokemon)):
                if self.cpuPokemon[i].isAlive():
                    self.cpuActive = i
                    break
            self.switchPokemon(True,False)
            self.pokemonAI2.forceSwitch(self.cpuActive)
            self.log += "\n" + "Replaced with {0}.".format(self.cpuPokemon[self.cpuActive].getName())
            #print("Replaced with {0}.".format(self.cpuPokemon[self.cpuActive].getName()))

        self.selectMove1()



