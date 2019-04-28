import csv
from statistics import median

numTimeSlotPerRetition = 1440
problemInstance = "continuous" #"change_in_data_rates_office" #
algorithmName = "EXP3"
rootDir = "/media/cirlab/SeagateDrive/PeriodicEXP3/" + problemInstance + "/" + algorithmName + "/"
# rootDir = "/media/anuja/SeagateDrive/PeriodicEXP3/" + problemInstance + "/" + algorithmName + "/"
# "/home/cirlab/PeriodicEXP3/simulationResults/"
# inputCSVfile = rootDir + "distanceToNashEquilibrium.csv"
inputCSVfile = rootDir + "distanceToNE_percentage_median.csv"
# outputCSVfile = rootDir + "distancePerRepetition.csv"

def getMedianDistancePerRepetition(inutCSVfile):
    global numTimeSlotPerRetition

    medianDistancePerRepetition = []
    meanDistancePerRepetition = []

    with open(inutCSVfile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count = 0; distanceCurrentRepetitionList = []
        for row in csv_reader:
            if count > 0:
                timeSlot = int(row[0])
                distanceCurrentRepetitionList.append(float(row[1]))
                if timeSlot%numTimeSlotPerRetition == 0:
                    medianDistancePerRepetition.append(median(distanceCurrentRepetitionList))
                    meanDistancePerRepetition.append(sum(distanceCurrentRepetitionList)/len(distanceCurrentRepetitionList))
                    distanceCurrentRepetitionList = []
            count += 1
    csv_file.close()
    return medianDistancePerRepetition, meanDistancePerRepetition

def saveCSVfile(outputCSVfile, header, data):
    myfile = open(outputCSVfile, "w+", newline='')
    out = csv.writer(myfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    if header != []: out.writerow(header)
    for row in data: out.writerow(row)
    myfile.close()

def main():
    global rootDir

    medianDistancePerRepetition, meanDistancePerRepetition = getMedianDistancePerRepetition(inputCSVfile)
    # for i in range(len(medianDistancePerRepetition)): print(medianDistancePerRepetition[i])
    # saveCSVfile(rootDir + "medianDistancePerRepetition.csv", ["timeslot", "median"], [[i+1, medianDistancePerRepetition[i]] for i in range(len(medianDistancePerRepetition))])
    # saveCSVfile(rootDir + "meanDistancePerRepetition.csv", ["timeslot", "mean"], [[i+1, meanDistancePerRepetition[i]] for i in range(len(meanDistancePerRepetition))])
    saveCSVfile(rootDir + "medianDistancePerRepetition_percentage_median.csv", ["timeslot", "median"], [[i + 1, medianDistancePerRepetition[i]] for i in range(len(medianDistancePerRepetition))])
    saveCSVfile(rootDir + "meanDistancePerRepetition_percentage_median.csv", ["timeslot", "mean"], [[i+1, meanDistancePerRepetition[i]] for i in range(len(meanDistancePerRepetition))])
    print([[i+1, medianDistancePerRepetition[i]] for i in range(len(medianDistancePerRepetition))])

if __name__ == '__main__': main()