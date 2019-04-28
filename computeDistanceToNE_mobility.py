import csv
from copy import deepcopy
from networkx import NetworkGraph
import os
import argparse

parser = argparse.ArgumentParser(description='Simulates the wireless network selection by a number of wireless devices in the service area.')
parser.add_argument('-n', dest="num_device", required=True, help='number of active devices in the service area')
parser.add_argument('-k', dest="num_network", required=True, help='number of wireless networks in the service area')
parser.add_argument('-dir', dest="directory", required=True, help='root directory containing the simulation files')
parser.add_argument('-t', dest="num_time_slot", required=True, help='number of time slots in the simulation run')
parser.add_argument('-r', dest="number_of_run", required=True, help='number of runs')
parser.add_argument('-pr', dest="number_of_parallel_run", required=True, help='number of parallel runs')
parser.add_argument('-p', dest="current_phase", required=True, help='current phase')
parser.add_argument('-ne', dest="nash_equilibrium_state_list", required=True, help='list of Nash equilibrium states')
parser.add_argument('-u', dest="device_list", required=True, help='list of devices being considered')
parser.add_argument('-b', dest="network_bandwidth", required=True, help='total bandwidth of each network as a string separated with "_".')
args = parser.parse_args()

numUser = int(args.num_device)
numNetwork = int(args.num_network)
dir = args.directory
MAX_NUM_ITERATION = int(args.num_time_slot)
numRun = int(args.number_of_run)
numParallelRun = int(args.number_of_parallel_run)
currentPhase = int(args.current_phase)
NE = args.nash_equilibrium_state_list.split(","); NE = [int(x) for x in NE]
userBeingConsideredList = args.device_list.split(","); userBeingConsideredList = [int(x) for x in userBeingConsideredList]
NETWORK_BANDWIDTH = args.network_bandwidth.split("_"); NETWORK_BANDWIDTH = [int(x) for x in NETWORK_BANDWIDTH]

NETWORK_ID = [2, 3, 4, 5, 1] # network ID in ascending order of accessibility (users from how many networks can have access to it)
numMobileUser = 8   # number of users moving
DEBUG = 0   # 0 - no output; 1 - print details of computations; 2 - print details of computations and wait for user to press enter after each run is processed

outputDir = dir # + "extractedData/"
if os.path.exists(outputDir) == False: os.makedirs(outputDir)
# outputCSVfile_allRuns = outputDir + "distanceToNE_allRuns.csv"

CURRENT_PHASE = "PHASE_" + str(currentPhase)
iterationNumOffset = (MAX_NUM_ITERATION) * (currentPhase - 1)
# print("currentPhase:", currentPhase, ", iterationNumOffset", iterationNumOffset)
outputCSVfile_allRuns = outputDir + "distanceToNE_avgAllRuns_phase_" + str(currentPhase) + "_users" + str(userBeingConsideredList[0]) + "_" + str(userBeingConsideredList[-1]) + ".csv"

epsilon = 7.5

DEBUG = 0

''' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ '''
def computeDistanceToNE():
    '''
    @desc:      at each iteration of every run, computes the distance of the current state to Nash equilibrium
    @param:     none
    @returns:   list of distances to Nash equilibrium for each iteration (averaged over all runs), string containing all epsilon equilibrium points
    '''

    distanceToNE_avgAllRuns = [0] * MAX_NUM_ITERATION               # to store distance to NE per time steps (averaged over all runs)
    epsilonEquilibriumPoints = ""                                   # stores list of epsilon equilibrium points; may be used if plot is required
    availableNetworkPerUser = buildAvailableNetworkPerUserList()
    sortedUserList = sortUserListAscNumAvailableNetwork(availableNetworkPerUser)

    for j in range(numRun):
        # create list to store distance to NE per time steps (for individual runs)
        distanceToNE_perRun = [0] * MAX_NUM_ITERATION

        networkCSVfile = dir + "run" + str(j + 1) + "/" + CURRENT_PHASE + "/network.csv"
        with open(networkCSVfile, newline='') as networkCSVfile:
            networkReader = csv.reader(networkCSVfile)
            count = 0

            for rowNetwork in networkReader:  # compute total gain of user and that of each expert
                if count != 0:
                    #print("rowNetwork:", rowNetwork)
                    runNum = int(rowNetwork[0])
                    iterationNum = int(rowNetwork[1])
                    numUserPerNet = []

                    for i in range(numNetwork): numUserPerNet.append(int(rowNetwork[3 + i])) # construct list with number of users per network

                    # construct list of users per network
                    userListPerNet = []
                    for i in range(numNetwork):
                        userListCurrentNet = []
                        userListCurrentNetStr = rowNetwork[3 + numNetwork + i]
                        if userListCurrentNetStr != "set()":
                            userListCurrentNetStrSplit = userListCurrentNetStr[1:-1].split(", ")
                            for ID in userListCurrentNetStrSplit: userListCurrentNet.append(int(ID))

                        userListCurrentNetSorted = sortUserListAscNumAvailableNetwork(availableNetworkPerUser, userListCurrentNet)
                        userListPerNet.append(userListCurrentNetSorted)

                    # construct graph of networks and users
                    networkGraph = buildNetworkGraph(numNetwork, numUser, availableNetworkPerUser, userListPerNet)

                    distance = computeDistance(iterationNum, numUserPerNet, userListPerNet, availableNetworkPerUser, networkGraph)

                    distanceToNE_perRun[iterationNum - iterationNumOffset- 1] = distance
                    distanceToNE_avgAllRuns[iterationNum - iterationNumOffset - 1] += distance
                count += 1
        print("done for run" + str(j + 1) + " - phase " + str(currentPhase))
        savePerRunCSVfile((j + 1), distanceToNE_perRun)

    distanceToNE_avgAllRuns = [distance/(numParallelRun * numRun) for distance in distanceToNE_avgAllRuns]  # compute the average
    for i in range(len(distanceToNE_avgAllRuns)):
        if distanceToNE_avgAllRuns[i] <= epsilon:
            if epsilonEquilibriumPoints == "": epsilonEquilibriumPoints += str(i + 1)
            else: epsilonEquilibriumPoints += "," + str(i + 1)

    return distanceToNE_avgAllRuns, epsilonEquilibriumPoints

''' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ '''
def buildAvailableNetworkPerUserList():
    '''
    @desc:      constructs the list of networks available to each user
    @param:     none
    @returns:   list consisting of sub-lists representing list of networks available to each user
    '''

    availableNetworkPerUser = []

    for i in range(1, numMobileUser + 1):
        if currentPhase == 1: availableNetworkPerUser.append([1, 2, 3])
        elif currentPhase == 2: availableNetworkPerUser.append([1, 3, 4, 5])
        else: availableNetworkPerUser.append([1, 4, 5])
    for i in range(numMobileUser + 1, 11):
        availableNetworkPerUser.append([1, 2, 3])
    for i in range(11, 16):
        availableNetworkPerUser.append([1, 3, 4, 5])
    for i in range(16, 21):
        availableNetworkPerUser.append([1, 4, 5])

    return availableNetworkPerUser

''' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ '''
def sortUserListAscNumAvailableNetwork(availableNetworkPerUserList, userIDlist = list((i + 1) for i in range(numUser))):
    '''
    @desc: sorts a list of users in ascending order of number of networks available to them
    @param: list of available networks per user, list of users to sort in ascending order of number of networks available to them
    @returns: list of users to sort in ascending order of number of networks available to them
    '''
    availableNetworkPerUser = list(availableNetworkPerUserList[ID - 1] for ID in userIDlist) # construct a list of available networks for users in list userIDlist
    availableNetworkPerUserCopy = deepcopy(availableNetworkPerUser)
    sortedUserList = []     # resulting list of users sorted in asc order of the number of networks available
    availableNetworkPerUserSortedList = sorted(availableNetworkPerUserCopy, key=len) # sorted in ascending order of list (elements) size
    for elem in availableNetworkPerUserSortedList:
        elemIndexOriginalList = availableNetworkPerUserCopy.index(elem)
        if len(availableNetworkPerUserSortedList) > 1: availableNetworkPerUserSortedList = availableNetworkPerUserSortedList[1:]
        else: availableNetworkPerUserSortedList = []
        availableNetworkPerUserCopy[elemIndexOriginalList] = [-1] # so that index doesn't return the same index next time
        sortedUserList.append(userIDlist[elemIndexOriginalList])
    return sortedUserList

''' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ '''
def buildNetworkGraph(numNetwork, numUser, availableNetworkPerUser, userListPerNet): # ???numUser???
    networkGraph = NetworkGraph([(i + 1) for i in range(numNetwork)], []) # build graph, initializing the list of network ID
    for netIndex in range(len(userListPerNet)): # for each network
        netID = netIndex + 1
        for userID in userListPerNet[netIndex]:    # for each user in the specific network
            userIndex = userID - 1
            # get networks available to the user
            availableNetList = availableNetworkPerUser[userIndex]

            # create an edge between the current network and each of the network to which the user can go, if it does not exist
            for availableNetID in availableNetList:
                if availableNetID != netID:
                    if networkGraph.edgeExist(netID, availableNetID) == False: networkGraph.addEdge(netID, availableNetID, [userID])
                    else: networkGraph.addUserToEdge(netID, availableNetID, userID)

    for edge in networkGraph.edges: sortUserListAscNumAvailableNetwork(availableNetworkPerUser, edge.userList) # sort list of users
    return networkGraph
    # end buildNetworkGraph

''' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ '''
def findNetToMoveTo(currentNetIndex, numUserDiff):
    '''
    @desc:         gets ID of the next network to which users must be moved
    @input:        current index in network list, number of users to be moved from/to for each network
    @returns:     index of network to which users must be moved
    '''
    index = currentNetIndex
    while index < len(numUserDiff):
        #if numUserDiff[index] > 0:
        if numUserDiff[NETWORK_ID[index] - 1] > 0:  # the networks are considered in ascending order of accessibility (as per order in list NETWORK_ID)
            return NETWORK_ID[index]    # index iterates over list NETWORK_ID
        index += 1
    return -1

''' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ '''
def transferUser(fromNetID, toNetID, verticesAlongPath, networkGraph, maxNumUserToBeMoved, numUserPerNet, userListPerNet):

    distance = 0

    # find the minimum number of users who can be moved along the edges
    fromVertex = fromNetID
    toVertex = verticesAlongPath[1]
    for edge in networkGraph.edges:   # get number of users along edge(   fromVertex, toVertex)
        if edge.sourceVertex == fromVertex and edge.destinationVertex == toVertex:
            numUsersOnEdge = len(edge.userList)
            break
    numUserMoved = min(maxNumUserToBeMoved, numUsersOnEdge)

    if DEBUG >= 1: print("-----> in transferUser; fromNetID:", fromNetID, ", toNetID:", toNetID, ", totalNumUserToBeMoved: ", maxNumUserToBeMoved, ", number of users who can be moved: ", numUserMoved, "; pathLength: ", verticesAlongPath, "---", len(verticesAlongPath))
    prevVertex = fromNetID
    for vertex in verticesAlongPath[1:]:  # ignore the start vertex
        if DEBUG >= 1: print("considering edge ", prevVertex, "to", vertex)
        for edge in networkGraph.edges[::-1]:  # get number of users along edge(prevVertex, vertex)
            if edge.sourceVertex == prevVertex and edge.destinationVertex == vertex: # edge along which user will be moved
                if DEBUG >= 1: print("going to move", numUserMoved, "from edge (", prevVertex,",", vertex,") with user list", edge.userList)
                for i in range(numUserMoved): # move 'numUserMoved' users
                    userBeingMoved = edge.userList[0]
                    networkGraph.removeUserFromEdge(prevVertex, vertex, userBeingMoved)

                    ##### remove the user from the network so that I know who is/are in the network to know if their distance must be considered...
                    if DEBUG >= 1: print("user being moved from network", prevVertex, ": ", userBeingMoved, ", userListPerNet[",prevVertex - 1,"]: ",  userListPerNet[prevVertex - 1], " to network", vertex ," : userListPerNet:", userListPerNet)
                    userListPerNet[prevVertex - 1].remove(userBeingMoved)
                    userListPerNet[vertex - 1].append(userBeingMoved)

                    # path length > 1, add the users moved to the set of outgoing edges of the intermediary network
                    if (len(verticesAlongPath) - 1) > 1:
                        for edgeIntermediaryNet in networkGraph.edges[::-1]:
                            if edgeIntermediaryNet.sourceVertex == vertex: networkGraph.addUserToEdge(edgeIntermediaryNet.sourceVertex, edgeIntermediaryNet.destinationVertex, userBeingMoved)

                    #print("@@@ moving user", userBeingMoved, "from network", prevVertex, "to network", vertex)

                prevVertexIndex = prevVertex - 1
                vertexIndex = vertex - 1
                oldGain = NETWORK_BANDWIDTH[prevVertexIndex]/numUserPerNet[prevVertexIndex]
                newGain = NETWORK_BANDWIDTH[vertexIndex]/NE[vertexIndex]

                ##### include distance only if the user is being considered
                tmpDistance = (newGain - oldGain) * 100 / oldGain
                #print("tmpDistance: ", tmpDistance, ", moving user", userBeingMoved, "from network", prevVertex, "to network", vertex)
                if isUserBeingConsidered([userBeingMoved]):
                    if tmpDistance > distance: distance = tmpDistance
                    #print("tmpDistance is taken into consideration, distance = ", distance)
                #else:
                    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~Will not consider distance...; user being moved is ", userBeingMoved)#; input()
        prevVertex = vertex
    if DEBUG >= 1: print("updated graph: ", networkGraph)
    #print("distance being returned:", distance)
    return numUserMoved, distance
    # end transferUser

''' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ '''
def isUserBeingConsidered(uList):
    for user in uList:
        if user in userBeingConsideredList: return True
    return False
    # end isUserBeingConsidered

''' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ '''
def computeDistance(iterationNum, numUserPerNet, userListPerNet, availableNetworkPerUser, networkGraph):
    '''
    @desc:       computes the distance of a particular state from Nash equilibrium
    @param:    the iteration number in the run being processed, list of users in ascending  order of number of networks available, number
                      of users per network, list of users per network (user ID), networks available to each user
    returns:     distance of the particular state from Nash equilibrium
    '''
    # compute the distance from the current state to NE as sum of all additional bandwidth obtainable by the users by moving to NE state
    distance = 0
    numUserDiff = [] # only for the print statement at end of the function...

    if numUserPerNet != NE:  # current state is not NE
        distance = 0

        numUserDiff = list(numUserAtNE - numUserAtPresent for numUserAtNE, numUserAtPresent in zip(NE, numUserPerNet))


        #print("NE:", NE ,"; numUserPerNet: ", numUserPerNet)
        #print("numUserDiff: ", numUserDiff)

        currentPathLength = 1
        while any(x < 0 for x in numUserDiff) and currentPathLength < numNetwork:
            # find network from which to move user(s), fromNetID at index fromNetIndex
            # for fromNetIndex in range(len(numUserDiff)):
            for i in range(len(numUserDiff)):
                fromNetID = NETWORK_ID[i]
                fromNetIndex = fromNetID - 1    # iterate over networks in ascending order of accessibility

                if numUserDiff[fromNetIndex] < 0:  # need to move user from this network
                    totalNumUserToBeMoved = abs(numUserDiff[fromNetIndex])  # total number to be moved from the network
                    #print("totalNumUserToBeMoved from network ", fromNetID, " is ", totalNumUserToBeMoved)

                    toNetStartIndex = 0
                    while totalNumUserToBeMoved > 0 and toNetStartIndex < numNetwork:  # not reached end of the list, can still check if
                        # find network to which to move user(s)
                        toNetID = findNetToMoveTo(toNetStartIndex, numUserDiff)
                        if DEBUG >= 1: print("going to check transfer from network", fromNetID, "to network", toNetID, "going to break?", toNetID == -1)
                        if toNetID == -1:
                            if DEBUG >= 1: print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> cannot transfer!!!")
                            break
                        toNetIndex = toNetID - 1
                        pathLength, verticesAlongPath = networkGraph.shortestPath(fromNetID, toNetID)
                        if DEBUG >= 1: print("trying to move users from network ", fromNetID, "to network", toNetID, ", currentPathLength: ", currentPathLength, ", path length: ", pathLength, ", vertices along path:", verticesAlongPath)
                        if pathLength == currentPathLength: # number of 'hops' along the path is same as the path length being considered in this iteration
                            maxNumUserToBeMoved = min(totalNumUserToBeMoved, numUserDiff[toNetIndex])
                            numUserMoved, tmpDistance = transferUser(fromNetID, toNetID, verticesAlongPath, networkGraph, maxNumUserToBeMoved, numUserPerNet, userListPerNet)
                            if tmpDistance > distance: distance = tmpDistance ##### just added this line
                            numUserDiff[fromNetIndex] += numUserMoved # it's initially a negative value
                            numUserDiff[toNetIndex] -= numUserMoved  # it's initially a positive value
                            #print("tmpDistance before second condition: ", tmpDistance)
                            if numUserDiff[fromNetIndex] == 0: # all users moved from the network, compute the % higher gain users in that network can get
                                oldGain = NETWORK_BANDWIDTH[fromNetIndex]/numUserPerNet[fromNetIndex]
                                newGain = NETWORK_BANDWIDTH[fromNetIndex]/NE[fromNetIndex]
                                tmpDistance = max( tmpDistance, (newGain - oldGain) * 100 / oldGain)
                                #print("oldGain: ", oldGain, ", newGain:", newGain, ", tmpDistance: ", tmpDistance)
                                #print("tmpDistance after second condition: ", tmpDistance)

                            #print("successfully transferred", numUserMoved, "from network", fromNetID, "to network", toNetID, "; numUserDiff:", numUserDiff, ",tmpDistance:", tmpDistance)

                            ##### include distance only if the user is being considered
                            if isUserBeingConsidered(userListPerNet[fromNetIndex]):
                                if tmpDistance > distance: distance = tmpDistance
                                #print("tmpDistance is taken into consideration, distance = ", distance)
                            #else:
                                #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~Will not consider distance..., user(s) left in the network is/are ", userListPerNet[fromNetIndex]); #input()
                                #if tmpDistance > 45: print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~Will not consider distance..., user(s) left in the network is/are ", userListPerNet[fromNetIndex])
                                #print("tmpDistance: ", tmpDistance)
                            totalNumUserToBeMoved -= numUserMoved
                        #toNetStartIndex = toNetIndex + 1
                        toNetStartIndex = NETWORK_ID.index(toNetID) + 1
                        #input()

            currentPathLength += 1

    #else:  # current state is NE
    #    print("iteration", iterationNum, ", numUserPerNet: ", numUserPerNet, " --- NE")

    if any(x < 0 for x in numUserDiff): print("@", iterationNum, "--- numUserDiff:", numUserDiff, ", SOMETHING WENT WRONG!!!") ; input()
    return distance

''' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ '''
def savePerRunCSVfile(j, distanceToNE_perRun):
    outputCSVfile_singleRun = dir + "run" + str(j) + "/PHASE_" + str(currentPhase) + "/distanceToNE_device" + str(userBeingConsideredList[0]) + "_" + str(userBeingConsideredList[-1]) + ".csv"
    outfile = open(outputCSVfile_singleRun, "w")
    out = csv.writer(outfile, delimiter=',', quoting=csv.QUOTE_ALL)
    out.writerow(["Time step", "Total higher gain observable by a user"])
    for i in range(len(distanceToNE_perRun)): out.writerow([(i + 1), distanceToNE_perRun[i]])
    outfile.close()

''' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ '''
# main program

distanceToNE_avgAllRuns, epsilonEquilibriumPoints = computeDistanceToNE()

outfile = open(outputCSVfile_allRuns, "w")
out = csv.writer(outfile, delimiter=',', quoting=csv.QUOTE_ALL)
out.writerow(["Time step", "Total higher gain observable by a user (average over all runs)"])
for i in range(len(distanceToNE_avgAllRuns)): out.writerow([(i + 1) + iterationNumOffset, distanceToNE_avgAllRuns[i]])
outfile.close()2