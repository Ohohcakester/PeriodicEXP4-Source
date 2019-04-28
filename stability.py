'''
stability:
'''
import global_setting
import problem_instance_v2
import algo_periodicexp4.algo_periodicexp4 as algo_periodicexp4

stableProbability = 0.75
minNumTimeSlotForStability = 10      # the device must choose a particular network for at least the last
                                    # 'minNumTimeSlotForStability' time slots to be considered stable at that network
minNumRepetitionForStability = 2    # minimum number or repetitions the algorithm must be stable at a particular state

def extractStabilitySingleDevice(deviceData, numPeriod, numNetwork, algorithmName):
    '''
    description: extract details regarding stability of one device; get the network a particular device is stable at
    args:        per time slot details for the particular device, number of periods in the period set considered, number of networks
    return:      ID of the network the device is stable at; -1 if it doesn't stabilize at a particular network
    '''
    global stableProbability, minNumTimeSlotForStability

    preferredNetwork = -1
    # print(deviceData)
    for rowIndex in range(1, len(deviceData) + 1): #[:len(deviceData) - 1]:
        # networkSelected = int(row[2 + numPeriod])
        row = deviceData[rowIndex - 1]
        timeSlot = row[1]
        if algorithmName == "EXP3" or algorithmName == "BandwidthRatio": probabilityDistribution = row[2 + numNetwork: 2 + 2 * numNetwork]
        else: probabilityDistribution = row[2 + numPeriod + numNetwork: 2 + numPeriod + 2 * numNetwork]
        probabilityDistribution = [float(x) for x in probabilityDistribution]
        # print("prob start index:", 4 + numPeriod + numNetwork, ", end index:", 4 + numPeriod + 2 * numNetwork)
        # print("timeSlot:", timeSlot, "probabilityDistribution:", probabilityDistribution); #input()
        maxProbability = max(probabilityDistribution)
        currentPreferredNetwork = probabilityDistribution.index(maxProbability) + 1 if maxProbability >= stableProbability else -1
        if rowIndex > (len(deviceData) - minNumTimeSlotForStability + 1) and preferredNetwork != currentPreferredNetwork: preferredNetwork = -1; break
        else: preferredNetwork = currentPreferredNetwork
        # print("timeSlot:", timeSlot, ", probabilityDistribution:", probabilityDistribution)

    ### must consider phases...
    return preferredNetwork
    # end extractStabilitySingleDevice

def isStable(startTimeSlot, endTimeSlot, numNetwork, deviceDataList, numPeriod, problemInstance, repetitionIndex, algorithmName):
    '''
    description: considers one repetition and determines (1) if the algorithm is stable during the repetition, (2) the
                 stable state (if it stabilizes); assuming that the duration of time between changes in data rates is
                 called a phase - considers each phases which will have a different stable state
    args:        start and end time of the current repetition, number of networks, per time slot detains for each device,
                 number of periods in the period set considered
    return:      stable state or [-1]*numNetwork if it was not stable, network favored by each device at stable state
    '''
    global stableProbability

    stableStateListForCurrentRepetition = []
    preferredNetworkPerDeviceCurrentRepetition = []

    timeOfChangeList = problem_instance_v2.getTimesOfChange(problemInstance, repetitionIndex) + [endTimeSlot + 1]
    timeOfChangeList = sorted(timeOfChangeList)
    print("timeOfChangeList:",timeOfChangeList)

    for phaseIndex in range(1, len(timeOfChangeList)): # for each phase
        preferredNetworkPerDevice = []
        for deviceID in range(1, len(deviceDataList) + 1):
            # favoredNetwork = extractStabilitySingleDevice(deviceDataList[deviceID - 1][startTimeSlot-1:endTimeSlot], numPeriod, numNetwork)
            favoredNetwork = extractStabilitySingleDevice(deviceDataList[deviceID - 1][timeOfChangeList[phaseIndex - 1] -1:timeOfChangeList[phaseIndex] - 1], numPeriod, numNetwork, algorithmName)
            preferredNetworkPerDevice.append(favoredNetwork)
        # print("preferredNetworkPerDevice:", preferredNetworkPerDevice)
        if -1 in preferredNetworkPerDevice: stableStateListForCurrentRepetition.append([-1] * numNetwork)
        else: stableStateListForCurrentRepetition.append([preferredNetworkPerDevice.count(x) for x in range(1, numNetwork + 1)]) # else compute number of devices per network at the stable state
        preferredNetworkPerDeviceCurrentRepetition.append(preferredNetworkPerDevice)

    return stableStateListForCurrentRepetition, preferredNetworkPerDeviceCurrentRepetition
    # end isStable

def computeStability(problem_instance, deviceDataList, numTimeSlot, numRepeat, numPeriod, algorithmName):
    '''
    description:
    args:        number of values in the period list
    return:      None
    '''
    global minNumRepetitionForStability
    networkDataRate = problem_instance_v2.getNetworkDataRate(problem_instance, 1); numNetwork = len(networkDataRate)
    repetitionInWhichStabilized = -1  # -1 means the algorithm did not stabilized
    stableState = []
    preferredNetworkPerDevicePerRepetition = []

    for repetition in range(1, numRepeat + 1):
        repetitionDuration = numTimeSlot/numRepeat
        startTimeSlot = int((repetition - 1) * repetitionDuration + 1); endTimeSlot = int(startTimeSlot + repetitionDuration - 1)
        # print(startTimeSlot, endTimeSlot)
        stableStateListForCurrentRepetition, preferedNetworkPerDeviceCurrentRepetition = isStable(startTimeSlot, endTimeSlot, numNetwork, deviceDataList, numPeriod, problem_instance, repetition, algorithmName)
        preferredNetworkPerDevicePerRepetition.append(preferedNetworkPerDeviceCurrentRepetition)
        print(stableStateListForCurrentRepetition)
        if [-1]*numNetwork not in stableStateListForCurrentRepetition and stableState == [] and repetition <= (numRepeat - minNumRepetitionForStability + 1):
            stableState = stableStateListForCurrentRepetition
            repetitionInWhichStabilized = repetition
        elif stableState != stableStateListForCurrentRepetition:
            if [-1]*numNetwork not in stableStateListForCurrentRepetition and repetition <= (numRepeat - minNumRepetitionForStability + 1):
                stableState = stableStateListForCurrentRepetition
                repetitionInWhichStabilized = repetition
            else: stableState = []; repetitionInWhichStabilized = -1
    return stableState, repetitionInWhichStabilized, preferredNetworkPerDevicePerRepetition
    # end computeStability

def main():
    numTimeSlot = 8; numRepeat = 2; numDevice = 3; periodList = [3]
    problemInstance = 'change_in_data_rates_simple'

    global_setting.constants.update({'num_mobile_device': numDevice})
    global_setting.constants.update({'num_time_slot': numTimeSlot})
    global_setting.constants.update({'num_repeats': numRepeat})
    problem_instance_v2.initialize()
    # print(problem_instance_v2.PROBLEM_INSTANCES)

    networkDataRate = problem_instance_v2.getNetworkDataRate(problemInstance, 1); maxGain = max(networkDataRate)
    numNetwork = len(networkDataRate); networkList = list(range(1, numNetwork + 1))
    partitions = algo_periodicexp4.make_repeating_partition_cycles(numTimeSlot, numRepeat, periodList)

    mobileDeviceDataList = []
    headers = ["Run no.", "Time slot"] + ["w_partitionF1"] + ["Current network", "gain"] + \
              ["w_arm" + str(i) for i in range(1, numNetwork+1)] + \
              ["probability" + str(i) for i in range(1, numNetwork + 1)] + ["gamma"] + \
              ["Bandwidth in network %d (MB)" % j for j in range(1, numNetwork + 1)] + \
              ["maxGain"]
    for mobileDevice in range(numDevice):
        deviceData=[]
        deviceData.append([1, 1, 0, 1, 0.5, 1, 1, 1, 1 / 3, 1 / 3, 1 / 3, 0.3, 0, 0, 0, maxGain])
        deviceData.append([1, 2, 0, 1, 0.5, 1, 1, 1, 1/10, 2 / 10, 8 / 10, 0.3, 0, 0, 0, maxGain])
        deviceData.append([1, 3, 0, 1, 0.5, 1, 1, 1, 1/10, 2 / 10, 8 / 10, 0.3, 0, 0, 0, maxGain])
        deviceData.append([1, 4, 0, 1, 0.5, 1, 1, 1, 1/10, 7.5 / 10, 1.5 / 10, 0.3, 0, 0, 0, maxGain])
        # deviceData.append([1, 1, 0, 1, 0.5, 1, 1, 1, 1 / 10, 2 / 10, 8 / 10, 0.3, 0, 0, 0, maxGain])
        # deviceData.append([1, 2, 0, 1, 0.5, 1, 1, 1, 1 / 10, 8 / 10, 1 / 10, 0.3, 0, 0, 0, maxGain])
        # deviceData.append([1, 3, 0, 1, 0.5, 1, 1, 1, 1 / 10, 8 / 10, 1 / 10, 0.3, 0, 0, 0, maxGain])
        # deviceData.append([1, 4, 0, 1, 0.5, 1, 1, 1, 1 / 10, 8 / 10, 1 / 10, 0.3, 0, 0, 0, maxGain])
        deviceData.append([1, 5, 0, 1, 0.5, 1, 1, 1, 1/10, 2 / 10, 8 / 10, 0.3, 0, 0, 0, maxGain])
        deviceData.append([1, 6, 0, 1, 0.5, 1, 1, 1, 1/10, 8 / 10, 1 / 10, 0.3, 0, 0, 0, maxGain])
        deviceData.append([1, 7, 0, 1, 0.5, 1, 1, 1, 1/10, 8 / 10, 1 / 10, 0.3, 0, 0, 0, maxGain])
        deviceData.append([1, 8, 0, 1, 0.5, 1, 1, 1, 1/10, 7.5/ 10, 1.5 / 10, 0.3, 0, 0, 0, maxGain])
        mobileDeviceDataList.append(deviceData)
        # print(deviceData)
    # print(mobileDeviceDataList)
    stableState, repetitionInWhichStabilized, preferredNetworkPerDevicePerRepetition = computeStability(problemInstance, mobileDeviceDataList, numTimeSlot, numRepeat, len(periodList))
    print("##### result: ", stableState, repetitionInWhichStabilized, preferredNetworkPerDevicePerRepetition)
if __name__ == "__main__": main()