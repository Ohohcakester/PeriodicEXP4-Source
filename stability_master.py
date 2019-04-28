'''
@description: extracts details about stability and number of network switches
'''
import csv
import argparse
from numpy import median
from utility_method import saveToTxt, saveToCSV

parser = argparse.ArgumentParser(description='Exctracts details regarding stability of the algorithm.')
parser.add_argument('-d', dest="root_dir", required=True, help='root directory where data of all runs are stored')
parser.add_argument('-r', dest="num_run", required=True, help='number of simulation runs')
parser.add_argument('-t', dest="num_time_slot", required=True, help='number of time slots in each simulation run')
parser.add_argument('-n', dest="num_device", required=True, help='number of active devices in the service area')
parser.add_argument('-k', dest="num_network", required=True, help='number of wireless networks in the service area')
parser.add_argument('-p', dest="stable_probability", required=True, help='probability at which the algorithm is considered stable')
parser.add_argument('-c', dest="consecutive_stable_slot", required=True, help='minimum number of consecutive slots the algorithm must stay in the same state till the end of the run to be considered stable')
parser.add_argument('-ne', dest='nash_equilibrium_state_list', required=True, help='list of Nash equilibrium states for the setting')

args = parser.parse_args()
rootDir = args.root_dir
numRun = int(args.num_run)
numTimeSlot = int(args.num_time_slot)
numDevice = int(args.num_device)
numNetwork = int(args.num_network)
stableProbability = float(args.stable_probability)
consecutiveStableSlot = int(args.consecutive_stable_slot)
NEstate = args.nash_equilibrium_state_list.split(";"); NEstateList = []
for state in NEstate: state = state.split("_"); state = [int(x) for x in state]; NEstateList.append(state)

''' _________________________________________ extract stability status, number of network switch and cumulative gain of a device _________________________________________ '''
def extractStabilityStatus(deviceCSVfile, numNetwork, stableProbability, numTimeSlot, consecutiveStableSlot):
    '''
    description: extract details regarding stability of one device
    args:        CSV file containing run details of a specific device, number of networks, minimum probability of a network for the algorithm to be considered stable,
                 number of time slots, minimum number of consecutive time slots the device must be favoring a particular network at the end of the run for it to be considered
                 stable at that network
    return:      time slot at which the device made its decision to stick to a particular network, the network it selects with sufficiently high probability till the end of
                 execution, the number of times the device switched network, cumulative gain of each device
    '''
    stabilizationTimeSlot = -1
    preferredNetworkID = -1
    prevNetwork = -1; numNetworkSwitch = 0; cumulativeGain = 0
    # consecutiveStableSlot = 0  # must stay in that state for at least that number of slots at the end to be sure the algorithm stabilized...

    with open(deviceCSVfile, newline='') as deviceCSVfile:
        fileReader = csv.reader(deviceCSVfile)
        count = 0
        for row in fileReader:
            if count != 0:
                # stability
                probability = row[2 + numNetwork:2 + 2*numNetwork]; probability = [float(x) for x in probability]
                maxProbability = max(probability)
                currentPrefferedNetworkID = probability.index(maxProbability) + 1
                if maxProbability < stableProbability and stabilizationTimeSlot != -1:
                    stabilizationTimeSlot = -1; preferredNetworkID = -1
                elif maxProbability >= stableProbability and (stabilizationTimeSlot == -1 or preferredNetworkID != currentPrefferedNetworkID):
                    stabilizationTimeSlot = int(row[1]); preferredNetworkID = currentPrefferedNetworkID

                # network switch
                currentNetwork = int(row[2 + 2 * numNetwork])
                if prevNetwork != -1 and prevNetwork != currentNetwork: numNetworkSwitch += 1
                prevNetwork = currentNetwork

                # cumulative gain
                gain = float(row[4 + 2 * numNetwork])
                cumulativeGain += gain
            count += 1
    deviceCSVfile.close()

    # if we don't see it stay in a state for at least 'consecutiveStableSlot' time slots, we cannot be sure if the algorithm has stabilized
    if stabilizationTimeSlot > numTimeSlot - consecutiveStableSlot: stabilizationTimeSlot = -1; preferredNetworkID = -1

    return stabilizationTimeSlot, preferredNetworkID, numNetworkSwitch, cumulativeGain
    # end extractStabilityStatus

''' __________________ determines number of devices that must switch network for the algorithm to transition from its stable state to Nash equilibrium  __________________ '''
def getNumDeviceSwitchNetwork(stableState, NEstateList):
    '''
    description: computes and returns the number of devices that should switch network from the algorithm to transit from its stable state to a Nash equilibrium state
                 (if there are multiple Nash equilibrium states, it considers the one requiring the minimum number of switches)
    args:        the stable state of the algorithm, the list Nash equilibrium states for the setting considered
    return:      number of devices who need to switch network
    '''
    if stableState in NEstateList: return 0
    numDeviceSWitchNetworkPerNEState = []   # considers the number of moves to reach each NE state; will then take the minimum move
    for NEstate in NEstateList:
        numDeviceSwitch = [x - y for x, y in zip(stableState, NEstate)]
        count = sum([x for x in numDeviceSwitch if x > 0])
        numDeviceSWitchNetworkPerNEState.append(count)
    return min(numDeviceSWitchNetworkPerNEState)
    # end getNumDeviceSwitchNetwork

''' ______________________________________________________________________ check if a run is stable ______________________________________________________________________ '''
def isStable(rootDir, numNetwork, stableProbability, numTimeSlot, consecutiveStableSlot, NEstateList):
    '''
    description: determines (1) whether the run stabilized, (2) if it stabilizes, to which state, (3) time slot at which the algorithm stabilized, (4) the number of devices
                 that should switch network for the algorithm to get from its stable state to Nash equilibrium (this value is zero if the stable state is Nash equilibrium)
                 and (5) number of network switches made by each device
    args:        root directory where the files for each device are stored for a particular run, number of networks, minimum probability of a network for the algorithm to be
                 considered stable, number of time slots, minimum number of consecutive time slots the device must be favoring a particular network at the end of the run for
                 it to be considered stable at that network, list of Nash equilibrium states
    return:      the time slot at which the algorithm stabilized, its stable state and a list of the number of network switches of each device
    '''
    stabilizationTimeSlotPerDevice = []; preferredNetworkPerDevice = []; stableState = [-1] * numNetwork; numNetworkSwitchPerDevice = []; cumulativeGainPerDevice = []

    for deviceID in range(1, numDevice + 1):
        stabilizationTimeSlot, preferredNetwork, numNetworkSwitch, cumulativeGain = extractStabilityStatus(rootDir + "device" + str(deviceID) + ".csv", numNetwork, stableProbability, numTimeSlot, consecutiveStableSlot)
        # print(deviceID, stabilizationTimeSlot, preferredNetwork)
        stabilizationTimeSlotPerDevice.append(stabilizationTimeSlot)
        preferredNetworkPerDevice.append(preferredNetwork)
        numNetworkSwitchPerDevice.append(numNetworkSwitch)
        cumulativeGainPerDevice.append(cumulativeGain)

    if -1 not in stabilizationTimeSlotPerDevice:
        stabilizationTimeSlot = max(stabilizationTimeSlotPerDevice)
        for networkIndex in range(numNetwork):
            stableState[networkIndex] = preferredNetworkPerDevice.count(networkIndex + 1)
    else: stabilizationTimeSlot = -1

    numDeviceSwitchNetworkForNE = getNumDeviceSwitchNetwork(stableState, NEstateList)

    # print("stabilizationTimeSlotPerDevice: ", stabilizationTimeSlotPerDevice, ", preferredNetworkPerDevice:", preferredNetworkPerDevice)
    # print("numNetworkSwitchPerDevice:", numNetworkSwitchPerDevice)
    return stabilizationTimeSlot, stableState, numNetworkSwitchPerDevice, cumulativeGainPerDevice, numDeviceSwitchNetworkForNE
    # end isStable

''' ____________________________________________________________________________ main program ____________________________________________________________________________ '''
def main():
    global rootDir, numRun, numTimeSlot, numDevice, numNetwork, stableProbability, consecutiveStableSlot, NEstateList

    stabilizationTimeSlotPerRun = []
    stableStatePerRun = []
    numNetworkSwitchPerDevicePerRun = []
    cumulativeGainPerDevicePerRun = []
    numDeviceSwitchNetworkForNEPerRun = []

    for runIndex in range(1, numRun + 1):
        stabilizationTimeSlot, stableState, numNetworkSwitchPerDevice, cumulativeGainPerDevice, numDeviceSwitchNetworkForNE = \
            isStable(rootDir + "run" + str(runIndex) + "/", numNetwork, stableProbability, numTimeSlot, consecutiveStableSlot, NEstateList)
        stabilizationTimeSlotPerRun.append(stabilizationTimeSlot); stableStatePerRun.append(stableState)
        numNetworkSwitchPerDevicePerRun += numNetworkSwitchPerDevice
        numDeviceSwitchNetworkForNEPerRun.append(numDeviceSwitchNetworkForNE)
        cumulativeGainPerDevicePerRun += cumulativeGainPerDevice

    # process number of times each stable state reached
    numStableRun = numRun - stabilizationTimeSlotPerRun.count(-1)
    print("numStableRun:", numStableRun)

    # build list of stable states, their count and runs that stabilized to that state
    stableState = {}
    for i in range(numRun):
        stateStr = '_'.join(str(x) for x in stableStatePerRun[i])
        if stateStr in stableState:
            stableState[stateStr].update({'count':stableState[stateStr]['count']+1})
            stableState[stateStr].update({'run':stableState[stateStr]['run']+[i + 1]})
        else:
            stableState.update({stateStr:{}})
            stableState[stateStr].update({'count':1})
            stableState[stateStr].update({'run':[i+1]})
        stableState[stateStr].update({'numDeviceToSwitchForNE':numDeviceSwitchNetworkForNEPerRun[i]})
    print("stable state:", stableState)

    # save to text file
    outputTxtFile = rootDir + "stability.txt"
    data = "Stable run(s): " + str(numStableRun) + " (" + str(numStableRun*100/numRun) + "%)\n\n" + "Stable states:"
    for state in stableState:
        stateList = state.split('_'); stateList = [int(x) for x in stateList]
        data += "\n\t" + str(stateList) + ": " + str(stableState[state])
    stabilizationTimeSlotPerRun = list(filter(lambda x: x != -1, stabilizationTimeSlotPerRun))
    # print("stabilizationTimeSlotPerRun:", stabilizationTimeSlotPerRun)
    avgTime = medianTime = minTime = maxTime = -1
    if len(stabilizationTimeSlotPerRun) > 0:
        avgTime = sum(stabilizationTimeSlotPerRun) / len(stabilizationTimeSlotPerRun)
        medianTime = median(stabilizationTimeSlotPerRun); minTime = min(stabilizationTimeSlotPerRun); maxTime = max(stabilizationTimeSlotPerRun)
        data += "\n\nTime to stabilize (considering runs that stabilized):\n\tAverage: " + str(avgTime) + "\n\tMedian: " + str(medianTime) + "\n\tMinimum: " \
                + str(minTime) + "\n\tMaximum: " + str(maxTime)
    data += "\n\nTime to stabilize (considering runs that stabilized):\n\t" + str(stabilizationTimeSlotPerRun)
    # number of devices to switch network to transit from the state state to Nash equilibrium
    data += "\n\nNumber of devices to switch network to transit from the state state to Nash equilibrium:\n\t" + str(numDeviceSwitchNetworkForNEPerRun)
    saveToTxt(outputTxtFile, data)

    # save to csv file
    outputCSVfile = rootDir + "stability.csv"
    dataCSV = [["stable run(%)", "stable state", "", "#device to switch network be at NE", "time to stabilize (#time slot)", "", "", ""]]
    dataCSV.append(["", "state", "count", "", "median", "average", "min", "max"])
    count = 0
    for state in stableState:
        stateList = state.split('_'); stateList = [int(x) for x in stateList]
        if count == 0: dataCSV.append([numStableRun*100/numRun, stateList, stableState[state]['count'], stableState[state]['numDeviceToSwitchForNE'] , medianTime, avgTime, minTime, maxTime])
        else:
            dataCSV.append(["", stateList, stableState[state]['count'], stableState[state]['numDeviceToSwitchForNE'], "", "", "", ""])
        count += 1

    saveToCSV(outputCSVfile, [], dataCSV)

    # save the time to stabilize in a csv file for box plot
    for i in range(len(stabilizationTimeSlotPerRun)):
        stabilizationTimeSlotPerRun[i] = [0, stabilizationTimeSlotPerRun[i]]
    print(stabilizationTimeSlotPerRun)
    saveToCSV(rootDir + "stabilizationTimeSlotPerRun.csv", [], stabilizationTimeSlotPerRun)

    # number of network switch
    networkSwitchData = "Number of network switch per device:\n\tAverage: " + str(sum(numNetworkSwitchPerDevicePerRun)/len(numNetworkSwitchPerDevicePerRun)) \
                        + "\n\tMedian: " + str(median(numNetworkSwitchPerDevicePerRun)) + "\n\tMinimum: " + str(min(numNetworkSwitchPerDevicePerRun)) \
                        + "\n\tMaximum: " + str(max(numNetworkSwitchPerDevicePerRun)) + "\n\nNumber of network switch per device:\n\t" + str(numNetworkSwitchPerDevicePerRun)
    saveToTxt(rootDir + "networkSwitch.txt", networkSwitchData)
    # save number of network switch in a csv file for box plot
    for i in range(len(numNetworkSwitchPerDevicePerRun)):
        numNetworkSwitchPerDevicePerRun[i] = [0, numNetworkSwitchPerDevicePerRun[i]]
    saveToCSV(rootDir + "numberOfNetworkSwitch.csv", [], numNetworkSwitchPerDevicePerRun)

    # cumulative gain
    networkSwitchData = "Cumulative gain per device:\n\tAverage: " + str(sum(cumulativeGainPerDevicePerRun) / len(cumulativeGainPerDevicePerRun)) \
                        + "\n\tMedian: " + str(median(cumulativeGainPerDevicePerRun)) + "\n\tMinimum: " + str(min(cumulativeGainPerDevicePerRun)) \
                        + "\n\tMaximum: " + str(max(cumulativeGainPerDevicePerRun)) + "\n\nCumulative gain per device:\n\t" + str(cumulativeGainPerDevicePerRun)
    saveToTxt(rootDir + "cumulativeGain.txt", networkSwitchData)
    # save number of network switch in a csv file for box plot
    for i in range(len(cumulativeGainPerDevicePerRun)):
        cumulativeGainPerDevicePerRun[i] = [0, cumulativeGainPerDevicePerRun[i]]
    saveToCSV(rootDir + "cumulativeGain.csv", [], cumulativeGainPerDevicePerRun)

if __name__ == "__main__": main()
''' _____________________________________________________________________________ end of file ____________________________________________________________________________ '''