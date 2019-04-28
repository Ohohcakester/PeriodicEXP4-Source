import networkx as nx
import csv
from copy import deepcopy
import os
import problem_instance_v2
from termcolor import colored
import pickle
from utility_method import computeNashEquilibriumState, saveToCsv
import global_setting
from statistics import median

numDevice = 20
numTimeSlot = 86400
numRepeat = 60
numRun = 20
problem_instance = "mobility_setup3"
algorithmName = "EXP4"
rootDir = "/media/cirlab/SeagateDrive/PeriodicEXP3/" + problem_instance + "/" + algorithmName + "/"
DISTANCE_TYPE = "PERCENTAGE"

# networkGraph = nx.DiGraph()

def buildGraph(networkIDlist, devicePerNetwork, deviceListPerNetwork):
    '''
    description: build a graph of networks; vertices are networks and edges represent the possibility of devices moves from one network to the other;
                 the attribute of an edge list the set of devices that can move between the two networks
    args:        list of networks available, set of devices that selected each each network (devicePerNetwork), list of devices that have access to each network (deviceListPerNetwork)
    return:      graph of networks and devices along the edges
    '''
    networkGraph = nx.DiGraph()                 # create a directed graph
    networkGraph.add_nodes_from(networkIDlist)  # add the vertices; these are the set of networks
    # add the edges and attribute 'device_list' on each edge which is the set of devices that can switch transition between the vertices
    for fromNetworkID in range(1, len(deviceListPerNetwork) + 1):       # for each network
        deviceChosenNetwork = devicePerNetwork[fromNetworkID - 1]; deviceAccessToNetwork = deviceListPerNetwork[fromNetworkID - 1]
        # print("deviceChosenNetwork:", deviceChosenNetwork, ", deviceAccessToNetwork:", deviceAccessToNetwork)
        for deviceID in deviceChosenNetwork:                                                            # for each device that selected that network
            availableNetwork = [x for x in networkIDlist if deviceID in deviceListPerNetwork[x - 1] ]   # get list of networks available to the device
            # print("device", deviceID, ", available network ", availableNetwork)
            for toNetworkID in availableNetwork:
                if fromNetworkID != toNetworkID:
                    # add an edge to each network the device has access to and the device ID to the set on the edge
                    if not networkGraph.has_edge(fromNetworkID,toNetworkID):
                        networkGraph.add_edge(fromNetworkID, toNetworkID)
                        networkGraph[fromNetworkID][toNetworkID]['device_list'] = set()
                    networkGraph[fromNetworkID][toNetworkID]['device_list'].add(deviceID)
    return networkGraph
    # end buildGraph

def sortNetworkList(networkIDlist, networkGraph):
    '''
    description: sorts the list of network ID in ascending order based on their accessibility, i.e. devices from how many networks can have access to it; based on indegree of vertices
    args:        list of network ID, graph of networks and devices
    return:      sorted list of network IDs
    '''
    # reference: https://stackoverflow.com/questions/48382575/sort-graph-nodes-according-to-their-degree
    sortedNetworkIDlist = sorted(networkGraph.in_degree, key=lambda x: x[1])    # list of (networkID, indegree) tuples sorted in ascending order of vertex indegree, e.g. [(1,2), (2,3)]
    sortedNetworkIDlist = [x[0] for x in sortedNetworkIDlist]                   # get a list of network ID from the above list of tuples, e.g. [1, 2]
    return sortedNetworkIDlist
    # end sortNetworkList

def getDeviceToMove(fromNetworkID, deviceList, problem_instance, currentTimeSlot, networkDataRate, numDevicePerNetwork):
    '''
    description: finds the next device to move from its current network; e.g., if giving priority to devices that selected
                 a network not accessible to it
    args:        ID of network from which device has to be moved, the list of devices that can be considered, name of
                 problem instance being considered, the current time slot
    return:      ID of device to move from the network, current gain of the device
    '''
    deviceID = -1
    for device in deviceList:
        # print("problem_instance:", problem_instance, ", currentTimeSlot:", currentTimeSlot, ", fromNetworkID:",fromNetworkID, ", device:", device)
        if deviceID == -1: deviceID = device
        # try: problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, fromNetworkID, device)
        # except: print("exception in getDeviceToMove"); input()
        if not problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, fromNetworkID, device):
            return device, 0
    # to handle case when the device was just transitting through the current network and the number of devices that was associated to the device is zero
    if numDevicePerNetwork[fromNetworkID - 1] == 0: print(colored("time: " + str(currentTimeSlot) + ", deviceID: " + str(deviceID) + " from " + str(fromNetworkID), "red"))
    dataRate = networkDataRate[fromNetworkID - 1]/numDevicePerNetwork[fromNetworkID - 1] if numDevicePerNetwork[fromNetworkID - 1] > 0 else 0
    return deviceID, dataRate
    # end getDeviceToMove

def moveDevice(networkOnPath, maxNumDeviceToMove, networkGraph, problem_instance, currentTimeSlot, networkDataRate, numDevicePerNetwork, NE):
    '''
    description:
    args:        ID of network from which to move device(s), ID of network to which to move device(s), networks on the path
                 between fromNetworkID and toNetworkID, maximum number of device that can possibly be moved, the network
                 of networks and devices
    return:      number of devices that can be moved along the path, the movements of devices
    '''
    moveSet = {}        # store all the moves; compute the change in gain at the end because a device might move more than once - but a single distance must be considered

    # find the number of devices that can be moved along the path
    # print("networkOnPath:", networkOnPath   )
    numDeviceToMove = maxNumDeviceToMove; fromNetwork = networkOnPath[0]
    for toNetwork in networkOnPath[1:]:
        # print("from", fromNetwork, "to", toNetwork, "deviceList:", networkGraph[fromNetwork][toNetwork]['device_list'])
        numDeviceToMove = min(numDeviceToMove, len(networkGraph[fromNetwork][toNetwork]['device_list']))
        fromNetwork = toNetwork
    ##### print("to move", numDeviceToMove, "from network", networkOnPath[0], " to network", networkOnPath[-1])

    # get the device to move and save details about the movement in moveSet; consider moving those who selected a network not accessible to them first (i.e., those with gain zero)
    fromNetwork = networkOnPath[0]; deviceMovedList = []
    # print("edges:", networkGraph.edges, ", networkOnPath:", networkOnPath, ", numDeviceToMove:", numDeviceToMove)
    for toNetwork in networkOnPath[1:]:     # consider every edge along the path between fromNetworkID and toNetworkID
        for deviceID in deviceMovedList:
            if problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, toNetwork, deviceID): networkGraph[fromNetwork][toNetwork]['device_list'].add(deviceID)   # see below (*)
        for i in range(numDeviceToMove):
            # print("from:", fromNetwork, "to", toNetwork, "edges:", networkGraph.edges)
            deviceID, currentGain = getDeviceToMove(fromNetwork, networkGraph[fromNetwork][toNetwork]['device_list'], problem_instance, currentTimeSlot, networkDataRate, numDevicePerNetwork)
            ##### print("moving device ", deviceID, "from network", fromNetwork, "to network", toNetwork, "along path", networkOnPath)
            if deviceID not in moveSet:
                moveSet.update({deviceID:{}})
                moveSet[deviceID].update({'currentGain': currentGain})
                moveSet[deviceID].update({'network': toNetwork})
            else: moveSet[deviceID].update({'network': toNetwork})
            # remove the device from current fromNetwork to all networks - to be added to the next edge on the path in the next iteration (*)
            for tmpToNetwork in range(1, len(networkDataRate) + 1):
                if networkGraph.has_edge(fromNetwork, tmpToNetwork) and deviceID in networkGraph[fromNetwork][tmpToNetwork]['device_list']:
                    networkGraph[fromNetwork][tmpToNetwork]['device_list'].remove(deviceID)
                    if networkGraph[fromNetwork][tmpToNetwork]['device_list'] == set(): networkGraph.remove_edge(fromNetwork, tmpToNetwork)  # remove edge if no device on the edge
            # networkGraph[fromNetwork][toNetwork]['device_list'].remove(deviceID)
            # if networkGraph[fromNetwork][toNetwork]['device_list'] == set(): networkGraph.remove_edge(fromNetwork, toNetwork)  # remove edge if no device on the edge
            # if networkGraph.has_edge(fromNetwork, toNetwork): print("left of edge:", networkGraph[fromNetwork][toNetwork]['device_list'])
            deviceMovedList.append(deviceID)    # to be added to the next edge on the path, in case it needs to move across the next edge along the path
        fromNetwork = toNetwork                 # update fromNetwork for the next iteration if the path length is greater than 1

    # update the graph based on the movement of the device(s)
    for device in moveSet:
        fromNetwork = moveSet[device]['network']
        for network in range(1, len(networkDataRate) + 1):
            if network != fromNetwork and problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, network, device):
                if not networkGraph.has_edge(fromNetwork, network):
                    networkGraph.add_edge(fromNetwork, network)
                    networkGraph[fromNetwork][network]['device_list'] = set()
                if device not in networkGraph[fromNetwork][network]['device_list']: networkGraph[fromNetwork][network]['device_list'].add(device)
    return numDeviceToMove, moveSet
    # end moveDevice

def chooseBestNashEquilibriumState(NElist, numDevicePerNetwork):
    '''
    description: select the NE state to be considered based on the number of devices to move from/to each network to reach each of the NE states
    args:        list of NE states (basically the number of devices in each network at that state), current number of devices per network
    return:      the NE state to consider (the one requiring the least number of devices to change network)
    '''
    countNumDeviceToMove = []                                           # number of devices to move to reach each NE state
    for NEstate in NElist:
        numDeviceDiff = list(numDeviceAtNE - numDeviceAtPresent for numDeviceAtNE, numDeviceAtPresent in zip(NEstate, numDevicePerNetwork))
        countNumDeviceToMove.append(sum(x for x in numDeviceDiff if x > 0))
    minNumDeviceToMove = min(countNumDeviceToMove)
    return NElist[countNumDeviceToMove.index(minNumDeviceToMove)]
    # end selectNashEquilibriumState

def computeDistanceToNashEquilibrium(problem_instance, numTimeSlot, networkData, numDevice):
    '''
    description: computes the distance to Nash equilibrium per time slot and returns it as a list
    args:        name of the problem instance being considered, the total number of time slots, details about the network for each time slot
    return:      list of distance to Nash equilibrium per time slot
    '''

    # print(networkData); input()
    distanceToNE = []       # to store distance to Nash equilibrium per time steps for one run
    networkDataRate = []; numNetwork = len(networkDataRate); networkIDlist = []; deviceListPerNetwork = []; NElist = []

    f = open('networkDataRate.pkl', 'rb')  # 'r' for reading; can be omitted
    dataRatePickle = pickle.load(f)  # load file content as mydict
    f.close()

    for row in networkData: # each time slot
        ##### print("row:", row)
        timeSlot = int(row[1])

        # if there is a change in the environment in the current time slot, retrieve details for the current time slot from definition of problem instance;
        # list of data rates (hence, number of networks), list of devices that can access each network, Nash equilibrium state(s)
        if problem_instance == "continuous" or problem_instance_v2.changeInEnvironment(problem_instance, timeSlot):
            if problem_instance == "continuous":
                dataRateIndex = (timeSlot - 1) % len(dataRatePickle[0]); networkDataRate = [dataRatePickle[x][dataRateIndex] for x in range(len(dataRatePickle))]
                numNetwork = len(networkDataRate)
                NElist = computeNashEquilibriumState(numDevice, numNetwork, networkDataRate)
                # print("dataRateIndex:", dataRateIndex, ", networkDataRate:", networkDataRate)
            else:
                networkDataRate = problem_instance_v2.getNetworkDataRate(problem_instance, timeSlot); numNetwork = len(networkDataRate)
                NElist = problem_instance_v2.getNashEquilibriumState(problem_instance, timeSlot)
            networkIDlist = list(range(1, numNetwork + 1))
            deviceListPerNetwork = problem_instance_v2.getDeviceListPerNetwork(problem_instance, timeSlot)
        # print("t = ", timeSlot, ", bit rate:", networkDataRate, ", NE list:", NElist); #input()

        numDevicePerNetwork = [row[3 + i] for i in range(numNetwork)]                       # construct list with number of devices per network
        devicePerNetwork = [row[3 + 2 * numNetwork + i] for i in range(numNetwork)]         # construct list of sets of devices that selected each network
        networkGraph = buildGraph(networkIDlist, devicePerNetwork, deviceListPerNetwork)    # build graph of networks and devices
        sortedNetworkIDList = sortNetworkList(networkIDlist, networkGraph)                  # sort list of network IDs in order of accessibility

        numDeviceDiff = []
        # compute the distance from the current state to Nash equilibrium
        if numDevicePerNetwork in NElist: distance = 0  # current state is one of the Nash equilibrium state(s)
        else:  # current state is not any of the Nash equilibrium state(s)
            distance = 0; moveSet = {}
            NE = chooseBestNashEquilibriumState(NElist, numDevicePerNetwork)    # select the NE state requiring the least number of device switches

            # compute the number of devices to move from/to each network
            numDeviceDiff = list(numDeviceAtNE - numDeviceAtPresent for numDeviceAtNE, numDeviceAtPresent in zip(NE, numDevicePerNetwork)); ##### print("numDeviceDiff:", numDeviceDiff)
            ##### print(">>>>> t = ", timeSlot, ", NE:", NE, ", numDeviceDiff:", numDeviceDiff)
            pathLength = 1  # start by trying to switch devices to another network by following a path of length 1, i.e., directly moving it to another network
            while any(x < 0 for x in numDeviceDiff): # and pathLength < numNetwork:
                totalNumMoves = 0
                if pathLength == numNetwork: pathLength = 1
                for i in range(len(numDeviceDiff)):                             # i = 0, 1, ..., numNetwork-1
                    fromNetworkID = sortedNetworkIDList[i]                      # consider networks in sorted order
                    if numDeviceDiff[fromNetworkID - 1] < 0:                    # check if device(s) must be moved from network with ID fromNetworkID
                        j = 0
                        while j < len(numDeviceDiff):
                            toNetworkID = sortedNetworkIDList[j]
                            if numDeviceDiff[toNetworkID - 1] > 0:              # check if device(s) must be moved to network with ID toNetworkID
                                # at this point, we have identified a network from which device(s) has/have to be moved and a network to which device(s) has/have to be moved
                                # get the length of the shortest path from network fromNetworkID to network toNetworkID
                                try: networkOnPath = nx.shortest_path(networkGraph, fromNetworkID, toNetworkID)
                                except nx.NetworkXNoPath: networkOnPath = [];
                                if (len(networkOnPath) - 1) == pathLength:  # the length is equal to the current length being considered
                                    ##### print("path:", networkOnPath)
                                    maxNumDeviceToMove = min(numDeviceDiff[toNetworkID - 1], abs(numDeviceDiff[fromNetworkID - 1]))   # max number of devices that can possibly be moved between the networks
                                    numDeviceToMove, tmpMoveSet = moveDevice(networkOnPath, maxNumDeviceToMove, networkGraph, problem_instance, timeSlot, networkDataRate, numDevicePerNetwork, NE)
                                    # merge moveSet and tmpMoveSet
                                    for device in tmpMoveSet:
                                        if device in moveSet: moveSet[device]['network'] = tmpMoveSet[device]['network']
                                        else: moveSet.update({device:tmpMoveSet[device]})
                                    numDeviceDiff[fromNetworkID - 1] += numDeviceToMove; numDeviceDiff[toNetworkID - 1] -= numDeviceToMove; totalNumMoves += numDeviceToMove
                                    # no more devices to move from network fromNetworkID, compute how much higher gain the remaining devices in that network will get
                                    if numDeviceDiff[fromNetworkID - 1] == 0:
                                        if NE[fromNetworkID - 1] != 0:
                                            currentGain = networkDataRate[fromNetworkID - 1] / numDevicePerNetwork[fromNetworkID - 1]
                                            gainAtNE = networkDataRate[fromNetworkID - 1] / NE[fromNetworkID - 1]
                                            tmpDistance = ((gainAtNE - currentGain) * 100/gainAtNE) if DISTANCE_TYPE == "PERCENTAGE" else gainAtNE - currentGain
                                            ##### print("tmpDistance users left in network ", fromNetworkID, "=", tmpDistance)
                                            if tmpDistance > distance: distance = tmpDistance;
                                        break
                            j += 1
                pathLength += 1
                # if totalNumMoves == 0 and pathLength == numNetwork: break
            # compute distance based on the set of moves of devices
            for device in moveSet:
                destinationNetwork = moveSet[device]['network']; currentGain = moveSet[device]['currentGain']
                gainAtNE = networkDataRate[destinationNetwork - 1] / NE[destinationNetwork - 1]
                tmpDistance = (gainAtNE - currentGain) * 100/gainAtNE if DISTANCE_TYPE == "PERCENTAGE" else gainAtNE - currentGain
                if tmpDistance > distance: distance = tmpDistance
                ##### print(device, moveSet[device], "currentGain:", currentGain, ", gainAtNE:", gainAtNE, ", tmpDistance:", tmpDistance)
        distanceToNE.append(distance); #####input()
        ##### print("distance:", distance); #input()
        if any(x < 0 for x in numDeviceDiff): print("@", timeSlot, "--- numDeviceDiff:", numDeviceDiff, ", SOMETHING WENT WRONG!!!"); input()
    return distanceToNE
    # end computeDistanceToNashEquilibrium

def extractDataFromFile(inputCSVfile):
    networkData = []
    with open(inputCSVfile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count = 0
        for row in csv_reader:
            # row: ['1', '1', '1', '7', '7', '6', '7', '14', '44', '{1, 2, 4, 10, 12, 13, 20}', '{3, 5, 6, 9, 14, 17, 19}', '{7, 8, 11, 15, 16, 18}']
            if count > 0:
                for i in range(len(row)):
                    element = row[i]
                    if element == 'set()': row[i] = set()
                    elif '.' in element: row[i] = float(element)
                    elif '{' in element:
                        userList = set()
                        row[i] = row[i][1:-1]; row[i] = row[i].split(','); row[i] = [int(x) for x in row[i]];
                        for user in row[i]: userList.add(user)
                        row[i] = userList
                    else: row[i] = int(row[i])
                networkData.append(row)
            count += 1
    csv_file.close()
    return networkData
    # end extractDataFromFile

def main():
    distanceToNE_perRun = []

    global_setting.constants.update({'num_mobile_device': numDevice})
    global_setting.constants.update({'num_time_slot': numTimeSlot})
    global_setting.constants.update({'num_repeats': numRepeat})

    problem_instance_v2.initialize()

    # for each run, compute the distance to Nash equilibrium
    for runIndex in range(1, numRun+1):
        runDir = rootDir + "run" + str(runIndex) + "/"
        # load the network details from csv file
        networkData = extractDataFromFile(runDir + "network.csv")
        # call the function to compute the distance to Nash equilibrium
        distancetoNE = computeDistanceToNashEquilibrium(problem_instance, numTimeSlot, networkData, numDevice)
        # print(distancetoNE)
        saveToCsv(runDir + "distanceToNE_percentage.csv", ["timeslot", "distance"], [[timeIndex + 1, distancetoNE[timeIndex]] for timeIndex in range(len(distancetoNE))])
        distanceToNE_perRun.append(distancetoNE)
        print("done run", runIndex)

    # compute median distance over runs
    distanceToNE_combined = []
    for j in range(len(distanceToNE_perRun[0])):
        # print("i=", j)
        distanceToNE_combined.append(median([distanceToNE_perRun[i][j] for i in range(len(distanceToNE_perRun))]))

    # print(distanceToNE_combined)
    saveToCsv(rootDir + "distanceToNE_percentage_median.csv", ["timeslot", "distance"], [[timeIndex + 1, distanceToNE_combined[timeIndex]] for timeIndex in range(len(distanceToNE_combined))])
    # end main

if __name__ == '__main__': main()