import socket
from sys import argv, exit

# INITIALIZING STATES 
# states of light A, D, B, C respectively
# the first number represents "go straight" light and the second "go right"
# 1 represents on and 0 off

# this is the state A's pov
states =    [[1, 1, 0, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 0, 1, 0, 0],
             [1, 0, 0, 0, 1, 0, 0, 0],
             [1, 0, 0, 1, 0, 0, 0, 0]]


# we duplicate the above four times while shifting the elements of a row
# by two positions to get all possible states

def roll(lst, n):
    return lst[n:] + lst[:n]

# duplicating
for i in range(3):
    for j in range(4):
        states.append( roll(states[i*4 +j], 2) )

# rearranging columns in A, B, C, D order
for i in range(16):
    states[i] = states[i][:2] + states[i][4:] + states[i][2:4]




# MISC FUNCTIONS
# this function tries to establish connection
def connectSocket():
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
    serverSocket = socket.socket()
    host = '127.0.0.1'
    port = port

    # try establishing the connection
    try:
        serverSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
        exit(1)

    return serverSocket

# queries the client for the number of timesteps and returns
def getTimeSteps(client):
    client.sendall(str.encode('TIMESTEPS'))
    steps = client.recv(1024).decode('utf-8')

    return int(steps)

# queries the client for the input and returns it
def userInput(client):
    client.sendall(str.encode('INPUT'))
    usrInput = client.recv(1024).decode('utf-8')

    inputList = [int(x) for x in usrInput.split()]
    print(f'User Input: {inputList}')

    return inputList


def printState(state):
    for i in range(4):
        if state[i*2] == 1 and state[i*2 + 1] ==1:
            print(f'{chr(65+i)} - go straight, go right')
        elif state[i*2] == 1:
            print(f'{chr(65+i)} - go straight')
        elif state[i*2 + 1] == 1:
            print(f'{chr(65+i)} - go right')
        else:
            print(f'{chr(65+i)} - off')



# FSM FUNCTIONS
# returns machine input
def machineInput(queue, client, takeUsrInpt):
    if takeUsrInpt:
        # add user input to the queue
        queue = [sum(x) for x in zip(queue, userInput(client))]
    
    return queue

# returns the machine output
def machineOutput(nxtState, inpt):
    # simple return the diff of traffic queue and light states
    # ensures that the traffic que does not have negative elements
    out = []

    for i in range(len(inpt)):
        x = inpt[i] - nxtState[i]
        if x < 0:
            x = 0
        out.append(x)

    return out
    

# TODO
def stateTransition(inpt):
    global states

    # calculate the next state
    indx = 0
    maxIndx = inpt.index(max(inpt))
    mins = sum(machineOutput(states[0], inpt))

    # calculate the state that results in the min number of cars
    # in the queue
    for i in range(len(states)):
        sums = sum(machineOutput(states[i], inpt))
        if mins >= sums:
            indx = i
            mins = sums
        # if 2 cars cross (the max that can) and cars from the lane with max cars
        # cross then select this state and break
        if (sum(inpt) - mins)==2 and states[indx][maxIndx] == 1:
            break

    # update the next state
    nxtState = states[indx]

    # calculate the machine output using the next state
    output = machineOutput(nxtState, inpt)

    # returns the next state and output
    return nxtState, output



def main():
    # CLIENT CONNECTION
    # extablish connection
    server = connectSocket()

    # listen to the connection requests
    server.listen()

    # connect to client
    print('Waiting for the client ...')
    client, addr = server.accept()
    print('Connected to the client\n')


    # INITIALIZING VARIABLES
    # specifies whether to take user input
    takeUsrInpt = True
    # specifies the current traffic queue
    queue = [0]*8
    # specifies the current state. Initialized with some initial state
    curState = states[0]
    # specifies the final queue state
    finalQueue = [0]*8

    # get time steps for user input
    t = getTimeSteps(client)
    step = 1


    # THE FSM LOOP
    while takeUsrInpt or queue != finalQueue:
        if t < step:
            takeUsrInpt = False
        print(f'\nTime step {step} :')

        # takes machine input
        queue = machineInput(queue, client, takeUsrInpt)
        # storing the initial queue
        intQueue = queue

        # execute the state transition function which does the following:
        # (machine input) -> (next state, machine output)
        curState, queue = stateTransition(queue)
        
        printState(curState)

        print(f'Initial queue: {intQueue}')
        print(f'Final queue:   {queue}\n')

        print(f'Cars crossed:  {[(a-b) for (a, b) in zip(intQueue, queue)]}\n')
        
        step += 1

    # closing the connection
    client.close()
    server.close()

main()
