import socket
from sys import exit, argv

# function returns a positive integer
def posInt(msg):
    val = 0
    while True:
        try:
            val = int(input(msg))
        except ValueError:
            print("please enter an integer")
            continue

        if val<1:
            print("please enter a positive integer")
        else:
            break
    return val


# check the commandline parameters
if len(argv) != 2:
    print(f"Usage: {str(argv[0])} portNumber")
    exit(1)

# tryng to establish a connection
ClientSocket = socket.socket()
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
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))
    exit(1)

print("Connected to the Casino") 

# send identity to the server
ClientSocket.sendall(str.encode('CLIENT'))

players = posInt('\nPlease enter the number of players (<= 17): ')
rounds = 0
while True:
    rounds = posInt('Please enter the number of rounds: ')
    if rounds % players == 0:
        print('Number of rounds cant be divisible by number of players')
    else:
        break

ClientSocket.sendall(str.encode(str(players).zfill(3) + str(rounds).zfill(3)))

print('Data sent to the casino server')

# close the connection
ClientSocket.close()
