'''
@description:   Defines utility methods used by other programs (python files)
'''
import csv

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

class CsvData(object):
    def __init__(self, filepath, headers):
        self.filepath = filepath
        self.headers = headers
        self.rows = []

    def addRow(self, row):
        self.rows.append(tuple(row))

    def saveToFile(self):
        saveToCsv(self.filepath, self.headers, self.rows)
# end CsvData class

def saveToCsv(outputCSVfile, headers, rows):
    myfile = open(outputCSVfile, "w+", newline='')
    out = csv.writer(myfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    out.writerow(headers)
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