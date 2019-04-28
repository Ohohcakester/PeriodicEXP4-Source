import matplotlib.pyplot as plt
import numpy as np
import csv
from mpl_toolkits import mplot3d

# NUM_MOBILE_DEVICE = 20
# NUM_TIME_SLOT = 86400
# NUM_REPEATS = 60
# NUM_RUN = 20
# ALGORITHM = "EXP4"
# OUTPUT_DIR = ""
# NUM_NETWORK = 3
# NUM_PERIOD = 24
NUM_MOBILE_DEVICE = 20
NUM_TIME_SLOT = 86400
NUM_REPEATS = 60
NUM_RUN = 20
ALGORITHM = "EXP4"
OUTPUT_DIR = ""
NUM_NETWORK = 3
NUM_PERIOD = 24
SKIP_STEP = 1


def get_subdivisions():
    T = NUM_TIME_SLOT
    R = NUM_REPEATS
    for i in range(R):
        start, end = T * i // R, T * (i + 1) // R
        yield start, end

def plot_3d(x, y, zs_labels, skip_step=1, color=None):
    ax = plt.axes(projection='3d')

    x_filtered = x[::skip_step]
    X, Y = np.meshgrid(x_filtered, y)

    for z, label in zs_labels:
        z_filtered = z[::skip_step]
        Z = np.array(z_filtered)
        if color != None:
            ax.plot_surface(X, Y, Z.T, label=label, color=color)
        else:
            ax.plot_surface(X, Y, Z.T, label=label)


def save_fig(outputDir, runIndex):
    figure_name = plt.gcf().get_label().replace(' ', '_') + "_run" + str(runIndex)
    plt.savefig('%s\\%s.png' % (outputDir, figure_name))

def plot_graphs(OUTPUT_DIR, dir, runIndex):
    totalProbs = [[0] * NUM_NETWORK for i in range(NUM_TIME_SLOT)]

    for deviceID in range(1, NUM_MOBILE_DEVICE + 1):
        CSVfile = dir + "device" + str(deviceID) + ".csv"
        # probList = [get_data('probability%d' % i, csvData) for i in range(1, NUM_NETWORK + 1)]
        probList = loadProbabilityList(CSVfile)
        # print(deviceID, "probList:", probList);

        for t in range(NUM_TIME_SLOT):
            for i in range(NUM_NETWORK):
                totalProbs[t][i] += probList[i][t]
        print("done devcie", deviceID)
    # print(totalProbs)
    saveCSVfile(OUTPUT_DIR + "totalProbability_run" + str(runIndex) + ".csv", totalProbs)

    # plot probability distribution over time (3D) for each device, and total probability distribution
    x = list(range(1, NUM_TIME_SLOT + 1))
    y = list(range(1, NUM_NETWORK + 1))

    plt.figure('Total Probability')
    plot_3d(x, y, [(totalProbs, 'total')], skip_step=SKIP_STEP, color='#ff8020')
    save_fig(OUTPUT_DIR, runIndex)
    return totalProbs
    # plt.show()

def loadProbabilityList(CSVfileName):
    probabilityList = []
    for i in range(NUM_NETWORK): probabilityList.append([])

    with open(CSVfileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                if ALGORITHM == "EXP3" or ALGORITHM == "BandwidthRatio":
                    probabilityDistribution = row[2 + NUM_NETWORK: 2 + 2 * NUM_NETWORK]
                else:
                    probabilityDistribution = row[2 + NUM_PERIOD + NUM_NETWORK: 2 + NUM_PERIOD + 2 * NUM_NETWORK]
                probabilityDistribution = [float(x) for x in probabilityDistribution]
                for netIndex in range(NUM_NETWORK): probabilityList[netIndex].append(probabilityDistribution[netIndex])
            line_count += 1
    csv_file.close()
    return probabilityList

def saveCSVfile(outputCSVfile, totalProbs):
    myfile = open(outputCSVfile, "w+", newline='')
    out = csv.writer(myfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    out.writerow(['network' + str(i) for i  in range(1, NUM_NETWORK + 1)])
    for row in totalProbs: out.writerow(row)
    myfile.close()

def main():
    totalProbsAllRun = [[0] * NUM_NETWORK for i in range(NUM_TIME_SLOT)]

    for runIndex in range(1, NUM_RUN  + 1):
        currentRunTotalProbList = plot_graphs(OUTPUT_DIR, OUTPUT_DIR + "run" + str(runIndex) + "/", runIndex)
        for t in range(NUM_TIME_SLOT):
            for i in range(NUM_NETWORK):
                totalProbsAllRun[t][i] += currentRunTotalProbList[t][i]
        print("done run", runIndex)

    x = list(range(1, NUM_TIME_SLOT + 1))
    y = list(range(1, NUM_NETWORK + 1))

    for t in range(NUM_TIME_SLOT):
        for i in range(NUM_NETWORK):
            totalProbsAllRun[t][i] /= NUM_RUN

    plt.figure('Total Probability')
    plot_3d(x, y, [(totalProbsAllRun, 'total')], skip_step=SKIP_STEP, color='#ff8020')
    save_fig(OUTPUT_DIR, "all")

    saveCSVfile(OUTPUT_DIR + "totalProbability_allRun.csv", totalProbsAllRun)

main()

# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
#
# NUM_DEVICE = 20
# NUM_RUN = 1
# DIR = "/home/cirlab/PeriodicEXP3/simulationResults/test/"
# NUM_NETWORK = 3
# NUM_TIME_SLOT = 2880
# ALGORITHM_NAME = "EXP4"
# NUM_PERIOD = 24
#
# def get_data(name, csvData):
#     for index, header in enumerate(csvData.headers):
#         if header == name:
#             return [row[index] for row in csvData.rows]
#
# def plot_3d(x,y,zs_labels,skip_step=1, color=None):
#     ax = plt.axes(projection='3d')
#
#     x_filtered = x[::skip_step]
#     X, Y = np.meshgrid(x_filtered, y)
#
#     for z, label in zs_labels:
#         z_filtered = z[::skip_step]
#         Z = np.array(z_filtered)
#         if color != None:
#             ax.plot_surface(X, Y, Z.T, label=label, color=color)
#         else:
#             ax.plot_surface(X, Y, Z.T, label=label)
#
# def computeTotalProbability(INPUT_DIR, NUM_DEVICE, NUM_NETWORK, NUM_TIME_SLOT):
#     '''
#     description: computes total probabilities for each network per time slot - for a single run
#     return:      list of total probabilities for each network per time slot for one run
#     '''
#     global ALGORITHM_NAME, NUM_PERIOD
#
#     def save_fig():
#         # if not SAVE_LOG_DETAILS: return
#         figure_name = plt.gcf().get_label().replace(' ', '_')
#         plt.savefig('%s\\%s.png' % (INPUT_DIR, figure_name))
#
#     # armChoices = []
#     # for deviceID, csvData in deviceCsvDatas:
#     #     armChoices.append((deviceID, get_data('Current network', csvData)))
#
#     totalProbs = [[0] * NUM_NETWORK for i in range(NUM_TIME_SLOT)]
#     # probs = []
#     # highestProbs = []
#     # for deviceID, csvData in deviceCsvDatas:
#     for deviceID in range(1, NUM_DEVICE + 1):
#         # probList = [get_data('probability%d' % i, csvData) for i in range(1, NUM_NETWORK + 1)]
#         CSVfile = INPUT_DIR + "device" + str(deviceID) + ".csv";  probList = []
#         if ALGORITHM_NAME == "EXP3" or ALGORITHM_NAME == "BandwidthRatio":
#             # probabilityDistribution = row[2 + numNetwork: 2 + 2 * numNetwork]
#             colnames = ['RunNo', 'TimeSlot'] + \
#                        ['w_arm' + str(i) for i in range(1, NUM_NETWORK + 1)] + \
#                        ['probability' + str(i) for i in range(1, NUM_NETWORK + 1)] + \
#                        ['gamma', 'currentNetwork', 'gain'] + \
#                        ['Bandwidth' + str(i) for i in range(1, NUM_NETWORK + 1)] + ['maxGain']
#         else:
#             colnames = ['RunNo', 'TimeSlot'] + ['w_partitionF' + str(i) for i in range(1, NUM_PERIOD + 1)] + \
#                        ['w_arm' + str(i) for i in range(1, NUM_NETWORK + 1)] + \
#                        ['probability' + str(i) for i in range(1, NUM_NETWORK + 1)] +\
#                        ['gamma', 'currentNetwork', 'gain'] + \
#                        ['Bandwidth' + str(i) for i in range(1, NUM_NETWORK + 1)] + ['maxGain']
#             # probabilityDistribution = row[2 + numPeriod + numNetwork: 2 + numPeriod + 2 * numNetwork]
#         df = pd.read_csv(CSVfile)
#         for i in range(1, NUM_NETWORK + 1):
#             columnName = 'probability' + str(i)
#             probList.append(df[columnName])
#         print("device:", deviceID, ", probList:", len(probList[0]))
#         # largests = [max(enumerate(probs), key=lambda tup: tup[1])[0] + 1 for probs in zip(*probList)]
#         # highestProbs.append((deviceID, largests))
#
#         # probs.append((deviceID, [list(i) for i in zip(*probList)]))
#
#         for t in range(NUM_TIME_SLOT):
#             for i in range(NUM_NETWORK):
#                 totalProbs[t][i] += probList[i][t]
#
#     print(totalProbs)
#
#     # dataRateList = [get_data('dataRate%d' % i, networkCsvData) for i in range(1, NUM_NETWORK + 1)]
#     # dataRateList = [list(i) for i in zip(*dataRateList)]
#
#     SKIP_STEP = 1
#
#     # plot bandwidth graph
#     # if True:
#     #     x = list(range(1, NUM_TIME_SLOT + 1))
#     #     y = list(range(1, NUM_NETWORK + 1))
#     #     plt.figure('Network Bandwidths')
#     #     plot_3d(x, y, [(dataRateList, 'bandwidth')], skip_step=SKIP_STEP)
#     #     save_fig()
#     #
#     # # plot highest probability arm of each device
#     # if True:
#     #     plt.figure('Highest Probability Arms')
#     #     x = range(1, NUM_TIME_SLOT + 1)
#     #     for deviceID, arms in highestProbs:
#     #         y = [v + deviceID / NUM_MOBILE_DEVICE / 4 for v in arms]
#     #         plt.plot(x, y, label='%d' % deviceID)
#     #     save_fig()
#     #
#     # # plot probability distribution over time (3D) for each device, and total probability distribution
#     # if True:
#     #     x = list(range(1, NUM_TIME_SLOT + 1))
#     #     y = list(range(1, NUM_NETWORK + 1))
#     #     for deviceID, deviceProbs in probs:
#     #         plt.figure('Device %d Probability' % deviceID)
#     #         plot_3d(x, y, [(deviceProbs, '%d' % deviceID)], skip_step=SKIP_STEP)
#     #         save_fig()
#
#     x = list(range(1, NUM_TIME_SLOT + 1))
#     y = list(range(1, NUM_NETWORK + 1))
#
#     plt.figure('Total Probability')
#     plot_3d(x, y, [(totalProbs, 'total')], skip_step=SKIP_STEP, color='#ff8020')
#     # plot_3d(x,y,[(deviceProbs,'%d'%deviceID) for deviceID, deviceProbs in probs], skip_step=500)
#     save_fig()
#
#     # # plot probability distribution at final timestep (2D)
#     # if True:
#     #     plt.figure('Final Timestep Probabilities')
#     #     x = range(1, NUM_NETWORK + 1)
#     #     for deviceID, deviceProbs in probs:
#     #         finalProbs = deviceProbs[-1]
#     #         plt.plot(x, finalProbs, label='%d' % deviceID)
#     #     save_fig()
#     #
#     # if SHOW_PLOTS:
#     #     plt.show()
#
# def main():
#     global NUM_DEVICE, NUM_NETWORK, NUM_TIME_SLOT, NUM_RUN, DIR
#
#     for runIndex in range(1, NUM_RUN + 1): # process data for each run
#         INPUT_DIR = DIR + "run" + str(runIndex) + "/"
#         # deviceCsvDatas = [(m.deviceID, m.csvData) for m in mobileDeviceList]
#         computeTotalProbability(INPUT_DIR, NUM_DEVICE, NUM_NETWORK, NUM_TIME_SLOT)
#         # computeTotalProbability(inputCSVfile, deviceCsvDatas, NUM_NETWORK, NUM_TIME_SLOT, OUTPUT_DIR)
#         # deviceCsvDatas = [(m.deviceID, m.csvData) for m in mobileDeviceList]
#     return
#
# main()
# #
# # save data for each run
# # average over runs and plot