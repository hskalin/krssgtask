import socket
from sys import exit, argv

# this function returns the card value and name given a string
def returnCard(card):
    index = int(card)

    # first determine the suit
    if index < 14:
        suit = " of Diamond"
    elif index < 27:
        suit = " of Hearts"
    elif index < 40:
        suit = " of Spades"
    else:
        suit = " of Clubs"

    # determining the card value
    index = index % 13
    if index == 0:
        index = 13

    # finalizing the name
    if index == 1:
        value = "Ace"
    elif index == 11:
        value = "Joker"
    elif index == 12:
        value = "Queen"
    elif index == 13:
        value = "King"
    else:
        value = str(index)

    # returning the vlaue and the name
    return index, value + suit


# check the commandline parameters
if len(argv) != 2:
    print(f"Usage: {str(argv[0])} portNumber")
    exit(1)

# tryng to establish a connection
playerSocket = socket.socket()
host = '127.0.0.1'

# check is the port number specified is an integer
try:
    port = int(argv[1])
except ValueError:
    print("error: port number should be an integer")
    exit(1)

# trying to connect to the server
print('Connecting to the Casino ...')
try:
    playerSocket.connect((host, port))
except socket.error as e:
    print(str(e))
    exit(1)

# send ID
playerSocket.sendall(str.encode('PLAYER'))

print("Connected to the Casino. Waiting for other players to join.")

# start the main loop that continuously listens to the casino server
while True:
    # getting the response from the server
    resp = playerSocket.recv(1024).decode('utf-8')

    # if the message is TERM then close the connection
    if resp == 'TERM':
        print('Casino server sent termination signal')
        break

    # if the response begins with CARD then parse the string, get cards and ask
    # the user for the card to use
    elif resp[:4] == 'CARD':
        print(f'\nStarting round {resp[-1]}')
        print('Cards received')

        print(f'Card [1] - {returnCard(resp[4:6])}')
        print(f'Card [2] - {returnCard(resp[6:8])}')
        print(f'Card [3] - {returnCard(resp[8:10])}')

        # ensuring proper input
        card = 0
        while True:
            try:
                card = int(input("\nEnter the card number to use (1, 2, 3)  "))
            except ValueError:
                print("please enter an integer in [1, 3]")
                continue

            if card < 1 or card > 3:
                print("please enter an integer in [1, 3]")
            else:
                break

        # send the card value to the casino server
        playerSocket.sendall(str.encode(str(returnCard(resp[2+card*2:4+card*2])[0]) ))

    # if the message begins with RES then print it
    elif resp[:3] == 'RES':
        print(resp[3:])

# close the connection
playerSocket.close()
