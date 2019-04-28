'''
@description:   Defines utility methods used by other programs (python files)
'''
import csv
from itertools import product
import numpy as np
import problem_instance_v2

''' ___________________________________________________ computes number of devices per network at Nash equilibrium state __________________________________________________ '''
def isNashEquilibrium(combination, numNetwork, bandwidthPerNetwork):
    for i in range(numNetwork):
        for j in range(numNetwork):
            if i != j and combination[i] != 0 and bandwidthPerNetwork[i]/combination[i] < bandwidthPerNetwork[j]/(combination[j] + 1): return False
    return True

def computeNashEquilibriumState(numDevice, numNetwork, bandwidthPerNetwork):
    NashEquilibriumlist = []

    for item in product(range(numDevice + 1), repeat = numNetwork):
        if sum(item) == numDevice:
            if isNashEquilibrium(item, numNetwork, bandwidthPerNetwork):
                NashEquilibriumlist.append(list(item))#; print(item)
    return NashEquilibriumlist

''' ___________________________________________________________________ compute moving average of a list _________________________________________________________________ '''
def computeMovingAverage(values, window):
    ''' source: https://gordoncluster.wordpress.com/2014/02/13/python-numpy-how-to-generate-moving-averages-efficiently-part-2/ '''
    weights = np.repeat(1.0, window) / window
    sma = np.convolve(values, weights, 'valid')
    return sma
    # end computeMovingAverage

''' _________________________________________________________ computes distance to Nash equilibrium per time slot ________________________________________________________ '''
def computeDistanceToNashEquilibrium(problem_instance, numTimeSlot, networkData):
    '''
    description: computes the distance to Nash equilibrium per time slot and returns it as a list
    args:        the problem instance being considered, the total number of time slots, details about the network for each time slot
    return:      list of distance to Nash equilibrium per time slot
    '''
    distanceToNE = []  # to store distance to Nash equilibrium per time steps for one run

    for row in networkData:
        # runNum = row[0]
        timeSlot = int(row[1])

        # get the number of networks and the list of Nash equilibrium states for the current time slot based on the problem instance
        networkDataRate = problem_instance_v2.getNetworkDataRate(problem_instance, timeSlot)
        numNetwork = len(networkDataRate)
        NElist = problem_instance_v2.getNashEquilibriumState(problem_instance, timeSlot)

        # construct list with number of devices per network
        numDevicePerNetwork = []
        for i in range(numNetwork): numDevicePerNetwork.append(row[3 + i])

        # construct set of devices that selected each network
        devicePerNetwork = []
        for i in range(numNetwork): devicePerNetwork.append(row[3 + 2*numNetwork+ i])

        # compute the distance from the current state to Nash equilibrium
        if numDevicePerNetwork in NElist: distance = 0  # current state is one of the Nash equilibrium state(s)
        else:                                           # current state is not any of the Nash equilibrium state(s)
            distance = 0

            # select the NE state to be considered based on the number of devices to move from/to each network to reach each of the NE states
            countNumDeviceToMove = []  # number of devices to move to reach each NE state
            for NEstate in NElist:
                numDeviceDiff = list(numDeviceAtNE - numDeviceAtPresent for numDeviceAtNE, numDeviceAtPresent in zip(NEstate, numDevicePerNetwork))
                countNumDeviceToMove.append(sum(x for x in numDeviceDiff if x > 0))

            minNumDeviceToMove = min(countNumDeviceToMove)
            NEindex = countNumDeviceToMove.index(minNumDeviceToMove)
            NE = NElist[NEindex]

            # compute the number of devices to move from/to each network
            numDeviceDiff = list(numDeviceAtNE - numDeviceAtPresent for numDeviceAtNE, numDeviceAtPresent in zip(NE, numDevicePerNetwork))

            i = 0
            while i < len(numDeviceDiff):
                if numDeviceDiff[i] < 0:            # device(s) need to move from this network
                    for j in range(len(numDeviceDiff)):
                        if numDeviceDiff[j] > 0:    # device(s) need to move to this network
                            maxNumDeviceToMove = min(numDeviceDiff[j], abs(numDeviceDiff[i]))
                            numDeviceToMove, minCurrentGain = getNumDeviceToMove(i+1, j+1, maxNumDeviceToMove, devicePerNetwork, problem_instance, timeSlot)
                            # print("numDeviceToMove:",numDeviceToMove)
                            if numDeviceToMove > 0:
                                # print("i", i, ", j", j, ", numDeviceToMove:", numDeviceToMove, ", NE:", NE)
                                currentGain = 0 if minCurrentGain < 0 else networkDataRate[i]/numDevicePerNetwork[i]
                                tmpDistance = (((networkDataRate[j] / NE[j]) - currentGain)) #* 100 / currentGain
                                if tmpDistance > distance: distance = tmpDistance
                                numDeviceDiff[i] += numDeviceToMove
                                numDeviceDiff[j] -= numDeviceToMove
                        if numDeviceDiff[i] == 0:
                            if NE[i] != 0:
                                currentGain = networkDataRate[i]/numDevicePerNetwork[i]
                                tmpDistance = ((networkDataRate[i]/NE[i] - currentGain)) #* 100 / currentGain
                                if tmpDistance > distance: distance = tmpDistance
                            break
                i += 1
        distanceToNE.append(distance)
    return distanceToNE
    # end computeDistanceToNashEquilibrium

def getNumDeviceToMove(fromNetwork, toNetwork, maxNumDeviceToMove, devicePerNetwork, problem_instance, currentTimeSlot):
    '''
    description: computes the number of devices that can be moved from network fromNetwork to network toNetwork
    args:        network (ID) from which to move devices, network(ID) to which to move devices
    return:      number of devices that can be moved between the networks, an indication whether the min gain currently observed by a device to be moved is zero
                 (indicated by -1) or not (indicated by 1)
    '''
    # compute the number of devices that selected network fromNetwork but the latter is not available to them
    numDevice = 0
    minCurrentGain = -1
    # print("devicePerNetwork[fromNetwork - 1]:", devicePerNetwork[fromNetwork - 1])
    for deviceID in devicePerNetwork[fromNetwork - 1]:
        if (not problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, fromNetwork, deviceID)) and problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, toNetwork, deviceID):
            numDevice += 1
            if numDevice == maxNumDeviceToMove: return numDevice, minCurrentGain
    for deviceID in devicePerNetwork[fromNetwork - 1]:
        if problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, fromNetwork, deviceID) and problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, toNetwork, deviceID):
            numDevice += 1
            if minCurrentGain < 0: minCurrentGain = 1
            if numDevice == maxNumDeviceToMove: return numDevice, minCurrentGain
    return numDevice, minCurrentGain
    # end getNumDeviceToMove

''' ___________________________________________________________________ get the index of object in list __________________________________________________________________ '''
def getListIndex(networkList, searchID):
    '''
    description: returns the index in a list (e.g. networkList or self.weight) at which details of the network with ID searchID is stored
    args:        self, ID of the network whose details is being sought
    returns:     index of array at which details of the network is stored
    assumption:  the list contains a network object with the given network ID searchID
    '''
    index = 0
    while index < len(networkList) and networkList[index].networkID != searchID:
        index += 1
    return index
    # end getListIndex

''' _____________________________________________________________________ to save details to csv file ____________________________________________________________________ '''
class CsvData(object):
    def __init__(self, filepath, headers):
        self.filepath = filepath
        self.headers = headers
        self.rows = []

    def addRow(self, row):
        self.rows.append(row)

    def saveToFile(self):
        saveToCsv(self.filepath, self.headers, self.rows)
# end CsvData class

def saveToCsv(outputCSVfile, headers, rows):
    myfile = open(outputCSVfile, "w+", newline='')
    out = csv.writer(myfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    if headers !=[]: out.writerow(headers)
    for row in rows: out.writerow(row)
    myfile.close()

def createBlankCsv(outputCSVfile, headers):
    myfile = open(outputCSVfile, "w+", newline='')
    out = csv.writer(myfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    out.writerow(headers)
    myfile.close()

def appendRowToCsv(outputCSVfile, row):
    myfile = open(outputCSVfile, "a", newline='')
    out = csv.writer(myfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    out.writerow(row)
    myfile.close()

def deviceCsvName(path, deviceID):
    return '%s/device%d.csv' % (path, deviceID)

def networkCsvName(path):
    return "%s/network.csv" % path

def saveToTxt(outputTxtFile, data):
    myfile =  open(outputTxtFile, "w")
    myfile.write(data)
    myfile.close()

def generate_random_seed():
    import random
    return random.randrange(2147483647)
''' _____________________________________________________________________________ end of file ____________________________________________________________________________ '''