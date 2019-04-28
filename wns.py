#!/usr/bin/python3

import simpy
from network import Network
import numpy as np
import global_setting
import argparse
import os
import time
import traceback
# import problem_instance
import problem_instance_v2
import analysis
from utility_method import generate_random_seed, computeDistanceToNashEquilibrium
# algorithms
import algo_exp3
import algo_periodicexp4.algo_periodicexp4 as algo_periodicexp4
import algo_bandwidthRatio
import pickle

# import computeDistanceToNE_mobility_v2
''' ______________________________________________________________________________ constants ______________________________________________________________________________ '''
# set from values passed as arguments when the program is executed
boolstr = lambda s : (s.lower() == 'true')
parser = argparse.ArgumentParser(description='Simulates the wireless network selection by a number of wireless devices in the service area.')
parser.add_argument('-log', dest="save_log_details", required=True, type=boolstr, help='whether to save log details [True/False]')
parser.add_argument('-plot', dest="show_plots", required=True, type=boolstr, help='whether to display graph plots [True/False]')
parser.add_argument('-n', dest="num_device", required=True, type=int, help='number of active devices in the service area')
parser.add_argument('-p', dest="problem_instance", required=True, type=str, help='problem instance to use')
parser.add_argument('-t', dest="num_time_slot", required=True, type=int, help='number of time slots in the simulation run')
parser.add_argument('-r', dest="run_index", required=True, type=int, help='current run index')
parser.add_argument('-rep', dest="num_repeats", required=True, type=int, help='number of repeats of problem instance')
parser.add_argument('-per', dest="period_option", required=True, type=int, help='period configuration to use')
parser.add_argument('-a', dest="algorithm_name", required=True, type=str, help='name of selection algorithm used by the devices')
parser.add_argument('-dir', dest="directory", required=True, type=str, help='root directory containing the simulation files')
parser.add_argument('-gamma', dest='learning_rate', required=True, type=float, help="the learning rate")
parser.add_argument('-o', dest="optimization", required=True, type=boolstr, help="whether to leverage any optimization")
args = parser.parse_args()
SAVE_LOG_DETAILS = args.save_log_details; global_setting.constants.update({'save_log_details':SAVE_LOG_DETAILS})
SHOW_PLOTS = args.show_plots; global_setting.constants.update({'show_plots':SHOW_PLOTS})
NUM_REPEATS = args.num_repeats; global_setting.constants.update({'num_repeats':NUM_REPEATS})
PERIOD_OPTION = args.period_option; global_setting.constants.update({'period_option':PERIOD_OPTION})
NUM_MOBILE_DEVICE = args.num_device; global_setting.constants.update({'num_mobile_device':NUM_MOBILE_DEVICE})
PROBLEM_INSTANCE_NAME = args.problem_instance; global_setting.constants.update({'problem_instance':PROBLEM_INSTANCE_NAME})
NUM_TIME_SLOT = args.num_time_slot; global_setting.constants.update({'num_time_slot':NUM_TIME_SLOT})
global_setting.constants.update({'run_num':args.run_index})
ALGORITHM_NAME = args.algorithm_name; global_setting.constants.update({'algorithm_name':ALGORITHM_NAME})
DIR = args.directory; global_setting.constants.update({'output_dir':DIR})
GAMMA = args.learning_rate; global_setting.constants.update({'gamma':GAMMA})
OPTIMIZATION = args.optimization; global_setting.constants.update({'OPTIMIZATION':OPTIMIZATION})
problem_instance_v2.initialize()    # retrieve the global variables

''' ____________________________________________________________________ setup and start the simulation ___________________________________________________________________ '''
startTime = time.time()
env = simpy.Environment()

if SAVE_LOG_DETAILS:
    if not os.path.exists(DIR): os.makedirs(DIR)  # create output directory if it doesn't exist

#instance, maxGain, numNetwork = problem_instance.PROBLEM_INSTANCES[PROBLEM_INSTANCE_NAME](NUM_TIME_SLOT)

if PROBLEM_INSTANCE_NAME == "continuous":
    f = open('networkDataRate.pkl', 'rb')  # 'r' for reading; can be omitted
    dataRate = pickle.load(f)  # load file content as mydict
    f.close()
    # print("data rate:", dataRate)
    networkDataRate = [dataRate[x][0] for x in range(len(dataRate))]
    maxGain = max([max(x) for x in dataRate])
else:
    networkDataRate = problem_instance_v2.getNetworkDataRate(PROBLEM_INSTANCE_NAME, 1)  # print(t, currentDataRate)
    maxGain = max(networkDataRate)
##### maxGain is maximum over whole simulation

numNetwork = len(networkDataRate)
# networkDataRate = problem_instance_v2.getNetworkDataRate(PROBLEM_INSTANCE_NAME, 1)
# numNetwork = len(networkDataRate); maxGain = max(networkDataRate)
networkList = [Network(0) for i in range(numNetwork)]
#networkList = [Network(NETWORK_BANDWIDTH[i]) for i in range(numNetwork)]        # create network objects and store in networkList
global_setting.constants.update({'network_list':networkList})

''' ____ configured global settings. now to import the stuff that uses it ____ '''
from mobile_device import MobileDevice
import logging_configure
import data_analyzer
logging_configure.initialize((DIR if SAVE_LOG_DETAILS else None))
''' __________________________________________________________________________ '''


periods = problem_instance_v2.PERIOD_OPTIONS[PERIOD_OPTION]
if PERIOD_OPTION <= 2: partitions = algo_periodicexp4.make_partition_cycles(NUM_TIME_SLOT, periods)
else: partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)

print("partitions:", partitions); input()
mobileDeviceList = [MobileDevice(networkList, trackDetailedStats=True,
                    maxGain=maxGain, partitions=partitions)
                    for i in range(NUM_MOBILE_DEVICE)] # create mobile device objects and store in mobileDeviceList

seed = generate_random_seed()
np.random.seed(seed)

results = []

gamma_function = lambda t : min(t**(-1/3),0.9)
# print("nashEquilibriumStateList:", nashEquilibriumStateList); input()
try:
    # proc = env.process(problem_instance.run_instance(env, networkList, instance))
    for i in range(NUM_MOBILE_DEVICE):
        if ALGORITHM_NAME == "EXP3":
            algorithm = algo_exp3.Exp3Algo(numNetwork, NUM_TIME_SLOT, seed=seed+i)
        elif ALGORITHM_NAME == "EXP4":
            algorithm = algo_periodicexp4.PeriodicExp4(NUM_TIME_SLOT, numNetwork, partitions, seed=seed+i, gamma = GAMMA)
            # self, T, K, functions, seed = 0, gamma = None
            #algorithm = algo_periodicexp4.algo_partition_cycles(NUM_TIME_SLOT, numNetwork, [1], gamma=0.5)
        elif ALGORITHM_NAME == "BandwidthRatio":
            algorithm = algo_bandwidthRatio.BandwidthRatioAlgo(numNetwork, NUM_TIME_SLOT, seed=seed + i)
        proc = env.process(mobileDeviceList[i].runAlgorithm(env, algorithm, results, gamma_function, PROBLEM_INSTANCE_NAME, OPTIMIZATION))
    env.run(until=proc)  # SIM_TIME)
except Exception:
    traceback.print_exc()

endTime = time.time()
timeTaken = endTime - startTime; unit = "seconds"
if timeTaken > (60 ** 2): timeTaken /= (60 ** 2); unit = "hours"
elif timeTaken > 60: timeTaken /= 60; unit = "minutes"

print("----- simulation completed in %s %s -----" % (timeTaken, unit))
# print("----- simulation completed -----")

# analysis
data_analyzer.analyze(results, [(m.deviceID, m.csvData) for m in mobileDeviceList], mobileDeviceList[0].networkCsvData)
# analysis.analyze(PROBLEM_INSTANCE_NAME, NUM_TIME_SLOT, mobileDeviceList[0].networkCsvData.rows, DIR, NUM_REPEATS)
# distance = computeDistanceToNE_mobility_v2.computeDistanceToNashEquilibrium(PROBLEM_INSTANCE_NAME, NUM_TIME_SLOT, mobileDeviceList[0].networkCsvData.rows,NUM_MOBILE_DEVICE)
# # distanceOld = computeDistanceToNashEquilibrium(PROBLEM_INSTANCE_NAME, NUM_TIME_SLOT, mobileDeviceList[0].networkCsvData.rows)
# print(distance)
# # print(distanceOld)
# # print(distance == distanceOld)
# print("results:", results)
# for result in results: print(result[1])


# write csvs
if SAVE_LOG_DETAILS: # and False:
    for mobileDevice in mobileDeviceList:
        mobileDevice.writeCsv()
    print("----- csvs written -----")
deviceDataList = [mobileDevice.csvData.rows for mobileDevice in mobileDeviceList]
# print(deviceDataList)
# print(periods, len(periods))
analysis.analyze(PROBLEM_INSTANCE_NAME, NUM_TIME_SLOT, mobileDeviceList[0].networkCsvData.rows,NUM_MOBILE_DEVICE, results, DIR, NUM_REPEATS, deviceDataList, len(periods),ALGORITHM_NAME)


''' _____________________________________________________________________________ end of file _____________________________________________________________________________ '''


# repeat instances
# instance, maxGain, numNetwork = problem_instance.repeat_instance(
#     NUM_TIME_SLOT, NUM_REPEATS,
#     problem_instance.PROBLEM_INSTANCES[PROBLEM_INSTANCE_NAME]
# )
# defines what list of labels to assign to time slots by partition functions;
# perdiods - a list of the number of labels used by the partition function
# if PERIOD_OPTION == 0: # EXP3
#     periods = [1]
#     partitions = algo_periodicexp4.make_partition_cycles(NUM_TIME_SLOT, periods)
# elif PERIOD_OPTION == 1: # EXP3, but reset every day
#     periods = [NUM_REPEATS]
#     partitions = algo_periodicexp4.make_partition_cycles(NUM_TIME_SLOT, periods)
# elif PERIOD_OPTION == 2: # unused
#     periods = list(range(1,15))
#     partitions = algo_periodicexp4.make_partition_cycles(NUM_TIME_SLOT, periods)
# elif PERIOD_OPTION == 3: # unused
#     periods = list(range(1,15))
#     periods = [i*NUM_REPEATS for i in periods]
#     partitions = algo_periodicexp4.make_partition_cycles(NUM_TIME_SLOT, periods)
# elif PERIOD_OPTION == 4:
#     pass #DISABLED
# elif PERIOD_OPTION == 5:
#     periods = list(range(1,15))
#     partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)
# elif PERIOD_OPTION == 6:
#     periods = list(range(1,40))
#     partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)
# elif PERIOD_OPTION == 7: #primes below 15
#     periods = [1,2,3,5,7,11,13]
#     partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)
# elif PERIOD_OPTION == 8: #primes below 40
#     periods = [1,2,3,5,7,11,13,17,19,23,29,31,37]
#     partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)
# elif PERIOD_OPTION == 9: #powers of 2 up to 16
#     periods = [1,2,4,8,16]
#     partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)
# elif PERIOD_OPTION == 10: #powers of 2 up to 1024
#     periods = [1,2,4,8,16,32,64,128,256,512,1024]
#     partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)
# elif PERIOD_OPTION == 11: # all numbers up to 100
#     periods = list(range(100))
#     partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)
# elif PERIOD_OPTION == 12: # primes below 100
#     periods = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
#     partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)
# elif PERIOD_OPTION == 13: # large primes only
#     periods = [53,59,61,67,71,73,79,83,89,97]
#     partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)
# """
# elif PERIOD_OPTION >= 14: # temp, delete
#     # 14 --> 1
#     periods = [PERIOD_OPTION-13]
#     partitions = algo_periodicexp4.make_repeating_partition_cycles(NUM_TIME_SLOT, NUM_REPEATS, periods)
# """