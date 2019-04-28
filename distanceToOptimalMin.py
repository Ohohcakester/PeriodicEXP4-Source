# 1: 16/7
# 2 and 6: 7/2
# 3 and 5: 4
# 4: 36/7
# (min users are getting) divide by (optimal min)
import csv

numDevice = 20
numNetwork = 9
numTimeSlot = 48 #2880#86400
numRepeat = 2#60
numRun = 2#20
problem_instance = "mobility_setup3"
algorithmName = "EXP4"
# rootDir = "/media/cirlab/SeagateDrive/PeriodicEXP3/" + problem_instance + "/" + algorithmName + "/"
rootDir = "/home/cirlab/PeriodicEXP3/simulationResults/test/"
numPeriod = 24

# 0
# 13/24
# 14/24
# 17/24
# 18/24
# 23/24
optimalMinPerPhase = [16/7, 7/2, 4, 36/7, 4, 7/2]
print(optimalMinPerPhase)
numTimeSlotPerIteration = numTimeSlot//numRepeat
startPerPhase = [0, 13, 14, 17, 18, 23, 24]
numTimeSlotPerPhase = [(x * (numTimeSlotPerIteration//24)) + 1 for x in startPerPhase]
# print(numTimeSlotPerPhase); input()
# print("numTimeSlotPerIteration:", numTimeSlotPerIteration); input()
optimalMin = []
for i in range(1, len(optimalMinPerPhase) + 1):
    optimalMin += [optimalMinPerPhase[i-1]] * (numTimeSlotPerPhase[i] - numTimeSlotPerPhase[i-1])
# print(optimalMin)
# input()

# def getMinimumGainPerTimeSlot(inputCSVfile):
#     # distancePerTimeSlot = []
#     minGainPerTimeSlot = []
#     with open(inputCSVfile) as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',')
#         count = 0
#         for row in csv_reader:
#             if count > 0:
#                 # timeSlot = int(row[1])
#                 numDevicePerNetwork = row[3: 3 + numNetwork]; numDevicePerNetwork = [int(x) for x in numDevicePerNetwork]
#                 networkDataRate = row[3 + numNetwork : 3 + 2*numNetwork]; networkDataRate = [float(x) for x in networkDataRate]
#                 # gainPerDevice = [x/y for x, y in zip(networkDataRate, numDevicePerNetwork)]
#                 gainPerDevice = []
#                 for i in range(len(networkDataRate)):
#                     if numDevicePerNetwork[i] > 0: gainPerDevice.append(networkDataRate[i]/numDevicePerNetwork[i])
#                 # print(gainPerDevice)
#                 minGain = min(gainPerDevice)
#                 # (min users are getting) divide by (optimal min)
#                 # (opt - algo) / opt
#                 # optimal = optimalMin[(timeSlot%numTimeSlotPerIteration) - 1]
#                 # print("t = ", timeSlot, ", optimal at", (timeSlot%numTimeSlotPerIteration) - 1, " - ", optimalMin[(timeSlot%numTimeSlotPerIteration) - 1])
#                 # if timeSlot % 100 ==0: input()
#                 # print(minGain); #input()
#                 # distancePerTimeSlot.append((optimal - minGain)/optimal)
#                 minGainPerTimeSlot.append(minGain)
#             count += 1
#     csv_file.close()
#     return minGainPerTimeSlot
#     # end getMinimumGainPerTimeSlot

def getMinimumGainPerTimeSlot(dir):
    perDeviceGainPerTimeSlot =[]; minGainPerTimeSlot = []
    for i in range(numTimeSlot):
        perDeviceGain = []
        for j in range(numDevice): perDeviceGain.append(1000)
        perDeviceGainPerTimeSlot.append(perDeviceGain)
    # print(perDeviceGainPerTimeSlot)
    for deviceID in range(1, numDevice + 1):
        deviceCSVfile = dir + "device" + str(deviceID) + ".csv"
        with open(deviceCSVfile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            count = 0
            for row in csv_reader:
                # print(row); input()
                if count > 0:
                    timeSlot = int(row[1])
                    if algorithmName == "EXP3" or algorithmName == "BandwidthRatio": gain = float(row[4 + (2 * numNetwork)])
                    else: gain = float(row[4 + numPeriod + (2 * numNetwork)])
                    perDeviceGainPerTimeSlot[timeSlot - 1][deviceID - 1] = gain
                count += 1
    for i in range(len(perDeviceGainPerTimeSlot)):
        # print(perDeviceGainPerTimeSlot[i])
        minGainPerTimeSlot.append(min(perDeviceGainPerTimeSlot[i]))
        # print(perDeviceGainPerTimeSlot[i], " - ", minGainPerTimeSlot[-1]); input()
    return minGainPerTimeSlot
    # end getMinimumGainPerTimeSlot

def computeDistanceToOptimalMinimum(minGainPerTimeSlot):
    distancePerTimeSlot_allRuns = []
    for timeSlot in range(1, numTimeSlot + 1):
        optimal = optimalMin[(timeSlot % numTimeSlotPerIteration) - 1]
        minGain = minGainPerTimeSlot[timeSlot - 1]
        distancePerTimeSlot_allRuns.append(((optimal - minGain)/optimal)*100)
    return distancePerTimeSlot_allRuns
    # end computeDistanceToOptimalMinimum

def saveToCsv(outputCSVfile, headers, rows):
    myfile = open(outputCSVfile, "w+", newline='')
    out = csv.writer(myfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    if headers !=[]: out.writerow(headers)
    for row in rows: out.writerow(row)
    myfile.close()

def main():
    minGainPerTimeSlot_allRuns = [0]*numTimeSlot
    for runIndex in range(1, numRun + 1):
        dir = rootDir + "run" + str(runIndex) + "/"
        minGainPerTimeSlot = getMinimumGainPerTimeSlot(dir)# + "network.csv")
        # print(runIndex, minGainPerTimeSlot)
        minGainPerTimeSlot_allRuns = [x + y for x,y in zip(minGainPerTimeSlot_allRuns, minGainPerTimeSlot)]

    minGainPerTimeSlot_allRuns = [x/numRun for x in minGainPerTimeSlot_allRuns]
    # print(minGainPerTimeSlot_allRuns)

    distancePerTimeSlot_allRuns = computeDistanceToOptimalMinimum(minGainPerTimeSlot_allRuns)
    saveToCsv(rootDir + "distanceToOptimalMin.csv", ["timeSlot", "distance"], [[(i + 1), distancePerTimeSlot_allRuns[i]] for i in range(numTimeSlot)])
    # end main

if __name__ == '__main__': main()