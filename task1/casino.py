import socket
import random
import time
from sys import exit, argv

from _thread import *

# initilizing the variables
# cards store the random cards string
cards = None
# this keeps track of the current round
crntRound = 0
# this keeps track of whether all cards are sent and received or not
sentList = []
# this stores all the palayers conection information
playerList = []
# this stores the cards returned by the players
retCards = []
# this keeps track of the cumulative scores of each player
winList = []

# this funtion is executed in a new thread and sends and receives cards simultaneously 
def threaded_player(player, index):
    # the global variables
    global cards, sentList, crntRound, retCards
     
    # send greeting
    player.send(str.encode(f'RESWelcome to the Casino\nYou are player {chr(65 + index)}'))
    time.sleep(0.1)

    # main loop which keeps checking if there are any cards to send 
    while True:
        # if sentList is true then send the cards
        if sentList[index] == 1:

            # send the corresponding cards to the players with round number
            player.sendall(str.encode('CARD' + cards[index*6 : (index+1)*6] + str(crntRound)))
            resp = player.recv(1024).decode('utf-8')

            # store the returned card
            retCards[index] = int(resp)
            
            # put sentList to zero indicating that card is received
            sentList[index] = 0
            
    player.close()



# this function gets the number of players and rounds from the client
def getGameData(CasinoSocket):
    print('Waiting for the client')
    client = None

    # loop unitl the connected program is the client
    while True:
        client, addr = CasinoSocket.accept()

        ID = client.recv(1024).decode('utf-8')

        if ID == 'CLIENT':
            break
        else:
            # send termination signal
            client.sendall(str.encode('TERM'))
            client.close()
    
    # get the game data
    data = client.recv(1024).decode('utf-8')
    print('Data received\n')

    # close connection
    client.close()

    # return the players and the rounds
    return int(data[:3]), int(data[3:6])



# this function connects to the specified number of players
def addPlayers(CasinoSocket, playerCount):
    global playerList

    print(f'Waiting for the {playerCount} players to join ...')

    for i in range(playerCount):
        # connects to the players and adds them to the playerList
        player, address = CasinoSocket.accept()
        _ = player.recv(1024)
        playerList.append(player)

        print(f'Connected to player {chr(65 + i)} at ' + address[0] + ' : ' + str(address[1]))
        # start the connection is a new thread
        start_new_thread(threaded_player, (player, i,))



# This function calculates the winner of each round and updates the winList
def updateResults():
    global sentList, retCards, winList, crntRound

    # temporary winList for the current round
    tempWinList = [0]*len(winList)

    # keep checking unitl the whole sentList is zero, ie all players returned the card
    while sum(sentList) != 0:
        time.sleep(0.1)

    print(f"Round {crntRound}\nCards received from the players")
    
    # find the max of cards
    maxCrd = max(retCards)
    # fill the win lists
    for i in range(len(retCards)):
        if retCards[i] == maxCrd:
            tempWinList[i] += 1
            winList[i] += 1

    # print the round winner
    if sum(tempWinList) > 1:
        print('Tie between ', end='')
    else:
        print('The winner is ', end='')

    for i in range(len(tempWinList)):
        if tempWinList[i] == 1:
            print(f'player {chr(65 + i)}, ', end='')
    print('\n')


# this function simulates the rounds
def simulateRound(rounds, playerCount):
    global crntRound, cards
    
    for i in range(rounds):
        crntRound += 1
        cards = ''
        cardlist = [x for x in range(1, 53)]

        # fill the cards string with random cards with no repetition
        for j in range(playerCount*3):
            num = random.choice(cardlist)
            cardlist.remove(num)

            cards = cards + str(num).zfill(2)

        # set the sentList to 1 which signals all the player threads to send the cards
        sentList[:] = [1]*len(sentList)
        # get the results
        updateResults()

# this function prints the final winner
def printWinner():
    global winList, playerList

    winners = 0
    maxWins = max(winList)

    for i in range(len(winList)):
        if winList[i] == maxWins:
            winners += 1

    if winners == 1:
        result = '\nGAME OVER\nThe winner of the game is '
    else:
        result = '\nGAME OVER\nTie between '

    for i in range(len(winList)):
        if winList[i] == maxWins:
            result += f'player {chr(65 + i)}, '

    print(result)

    # also sent the result string to all the players with a RES prefix so that 
    # the final result is displayed everywhere
    for player in playerList:
        player.sendall(str.encode('RES' + result))


# this function simulates the whole game
def simulateGame(rounds, playerCount):
    global playerList, crntRound, winList
    play = True

    while play:
        # simulate the rounds
        simulateRound(rounds, playerCount)
        # print the winner
        printWinner()

        # ask for anther game
        inpt = input('Play another game? (y/n) ')
        print()
        if inpt.lower() == 'n':
            play = False

            # if the ans is no then terminate all players by sending TERM signal
            for player in playerList:
                player.sendall(str.encode('TERM'))
        else:
            # if ans is yes then reset the current rounds and the winList
            crntRound = 0
            winList[:] = [0]*len(winList)
            retCards[:] = [0]*len(retCards)


def main():
    global cards, retCards, winList

    # check the commandline parameters
    if len(argv) != 2:
        print(f"Usage: {str(argv[0])} portNumber")
        exit(1)

    # ensure that the port number is an integer
    try:
        port = int(argv[1])
    except ValueError:
        print("error: port number should be an integer")
        exit(1)

    # initialize the socket 
    CasinoSocket = socket.socket()
    host = '127.0.0.1'
    port = port

    # try establishing the connection
    try:
        CasinoSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
        exit(1)

    # listen to the connection requests
    CasinoSocket.listen()

    # get the players and rounds number 
    playerCount, rounds = getGameData(CasinoSocket)

    # initialize redurned cards and winList to zero
    retCards[:] = [0]*playerCount
    winList[:] = [0]*playerCount

    for i in range(playerCount):
        sentList.append(0)

    # Add players to the playerList
    addPlayers(CasinoSocket, playerCount)

    print(f'\nAll {playerCount} players joined. Starting the game\n')

    # simulate the game
    simulateGame(rounds, playerCount)
    
    CasinoSocket.close()

main()
