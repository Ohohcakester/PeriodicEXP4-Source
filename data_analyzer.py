import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import statistics
import global_setting
from logging_configure import logger
import random

SHOW_PLOTS = global_setting.constants['show_plots']
SAVE_LOG_DETAILS = global_setting.constants['save_log_details']
NUM_MOBILE_DEVICE = global_setting.constants['num_mobile_device']
NUM_TIME_SLOT = global_setting.constants['num_time_slot']
NUM_REPEATS = global_setting.constants['num_repeats']
RUN_NUM = global_setting.constants['run_num']
ALGORITHM = global_setting.constants['algorithm_name']
OUTPUT_DIR = global_setting.constants['output_dir']
networkList = global_setting.constants['network_list']
NUM_NETWORK = len(networkList)

def weighted_choice(seq, weights):
    w = np.asarray(weights)
    p = w / w.sum()
    return np.random.choice(seq, p=w)

def get_subdivisions():
    T = NUM_TIME_SLOT
    R = NUM_REPEATS
    for i in range(R):
        start, end = T*i//R, T*(i+1)//R
        yield start, end

def get_data(name, csvData):
    for index, header in enumerate(csvData.headers):
        if header == name:
            return [row[index] for row in csvData.rows]

def plot_3d(x,y,zs_labels,skip_step=1, color=None):
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

    #ax.set_xlabel('X Label')
    #ax.set_ylabel('Y Label')
    #ax.set_zlabel('Z Label')

def plot_graphs(results, deviceCsvDatas, networkCsvData):
    def save_fig():
        if not SAVE_LOG_DETAILS: return
        figure_name = plt.gcf().get_label().replace(' ', '_')
        plt.savefig('%s\\%s.png' % (OUTPUT_DIR, figure_name))

    armChoices = []
    for deviceID, csvData in deviceCsvDatas:
        armChoices.append((deviceID, get_data('Current network', csvData)))

    totalProbs = [[0]*NUM_NETWORK for i in range(NUM_TIME_SLOT)]
    probs = []
    highestProbs = []
    for deviceID, csvData in deviceCsvDatas:
        probList = [get_data('probability%d'%i, csvData) for i in range(1,NUM_NETWORK+1)]
        largests = [max(enumerate(probs), key=lambda tup:tup[1])[0]+1 for probs in zip(*probList)]
        highestProbs.append((deviceID, largests))

        probs.append((deviceID, [list(i) for i in zip(*probList)]))

        for t in range(NUM_TIME_SLOT):
            for i in range(NUM_NETWORK):
                totalProbs[t][i] += probList[i][t]

    dataRateList = [get_data('dataRate%d'%i, networkCsvData) for i in range(1,NUM_NETWORK+1)]
    dataRateList = [list(i) for i in zip(*dataRateList)]
    
    SKIP_STEP = 1

    # plot bandwidth graph
    if True:
        x = list(range(1,NUM_TIME_SLOT+1))
        y = list(range(1,NUM_NETWORK+1))
        plt.figure('Network Bandwidths')
        plot_3d(x,y,[(dataRateList,'bandwidth')],skip_step=SKIP_STEP)
        save_fig()

    # plot highest probability arm of each device
    if True:
        plt.figure('Highest Probability Arms')
        x = range(1,NUM_TIME_SLOT+1)
        for deviceID, arms in highestProbs:
            y = [v+deviceID/NUM_MOBILE_DEVICE/4 for v in arms]
            plt.plot(x, y, label='%d'%deviceID)
        save_fig()

    # plot probability distribution over time (3D) for each device, and total probability distribution
    if True:
        x = list(range(1,NUM_TIME_SLOT+1))
        y = list(range(1,NUM_NETWORK+1))
        for deviceID, deviceProbs in probs:
            plt.figure('Device %d Probability' % deviceID)
            plot_3d(x,y,[(deviceProbs,'%d'%deviceID)],skip_step=SKIP_STEP)
            save_fig()

        plt.figure('Total Probability')
        plot_3d(x,y,[(totalProbs,'total')], skip_step=SKIP_STEP, color='#ff8020')
        #plot_3d(x,y,[(deviceProbs,'%d'%deviceID) for deviceID, deviceProbs in probs], skip_step=500)
        save_fig()

    # plot probability distribution at final timestep (2D)
    if True:
        plt.figure('Final Timestep Probabilities')
        x = range(1,NUM_NETWORK+1)
        for deviceID, deviceProbs in probs:
            finalProbs = deviceProbs[-1]
            plt.plot(x,finalProbs, label='%d'%deviceID)
        save_fig()

    if SHOW_PLOTS:
        plt.show()

def print_results(results, deviceCsvDatas, networkCsvData):
    deviceCsvDatas = deviceCsvDatas[:]
    deviceCsvDatas.sort(key=lambda pair:pair[0]) # sort by device ID

    # exact min bandwidth from best possible allocation
    def computeOptMinBandwidth(nUsers, dataRates):
        nextBandwidths = np.array(dataRates, dtype='f')
        originalRates = np.array(dataRates)
        nextCounts = np.array([1]*len(dataRates))
        for i in range(nUsers):
            index = np.argmax(nextBandwidths)
            lowestBandwidth = nextBandwidths[index]
            nextCounts[index] += 1
            nextBandwidths[index] = originalRates[index]/nextCounts[index]
        return lowestBandwidth.item()

    # estimated expected min bandwidth from a uniform distribution allocation
    def estimateUniformMinBandwidth(nUsers, dataRates):
        numNetworks = len(dataRates)
        counts = [0]*numNetworks
        for i in range(nUsers): counts[random.randrange(numNetworks)] += 1
        return min(dataRate/count for dataRate,count in zip(dataRates,counts) if count>0)

    # estimated expected min bandwidth from a uniform distribution allocation
    def estimateWeightedMinBandwidth(nUsers, dataRates):
        numNetworks = len(dataRates)
        seq = list(range(numNetworks))
        w = np.asarray(dataRates)
        p = w / w.sum()
        counts = [0]*numNetworks
        for i in range(nUsers): counts[np.random.choice(seq, p=p)] += 1
        return min(dataRate/count for dataRate,count in zip(dataRates,counts) if count>0)


    for deviceID, cumulativeGain, maxCumulativeGain in results:
        logger.info("Device %d - Score: %.2f, Max: %.2f, Regret: %.2f" % 
            (deviceID, cumulativeGain, maxCumulativeGain, maxCumulativeGain-cumulativeGain))

    cumulativeGains = [x[1] for x in results]
    cumulativeGains = [x/NUM_TIME_SLOT*NUM_MOBILE_DEVICE for x in cumulativeGains] # normalize

    dataRateList = [get_data('dataRate%d'%i, networkCsvData) for i in range(1,NUM_NETWORK+1)]
    dataRateList = [list(i) for i in zip(*dataRateList)] #transpose
    
    # timestep-wise min (we use this because we can make total min higher by rotating devices)
    allGains = [get_data('gain', csvData) for deviceID,csvData in deviceCsvDatas]
    allGains = [list(i) for i in zip(*allGains)] #transpose
    minGains = [min(gains) for gains in allGains]
    stepwiseMin = statistics.mean(minGains)*NUM_MOBILE_DEVICE

    # opt min (per step)
    optMinBandwidths = [computeOptMinBandwidth(NUM_MOBILE_DEVICE, dataRates) for dataRates in dataRateList]
    optMinBandwidth = statistics.mean(optMinBandwidths)*NUM_MOBILE_DEVICE

    # uniform min (per step)
    uniformMinBandwidths = [estimateUniformMinBandwidth(NUM_MOBILE_DEVICE, dataRates) for dataRates in dataRateList]
    uniformMinBandwidth = statistics.mean(uniformMinBandwidths)*NUM_MOBILE_DEVICE

    # optimally weighted min (per step)
    weightedMinBandwidths = [estimateWeightedMinBandwidth(NUM_MOBILE_DEVICE, dataRates) for dataRates in dataRateList]
    weightedMinBandwidth = statistics.mean(weightedMinBandwidths)*NUM_MOBILE_DEVICE

    for index, startEnd in enumerate(get_subdivisions()):
        start, end = startEnd
        averageStepwiseMin = statistics.mean(minGains[start:end])*NUM_MOBILE_DEVICE
        averageOptMin = statistics.mean(optMinBandwidths[start:end])*NUM_MOBILE_DEVICE
        averageWMin = statistics.mean(weightedMinBandwidths[start:end])*NUM_MOBILE_DEVICE
        logger.info('Div%dStepMin: %.2f' % (index, averageStepwiseMin))
        logger.info('Div%dOptMin: %.2f' % (index, averageOptMin))
        logger.info('Div%dWMin: %.2f' % (index, averageWMin))

    logger.info(", ".join((
        "MeanTotal: %.2f" % statistics.mean(cumulativeGains),
        "LowestTotal: %.2f" % min(cumulativeGains),
        "HighestTotal: %.2f" % max(cumulativeGains),
    )))
    logger.info(", ".join((
        "stdevTotal: %.2f" % statistics.stdev(cumulativeGains),
        "Mean-SD: %.2f" % (statistics.mean(cumulativeGains) - statistics.stdev(cumulativeGains)),
        "Mean+SD: %.2f" % (statistics.mean(cumulativeGains) + statistics.stdev(cumulativeGains)),
    )))
    logger.info(", ".join((
        "stepwiseMin: %.2f" % stepwiseMin,
    )))
    logger.info(", ".join((
        "optMinBandwidth: %.2f" % optMinBandwidth,
        "uniformMinBandwidth: %.2f" % uniformMinBandwidth,
        "weightedMinBandwidth: %.2f" % weightedMinBandwidth,
    )))

def analyze(results, deviceCsvDatas, networkCsvData):
    print_results(results, deviceCsvDatas, networkCsvData)
    plot_graphs(results, deviceCsvDatas, networkCsvData)