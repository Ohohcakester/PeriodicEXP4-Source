from statistics import mean, median, stdev
from math import sqrt
import csv

numRun = 20
rootDir = "/media/cirlab/SeagateDrive/PeriodicEXP3/change_in_data_rates_office/BandwidthRatio/"   # "/home/cirlab/PeriodicEXP3/simulationResults/test/"

def extractCumulativeGainDetail(cumulativeGainList):
    return mean(cumulativeGainList), median(cumulativeGainList), stdev(cumulativeGainList)

def extractDataFromFile(inputCSVfile):
    cumulativeGain = []
    with open(inputCSVfile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            cumulativeGain.append(float(row[1])/(8*1000))
    csv_file.close()
    return cumulativeGain
    # end extractDataFromFile

def main():
    meanList = []; medianList = []; stdevList = []

    for runIndex in range(1, numRun + 1):
        CSVfileName = rootDir + "run" + str(runIndex) + "/cumulativeGainPerDevice.csv"
        cumulativeGainList= extractDataFromFile(CSVfileName)
        meanCumulativeGain, medianCumulativeGain, stdevCumulativeGain = extractCumulativeGainDetail(cumulativeGainList)
        print(meanCumulativeGain, medianCumulativeGain, stdevCumulativeGain)
        meanList.append(meanCumulativeGain)
        medianList.append(medianCumulativeGain)
        stdevList.append(stdevCumulativeGain)
    print(meanList, medianList, stdevList)
    # print(median(meanList), median(medianList), median(stdevList))
    meanMean = mean(meanList)
    meanStdev = sqrt(sum([x**2 for x in stdevList])/numRun)
    print("Average mean", "Average standard deviation")
    print(meanMean, meanStdev)
if __name__ == '__main__': main()