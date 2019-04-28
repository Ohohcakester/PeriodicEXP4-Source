'''
@description:   Defines a class that models a mobile device
'''

''' ______________________________________________________________________ import external libraries ______________________________________________________________________ '''
import simpy
from network import Network
from utility_method import getListIndex, CsvData, deviceCsvName, networkCsvName
import global_setting
from termcolor import colored
from logging_configure import logger
import problem_instance_v2
from copy import deepcopy
import pickle
''' ______________________________________________________________________________ constants ______________________________________________________________________________ '''
NUM_MOBILE_DEVICE = global_setting.constants['num_mobile_device']
NUM_TIME_SLOT = global_setting.constants['num_time_slot']
RUN_NUM = global_setting.constants['run_num']
ALGORITHM = global_setting.constants['algorithm_name']
OUTPUT_DIR = global_setting.constants['output_dir']
networkList = global_setting.constants['network_list']

class PartitionCumulativeGains(object):
    '''
    description: used to compute the gain of each expert (possible set of choices for every partition options?);
                 this is eventually used to compute the gain of the "best" expert, and regret of the algorithm
    '''
    def __init__(self, partitionTuples, numNetworks):
        self.cumulativeGain = []
        for function, nLabels in partitionTuples:
            self.cumulativeGain.append([[0]*numNetworks for i in range(nLabels)])
        self.functions = tuple(tup[0] for tup in partitionTuples)

    def giveGain(self, t, potentialGains):
        for f, function in enumerate(self.functions):
            l = function(t-1)
            for i, value in enumerate(potentialGains):
                self.cumulativeGain[f][l][i] += value

    def maxCumulativeGain(self):
        return max(sum(max(gains) for gains in cumulativeLabelGains)
            for cumulativeLabelGains in self.cumulativeGain)

''' ____________________________________________________________________ MobileDevice class definition ____________________________________________________________________ '''
class MobileDevice(object):
    numMobileDevice = 0 # keeps track of number of mobile devices to automatically assign an ID to device upon creation

    def __init__(self, networks, maxGain, trackDetailedStats=False, partitions=None):
        MobileDevice.numMobileDevice = MobileDevice.numMobileDevice + 1
        self.deviceID = MobileDevice.numMobileDevice            # ID of device
        self.availableNetwork = [networkList[i].networkID for i in range(len(networkList))]  # networkIDs of set of available networks
        self.unavailableNetwork = []                            # networks currently not available
        self.currentNetwork = -1                                # network to which the device is currently associated
        self.gain = 0                                           # bit rate observed
        self.maxGain = maxGain                                  # initialize to max bit rate a client can expect to receive
        self.cumulativeGain = 0                                 # keeps track of the cumulative gain observed (unscaled)
        self.trackDetailedStats = trackDetailedStats

        if partitions == None: partitions = [(lambda t : 0, 1)] # constant function
        self.partitionCumulativeGains = PartitionCumulativeGains(partitions, len(networkList))

        self.csvData = None
        self.networkCsvData = None
        # end __init__


    def runAlgorithm(self, env, algorithm, results, gamma_function, problemInstance, optimization):
        '''
        description:
        args:        self, env, an object of the algorithm being used, a list to which each device will append its
                     cumulative gain and that of its best expert, the name of the problem instance being considered,
                     whether to leverage any optimization for the algorithm
        return:
        '''
        # problemInstance = 'change_in_data_rates'
        global ALGORITHM

        f = open('networkDataRate.pkl', 'rb')  # 'r' for reading; can be omitted
        dataRate = pickle.load(f)  # load file content as mydict
        f.close()

        if self.trackDetailedStats:
            if self.deviceID == 1: MobileDevice.makeNetworkCsv(self)
            MobileDevice.makeDeviceCsv(self, algorithm.get_log_headers())

        for t in range(1,NUM_TIME_SLOT+1):
            # makes changes in network data rates; single device updates the data rate
            if self.deviceID == 1:
                if problemInstance == "continuous":
                    dataRateIndex = (t-1)%len(dataRate[0]); currentDataRate = [dataRate[x][dataRateIndex] for x in range(len(dataRate))]
                    # print("index:", dataRateIndex)#, ", data rates:", currentDataRate)
                else: currentDataRate = problem_instance_v2.getNetworkDataRate(problemInstance, t) # print(t, currentDataRate)
                for i in range(len(networkList)): networkList[i].setDataRate(currentDataRate[i])


            # check if the device is still in the service area
            # if problem_instance_v2.isActive(problemInstance, t, self.deviceID):
            # makes changes to the set of available networks if required
            self.unavailableNetwork = problem_instance_v2.getUnavailableNetwork(problemInstance, t, self.deviceID) if optimization == True and problemInstance != "continuous" else []
            # print("t", t, ", device", self.deviceID, ", self.unavailableNetwork:", self.unavailableNetwork)
            if ALGORITHM == "BandwidthRatio": #self.unavailableNetwork = problem_instance_v2.getNetworkDataRate(problemInstance, t)
                if problemInstance == "continuous": dataRateIndex = (t-1)%len(dataRate[0]); dataRatePerNetwork = [dataRate[x][dataRateIndex] for x in range(len(dataRate))]
                else:
                    dataRatePerNetwork = problem_instance_v2.getNetworkDataRate(problemInstance, t)  # print(t, currentDataRate)
                    # self.unavailableNetwork is the data rate of each network instead; it's zero for unavailable networks
                    dataRatePerNetwork_Cpy = deepcopy(dataRatePerNetwork)
                    for i in range(len(dataRatePerNetwork)):
                        if (i + 1) in self.unavailableNetwork: dataRatePerNetwork_Cpy[i] = 0
                    # print("t", t, ", device", self.deviceID, ", self.unavailableNetwork:", self.unavailableNetwork, "datarate", dataRatePerNetwork,", dataRatePerNetwork_Cpy:", dataRatePerNetwork_Cpy)
                    self.unavailableNetwork = deepcopy(dataRatePerNetwork_Cpy)

            yield env.timeout(1)

            prevNetworkSelected = self.currentNetwork
            self.currentNetwork = self.availableNetwork[algorithm.get_next_arm(self.unavailableNetwork)] # select a wireless network ####################

            # associate with the network
            if prevNetworkSelected != self.currentNetwork:
                if prevNetworkSelected != -1: MobileDevice.leaveNetwork(self, prevNetworkSelected)
                MobileDevice.joinNetwork(self, self.currentNetwork, t)

            yield env.timeout(1)

            # observe a gain
            scaledGain = MobileDevice.observeGain(self, problemInstance, t)
            # scaledGain = min(self.gain/self.maxGain, 1)
            # I would rather set the value of maxGain to the new max if gain > maxGain?
            # if self.gain > self.maxGain: self.maxGain = self.gain - maybe in observeGain

            gamma = gamma_function(t,NUM_TIME_SLOT)
            algorithm.give_reward(scaledGain, gamma)

            # Score computation for result logging: (compute potential gain of all possible choices)
            self.cumulativeGain += self.gain
            potentialGains = [0]*len(networkList)
            for netIndex, network in enumerate(networkList): # append achievable download if connected to each of the other networks; each expert's gain
                if (network.networkID == self.currentNetwork):
                    # possibleDownload = network.dataRate/network.getNumAssociatedDevice()
                    possibleDownload = network.getPerDeviceDownload(problemInstance, t, self.deviceID, 1)
                else:
                    # possibleDownload = network.dataRate / (network.getNumAssociatedDevice() + 1)
                    if problem_instance_v2.isNetworkAccessible(problemInstance, t, network.networkID, self.deviceID):
                        possibleDownload = network.dataRate/(network.getNumAssociatedDevice() + 1)
                    else: possibleDownload = 0
                potentialGains[netIndex] = possibleDownload
            self.partitionCumulativeGains.giveGain(t, potentialGains)

            # logging details of current time step to user, network and rateOfConvergence files
            if self.trackDetailedStats:
                algoData = algorithm.get_timestep_log()
                MobileDevice.saveDeviceDetail(self, t, potentialGains, algoData)  # save device details to csv file
                if self.deviceID == 1: MobileDevice.saveNetworkDetail(self, t)    # save network details to csv file
            # else:
            #     print("device", self.deviceID, " not in service area");
            #     if self.currentNetwork != -1: MobileDevice.leaveNetwork(self, self.currentNetwork); self.currentNetwork = -1
            #     yield env.timeout(2)
            if self.deviceID == 1 and t % 1000 == 0: print("done " + str(t) + " time slots")

        maxCumulativeGain = self.partitionCumulativeGains.maxCumulativeGain()
        results.append((self.deviceID, self.cumulativeGain, maxCumulativeGain))

    ''' ################################################################################################################################################################### '''
    def observeGain(self, problem_instance, currentTimeSlot):
        '''
        description: determines the bit rate observed by the device from the wireless network selected and scale the gain to the range [0, 1]
        args:        self
        returns:     amount of bandwidth observed by the device
        '''
        networkIndex = getListIndex(networkList, self.currentNetwork)  # get the index in lists where details of the specific network is saved
        self.gain = networkList[networkIndex].getPerDeviceBitRate(problem_instance, currentTimeSlot, self.deviceID)  # in Mbps
        if self.maxGain < self.gain: self.maxGain = self.gain
        return self.gain/self.maxGain
        # end observeGain

    ''' ################################################################################################################################################################### '''
    def joinNetwork(self, networkSelected, currentTimeSlot):
        '''
        description: adds a particular device to a specified network, by incrementing the number of devices in that network by 1
        arg:         self, ID of network to join
        returns:     None
        '''
        networkIndex = getListIndex(networkList, networkSelected)
        networkList[networkIndex].associateDevice(self.deviceID)
        # end joinNetwork

    ''' ################################################################################################################################################################### '''
    def leaveNetwork(self, prevNetworkSelected):
        '''
        description: removes a particular device from a specified network, by decrementing the number of devices in that network by 1
        arg:         self, ID of network to leave
        returns:   None
        '''
        networkIndex = getListIndex(networkList, prevNetworkSelected)
        networkList[networkIndex].disassociateDevice(self.deviceID)
        # end leaveNetwork

    ''' ################################################################################################################################################################### '''
    def makeDeviceCsv(self, algoSpecificHeaders):
        headers = ["Run no.", "Time slot"] +\
                  algoSpecificHeaders +\
                  ["Current network", "gain"] +\
                  ["Bandwidth in network %d (MB)" % j for j in range(1,len(self.availableNetwork)+1)] +\
                  ["maxGain"]

        self.csvData = CsvData(deviceCsvName(OUTPUT_DIR, self.deviceID), headers)
        #createBlankCsv(deviceCsvName(OUTPUT_DIR, self.deviceID), headers)

    ''' ################################################################################################################################################################### '''
    def makeNetworkCsv(self):
        headers = ["Run no.", "Time slot", "Device ID"] +\
                  ['#users%d' % i for i in range(1,len(self.availableNetwork)+1)] +\
                  ['dataRate%d' % i for i in range(1,len(self.availableNetwork)+1)] + \
                  ["Devices in network %d" % j for j in range(1, len(self.availableNetwork) + 1)]
        self.networkCsvData = CsvData(networkCsvName(OUTPUT_DIR), headers)
        #createBlankCsv(networkCsvName(OUTPUT_DIR), headers)

    ''' ################################################################################################################################################################### '''
    def saveDeviceDetail(self, t, potentialGains, algoData):
        # , sharedData = [], shareObservation=0, receiveObservation=0, shareProb=0, receiveProb=0, uniformProb=0):
        '''
        description: save details for each device in its own cvs file
        args:        self, iteration t, weight used in the previous iteration to compute the probability, learning rate, scaled gain and estimated for the current time slot,
                     data that has been shared and is still valid, whether one's observation has been shared or data has been received in this time slot, the probability with
                     which the device shares and receives data, the value of the variable that controls the uniform part of the probability distribution
        returns:     None
        '''
        data = [RUN_NUM, t] +\
               algoData +\
               [self.currentNetwork, self.gain] +\
               potentialGains +\
               [self.maxGain]
        self.csvData.addRow(data)
        #appendRowToCsv(deviceCsvName(OUTPUT_DIR, self.deviceID), data)
        # end saveDeviceDetail

    ''' ################################################################################################################################################################### '''
    def saveNetworkDetail(self, t):
        '''
        description: save details pertaining to each wireless network
        args:        self, iteration t
        returns:     None
        '''
        data = [RUN_NUM, t, self.deviceID] +\
               [network.getNumAssociatedDevice() for network in networkList] +\
               [network.getDataRate() for network in networkList] + \
               [deepcopy(network.getAssociatedDevice()) for network in networkList]
        self.networkCsvData.addRow(data)
        # print("network data:", data, ", self.networkCsvData:", self.networkCsvData.rows); input()
        #appendRowToCsv(networkCsvName(OUTPUT_DIR), data)
        # end saveNetworkDetail

    def writeCsv(self):
        if self.csvData != None: self.csvData.saveToFile()
        if self.networkCsvData != None: self.networkCsvData.saveToFile()


    def updateChangeInNetwork(self, availableNetworkList, algorithm):
        '''
        description: performs updates because of changes in set of networks available
        args:        self, current set ot networks available
        return:      None
        '''
        newNetworks = list(set(availableNetworkList) - set(self.availableNetwork))
        lostNetworks = list(set(self.availableNetwork) - set(availableNetworkList))

        # self.lastWeightPerNetwork = {}
        self.availableNetwork = availableNetworkList
        # end updateChangeInNetwork
# end MobileDevice class