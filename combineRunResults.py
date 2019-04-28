import csv
import pandas
import statistics
import argparse

# rootDir = "/home/cirlab/PeriodicEXP3/simulationResults/"
# numRun = 2
parser = argparse.ArgumentParser(description='Process results from several runs.')
parser.add_argument('-dir', dest="directory", required=True, type=str, help='root directory containing the simulation files')
parser.add_argument('-n', dest="num_run", required=True, type=int, help="number of simulation runs")
parser.add_argument('-p', dest="problem_instance", required=True, type=str, help='problem instance being considered')
args = parser.parse_args()
dir = args.directory
numRun = int(args.num_run)
problem_instance = args.problem_instance

def saveToCsv(outputCSVfile, headers, rows):
    myfile = open(outputCSVfile, "w+", newline='')
    out = csv.writer(myfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    if headers !=[]: out.writerow(headers)
    for row in rows: out.writerow(row)
    myfile.close()

def processCumulativeGainPerDevice(dir, numRun):
    '''
    description: retrieves the cumulative gain of each device for all runs, computes and returns the mean, median, max and min
    args:        the root directory name where details of all runs are stored in a sub-directory, the number of runs
    return:      the mean, median, max and min cumulative gain observed by the devices
    '''
    cumulativeGainList = []
    for runIndex in range(1, numRun + 1):
        CSVfileName = dir + "run" + str(runIndex) + "/cumulativeGainPerDevice.csv"
        colnames = ['dummy', 'cumulativeGain']
        dataFromFile = pandas.read_csv(CSVfileName, names=colnames)
        cumulativeGainList += dataFromFile.cumulativeGain.tolist()
    mean = (sum(cumulativeGainList)/len(cumulativeGainList))/(8*1000)   # convert from Mbits to GB
    median = (statistics.median(cumulativeGainList))/(8*1000)           # convert from Mbits to GB
    minimum = (min(cumulativeGainList))/(8*1000)                        # convert from Mbits to GB
    maximum = (max(cumulativeGainList))/(8*1000)                        # convert from Mbits to GB

    return cumulativeGainList, mean, median, minimum, maximum
    # end processCumulativeGainPerDevice

def combineDistanceToNashEquilibrium(dir, numRun):
    '''
    description: combines the distance to Nash equilibrium per time slot for all runs, by computing the average over runs,
                 and returns them
    args:        the root directory name where details of all runs are stored in a sub-directory, the number of runs
    return:      average (over runs) per time slots distance to Nash equilibrium
    '''
    distancePerTimeSlot = []
    for runIndex in range(1, numRun + 1):
        CSVfileName = dir + "run" + str(runIndex) + "/distanceToNashEquilibrium.csv"
        colnames = ['timeSlot', 'distance']
        dataFromFile = pandas.read_csv(CSVfileName, names=colnames)
        distanceList = dataFromFile.distance.tolist()[1:]   # drop first element which is the header
        distanceList = [float(x) for x in distanceList]     # convert all elements to numeric
        distancePerTimeSlot = distanceList if distancePerTimeSlot ==[] else [x + y for x, y in zip(distancePerTimeSlot, distanceList)]
    return [x/numRun for x in distancePerTimeSlot]
    # end combineDistanceToNashEquilibrium

def combineStability(dir, numRun):
    '''
    decsrription: combines stability results for each run; saves the total number of runs that stabilized and the stable
                  states, with a count for each stable state
    args:         the root directory name where details of all runs are stored in a sub-directory, the number of runs
    return:
    '''
    numStableRun = 0
    stableStateList = []
    stableStateCount = []
    repetitionAtWhichStabilizedList = []

    for runIndex in range(1, numRun + 1):
        CSVfileName = dir + "run" + str(runIndex) + "/stability.csv"
        print(CSVfileName)
        with open(CSVfileName) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            count = 0
            for row in csv_reader:
                if count >= 2: break
                if count == 0:          # stable state
                    stableState = row[1]
                    print(stableState, stableStateList)
                    if stableState in stableStateList:
                        # print("already in list")
                        stableStateCount[stableStateList.index(stableState)] += 1
                    else:
                        # print("not in list");
                        stableStateList.append(stableState); stableStateCount.append(1); repetitionAtWhichStabilizedList.append([])
                elif count == 1:        # repetition in which stabilized
                    repetition = int(row[1])
                    repetitionAtWhichStabilizedList[stableStateList.index(stableState)].append(repetition)
                count += 1
        csv_file.close()
        if stableState != '[]': numStableRun += 1

    return numStableRun, stableStateList, stableStateCount, repetitionAtWhichStabilizedList

def main():
    global dir, numRun, problem_instance

    # dir = rootDir + algorithmName +"/"
    cumulativeGainList, mean, median, minimum, maximum = processCumulativeGainPerDevice(dir, numRun)
    print(mean, median, minimum, maximum)
    distance = combineDistanceToNashEquilibrium(dir, numRun)

    # save the details to individual files
    saveToCsv(dir + "cumulativeGainPerDevice.csv", ["", "cumulative gain (GB)"], [["mean", mean], ["median", median], ["min", minimum], ["max", maximum]])
    saveToCsv(dir + "distanceToNashEquilibrium.csv", ["timeSlot", "distance"], [[i + 1, distance[i]] for i in range(len(distance))])
    saveToCsv(dir + "cumulativeGainPerDeviceList.csv", [], [[0, cumulativeGainList[i]] for i in range(len(cumulativeGainList))])

    if problem_instance != 'continuous':
        print("combining stability...")
        numStableRun, stableStateList, stableStateCount, repetitionAtWhichStabilizedList = combineStability(dir, numRun)
        saveToCsv(dir + "stability.csv", [],[["No. of stable run:", numStableRun], ["Stables state(s):", stableStateList], ["Count for each state:", stableStateCount], ["Repetition at which stabilized:", repetitionAtWhichStabilizedList]])
    # end main

if __name__ == '__main__': main()