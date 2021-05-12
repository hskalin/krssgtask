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

        if val<0:
            print("please enter a positive integer")
        else:
            break
    return val

# takes and checks user input
def userInput():
    inputList = []

    while True:
        try:
            inputList = [int(x) for x in input('Input ').split()]
        except ValueError:
            print('Please enter integers')
            continue

        if len(inputList) != 8:
            print('Please enter 8 numbers separated by space')
        else:
            break

    inputStr = ''
    for i in range(len(inputList)):
        inputStr += str(inputList[i]) + ' '

    return inputStr


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
print('Connecting to the server ...')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))
    exit(1)

print("Connected to the server") 

t = -1

# main client loop
while True:
    # get message from the server
    resp = ClientSocket.recv(1024).decode('utf-8')

    # return time steps
    if resp == 'TIMESTEPS':
        t = posInt('Time steps t : ')
        ClientSocket.sendall(str.encode(str(t)))

    # return the user input
    elif resp == 'INPUT':
        ClientSocket.sendall(str.encode(userInput()))
        t = t - 1

    if t == 0:
        break


# close the connection
ClientSocket.close()
