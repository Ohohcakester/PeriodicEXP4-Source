import csv
from utility_method import saveToCsv
import computeDistanceToNE_mobility_v2
# import matplotlib.pyplot as plt
from utility_method import computeMovingAverage
from stability import computeStability

def analyze(problemInstance, numTimeSlot, networkdata, numDevice, cumulativeGainData, dir, numRepeat, deviceDataList, numPeriod, algorithmName):
    # get per device cumulative gain and save to csv file
    cumulativeGainPerDevice = [cumulativeGain[1] for cumulativeGain in cumulativeGainData]
    saveToCsv(dir + "cumulativeGainPerDevice.csv", [], [[0, cumulativeGain] for cumulativeGain in cumulativeGainPerDevice])

    # compute distance to Nash equilibrium and save to csv file
    distance = computeDistanceToNE_mobility_v2.computeDistanceToNashEquilibrium(problemInstance, numTimeSlot, networkdata, numDevice)
    saveToCsv(dir + "distanceToNashEquilibrium.csv", ["timeSlot", "distance"], [[i + 1, distance[i]] for i in range(len(distance))])

    if problemInstance != "continuous":
        print("will process stability...")
        # determine if the algorithm stabilized and save the result
        stableState, repetitionInWhichStabilized, preferredNetworkPerDevicePerRepetition = computeStability(problemInstance, deviceDataList, numTimeSlot, numRepeat, numPeriod, algorithmName)
        # print("stable state:", stableState, ", repetitionInWhichStabilized:", repetitionInWhichStabilized, ", preferredNetworkPerDevicePerRepetition:", preferredNetworkPerDevicePerRepetition)
        stabilityRows = [["stable state", stableState], ["repetitionInWhichStabilized", repetitionInWhichStabilized]]
        for repetition in range(1, len(preferredNetworkPerDevicePerRepetition) + 1):
            for phase in range(1, len(preferredNetworkPerDevicePerRepetition[0]) + 1):
                stabilityRows.append(["preferredNetworkPerDeviceRepetition"+str(repetition)+"Phase" + str(phase), preferredNetworkPerDevicePerRepetition[repetition-1][phase-1]])
        saveToCsv(dir + "stability.csv", [], stabilityRows)
    else: print("will not process stability")
    # plot the distance to Nash equilibrium for repetitions 1 and 60
    # plt.xlabel('Time slot')
    # plt.ylabel('Max higher gain a device can observe (Mbits)')
    # plt.title('Distance to Nash equilibrium')
    # plt.grid(True)
    # rollingAverageWindowSize = 10; numTimeSlotPerRepeat = numTimeSlot//numRepeat
    # # print(rollingAverageWindowSize // 2, numTimeSlotPerRepeat - (rollingAverageWindowSize // 2) + 1)
    # timeSlotList = list(range(rollingAverageWindowSize // 2, numTimeSlotPerRepeat - (rollingAverageWindowSize // 2) + 1))
    # distanceRepetition1 = distance[:numTimeSlotPerRepeat]; distanceRepetition60 = distance[numTimeSlot-numTimeSlotPerRepeat:]
    # # print(len(distanceRepetition1), len(distanceRepetition60), timeSlotList)
    # distanceRepetition1 = computeMovingAverage(distanceRepetition1, rollingAverageWindowSize)
    # distanceRepetition60 = computeMovingAverage(distanceRepetition60, rollingAverageWindowSize)
    # # print(len(distanceRepetition1), len(distanceRepetition60), timeSlotList)
    # plt.plot(timeSlotList, distanceRepetition1)
    # plt.plot(timeSlotList, distanceRepetition60)
    # plt.gca().legend(("Repetition 1", "Repetition " + str(numRepeat)))
    # plt.savefig(dir + "distanceToNashEquilibrium.png")
    # plt.show()

# import numpy as np
#
# t = np.arange(0.0, 2.0, 0.01)
# s = 1 + np.sin(2*np.pi*t)
# plt.plot(t, s)
#
# plt.xlabel('time (s)')
# plt.ylabel('voltage (mV)')
# plt.title('About as simple as it gets, folks')
# plt.grid(True)
# plt.savefig("test.png")
# plt.show()