'''
description: defines problem instances for simulation
'''

# num_repeat
# period_option
# data_rates /problem_instance?
# devices?
# changing data rates of same set of networks
# number of networks changes
# number of devices changes
# dat rates affected by distance of devices from access points

import global_setting
from utility_method import computeNashEquilibriumState
from math import ceil
# import fractions


# this file is imported in wns.py before the values of the global parameters are set; their correct values are set in initialize()
NUM_MOBILE_DEVICE = NUM_TIME_SLOT = NUM_REPEATS = 0; PROBLEM_INSTANCES = {}; PERIOD_OPTIONS = {}


def initialize():
    '''
    description: retrieves the values of the global parameters; they're are set after this file is imported
                 defines the problem instances and the period options
    args:        none
    return:      None
    '''
    global NUM_MOBILE_DEVICE, NUM_TIME_SLOT, NUM_REPEATS, PROBLEM_INSTANCES, PERIOD_OPTIONS

    NUM_MOBILE_DEVICE = global_setting.constants['num_mobile_device']
    NUM_TIME_SLOT = global_setting.constants['num_time_slot']
    NUM_REPEATS = global_setting.constants['num_repeats']

    ''' definition of problem instances '''
    PROBLEM_INSTANCES = {
        # number of devices, number of networks and data rates of networks remain unchanged
        'static':{
            0: {
                'data_rate': [4, 7, 22],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1))],
                # 'NEstate_list': computeNashEquilibriumState(NUM_MOBILE_DEVICE, 3, [4, 7, 22])
            }
        },

        'change_in_data_rates_simple': {
            0: {
                'data_rate': [7, 14, 44],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1))],
                'NEstate_list': [[0, 1, 2]]  # computeNashEquilibriumState(NUM_MOBILE_DEVICE, 3, [4, 7, 22])
            },
            1.0 / 2: {
                'data_rate': [36, 7, 22],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1))],
                'NEstate_list': [[2, 0, 1]]  # computeNashEquilibriumState(NUM_MOBILE_DEVICE, 3, [18, 4, 11])
            }
        },

        # number of devices and number of networks remain unchanged, but data rates of networks change
        # e.g. networks in an office; at 9am wifi networks poor, cellular better; at noon most people leave for lunch, cellular gets worse, WiFi gets better;
        # when they're back from lunch it's similar to before they leave for lunch; after office hours, WiFi gets better and cellular worse - e.g., assuming
        # they prefer WiFi when at office and switch to cellular while having lunch or on the way home (when WiFi is not available)
        'change_in_data_rates_office':{
            0: {
                'data_rate': [7, 14, 44],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1))],
                'NEstate_list': [[2, 4, 14]]    # computeNashEquilibriumState(NUM_MOBILE_DEVICE, 3, [4, 7, 22])
            },
            1.0 / 4: {
                'data_rate': [36, 7, 22],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1))],
                'NEstate_list': [[11, 2, 7]]    # computeNashEquilibriumState(NUM_MOBILE_DEVICE, 3, [18, 4, 11])
            }
            ,
            1.0 / 2: {
                'data_rate': [9, 16, 40],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1)),
                                list(range(1, NUM_MOBILE_DEVICE + 1))],
                'NEstate_list': [[2, 5, 13]]    # computeNashEquilibriumState(NUM_MOBILE_DEVICE, 3, [7, 13, 13])
            },
            3.0 / 4: {
                'data_rate': [40, 4, 21],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1)),
                                list(range(1, NUM_MOBILE_DEVICE + 1))],
                'NEstate_list': [[13, 1, 6]]
            }
        },

        # number of networks and data rates remain the same, but number of devices changes
        'change_in_number_of_devices': {
            0: {
                'data_rate': [4, 7, 22],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1))]
            },
            1.0 / 2: {
                'data_rate': [4, 7, 22],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE // 2 + 1)), list(range(1, NUM_MOBILE_DEVICE // 2 + 1)), list(range(1, NUM_MOBILE_DEVICE // 2 + 1))]
            }
        },

        # mobile users move around, devices have access to different sets of network which changes over time
        'mobility_setup1': {
            0: {
                'data_rate': [4, 7, 22],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1,NUM_MOBILE_DEVICE//2 + 1)),
                                 list(range(NUM_MOBILE_DEVICE//2 + 1, NUM_MOBILE_DEVICE + 1))],
                'NEstate_list': [[1, 2, 3]]
            },
            1.0 / 2: {
                'data_rate': [4, 7, 22],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), [1], list(range(2, NUM_MOBILE_DEVICE + 1))],
                'NEstate_list': [[0, 1, 5]]
            }
        },

        'mobility_setup2': {
            0: {
                'data_rate': [16, 14, 22, 7, 4],
                'device_list': [list(range(1, 21)), list(range(1, 11)), list(range(1, 16)), list(range(11, 21)), list(range(11, 21))],
                'NEstate_list': [[5, 5, 7, 2, 1]]
            },
            1.0 / 3: {
                'data_rate': [16, 14, 22, 7, 4],
                'device_list': [list(range(1, 21)), [9, 10], list(range(1, 16)), list(range(11, 21)) + list(range(1, 9)), list(range(11, 21)) + list(range(1, 9))],
                'NEstate_list': [[6, 2, 9, 2, 1]]
            },
            2.0 / 3: {
                'data_rate': [16, 14, 22, 7, 4],
                'device_list': [list(range(1, 21)), [9, 10], [9, 10] + list(range(11, 16)), list(range(11, 21)) + list(range(1, 9)), list(range(11, 21)) + list(range(1, 9))],
                'NEstate_list': [[8, 2, 5, 3, 2]]
            }
        },

        # 20 mobile users staying in a hostel; 15 work in the same office and travel together to work, in a bus that picks them from the hostel; 5 stay at home
        'mobility_setup3': {
            0: { # at home - 13 hrs
                'data_rate': [16, 7, 44, 40, 14, 22, 7, 36, 18],
                'device_list': [list(range(1, 21)), list(range(1, 21)), list(range(1, 11)), list(), list(), list(), list(), list(), list()],
                'NEstate_list': [[7, 3, 10, 0, 0, 0, 0, 0, 0]]
            },
            13/24: { # travelling to work - 1 hr
                'data_rate': [16, 7, 44, 40, 14, 22, 7, 36, 18],
                'device_list': [list(range(1,6)), list(range(1,6)), list(range(1,6)), list(range(6, 21)), list(range(6, 21)), list(), list(), list(), list()],
                'NEstate_list': [[1, 0, 4, 11, 4, 0, 0, 0, 0]]
            },
            14/24: { # in office - 3 hrs
                'data_rate': [16, 7, 44, 40, 14, 22, 7, 36, 18],
                'device_list': [list(range(1,6)), list(range(1,6)), list(range(1,6)), list(), list(), list(range(6, 21)), list(range(6, 21)), list(range(6, 21)), list()],
                'NEstate_list': [[1, 0, 4, 0, 0, 5, 1, 9, 0]]
            },
            17/24: { # lunch time - 1 hr
                'data_rate': [16, 7, 44, 40, 14, 22, 7, 36, 18],
                'device_list': [list(range(1,6)), list(range(1,6)), list(range(1,6)), list(), list(), list(range(6, 11)), list(range(6, 11)), list(range(6, 21)), list(range(11, 21))],
                'NEstate_list': [[1, 0, 4, 0, 0, 4, 1, 7, 3]]
            },
            18/24: { # in office - 5 hrs
                'data_rate': [16, 7, 44, 40, 14, 22, 7, 36, 18],
                'device_list': [list(range(1,6)), list(range(1,6)), list(range(1,6)), list(), list(), list(range(6, 21)), list(range(6, 21)), list(range(6, 21)), list()],
                'NEstate_list': [[1, 0, 4, 0, 0, 5, 1, 9, 0]]
            },
            23/24: { # travelling home - 1 hr
                'data_rate': [16, 7, 44, 40, 14, 22, 7, 36, 18],
                'device_list': [list(range(1,6)), list(range(1,6)), list(range(1,6)), list(range(6, 21)), list(range(6, 21)), list(), list(), list(), list()],
                'NEstate_list': [[1, 0, 4, 11, 4, 0, 0, 0, 0]]
            }
        },

        'continuous': {
            0: {
                'data_rate': [],
                'device_list': [list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1)), list(range(1, NUM_MOBILE_DEVICE + 1))],
                'NEstate_list': []
            }
        }

        } # end PROBLEM_INSTANCES


    ''' definition of period options '''
    PERIOD_OPTIONS = {
        1: [1],                                             # EXP3
        2: [NUM_REPEATS],                                   # EXP3, but reset every day
        3: list(range(1, 16)),                              # 1 - 15
        4: list(range(1, 40)),                              # 1 - 39
        5: [1, 2, 3, 5, 7, 11 ,13],                         # primes below 15
        6: [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37], # primes below 40
        7: [1, 2, 4, 8, 16],                                # powers of 2 up to 16
        8: [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],   # powers of 2 up to 1024
        9: list(range(100)),                                # all numbers up to 100
        10: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97],# primes below 100
        11: [53, 59, 61, 67, 71, 73, 79, 83, 89, 97],       # large primes only
        12: [24],
        13: list(range(1,25))
    } # end PERIOD_OPTIONS
    # end initialize


def mapKeyToTimeSlot(key):
    '''
    description: maps a key (that represents time of a change in the environment) from the problem instance definition to an actual time slot
    args:        a key in a problem instance definition
    return:      a time slot
    '''
    global NUM_TIME_SLOT, NUM_REPEATS

    return key*(NUM_TIME_SLOT/NUM_REPEATS) + 1
    # end mapKeyToTimeSlot

def mapTimeSlotToKey(timeSlot):
    '''
    description: maps an actual time slot to a key (that represents time of a change in the environment) in the problem instance definition
    args:        a time slot
    return:      a key in a problem instance definition
    '''
    global NUM_TIME_SLOT, NUM_REPEATS

    return (timeSlot - 1)/(NUM_TIME_SLOT/NUM_REPEATS)
    # end mapTimeSlotToKey

def findRelevantKey(problem_instance, currentTimeSlot):
    '''
    description: identify the key in the problem instance that defines the current state of the environment
    args:        dictionary storing definitions of problem instances, the problem instance being considered, the current time slot, total number of time slots in the run
    return:      key in problem instance that defines the current state of the environment
    '''
    global PROBLEM_INSTANCES, NUM_TIME_SLOT, NUM_REPEATS

    key_list = PROBLEM_INSTANCES[problem_instance].keys()
    timeOfChange = [mapKeyToTimeSlot(x) for x in key_list]
    timeOfChange = sorted(timeOfChange)
    # key_list = sorted(key_list, key=fractions.Fraction, reverse=True)
    timeSlot = timeOfChange[0]; i = 1
    # to cater for repeats
    currentTimeSlot = NUM_TIME_SLOT/NUM_REPEATS if currentTimeSlot % (NUM_TIME_SLOT / NUM_REPEATS) == 0 else currentTimeSlot % (NUM_TIME_SLOT / NUM_REPEATS)
    while len(timeOfChange) > i and currentTimeSlot >= timeOfChange[i]: timeSlot = timeOfChange[i]; i += 1
    return mapTimeSlotToKey(timeSlot)
    # end findRelevantKey

def changeInEnvironment(problem_instance, currentTimeSlot):
    '''
    description: determines if there is a change in the current time slot
    args:        the name of the problem instance being considered, the current time slot
    return:      True or False depending on whether there is a change in the current time slot
    '''
    global PROBLEM_INSTANCES

    currentTimeSlot = NUM_TIME_SLOT / NUM_REPEATS if currentTimeSlot % (NUM_TIME_SLOT / NUM_REPEATS) == 0 else currentTimeSlot % (NUM_TIME_SLOT / NUM_REPEATS)
    # print("#repeat:", NUM_REPEATS, ", currentTimeSlot = ", currentTimeSlot)
    key_list = PROBLEM_INSTANCES[problem_instance].keys()
    timeOfChange = [ceil(mapKeyToTimeSlot(x)) for x in key_list]
    # print("time of change:", timeOfChange)
    if currentTimeSlot in timeOfChange: return True
    return False
    # end changeInEnvironment

def getNetworkDataRate(problem_instance, currentTimeSlot):
    '''
    description: gets the data rate of each network for the current time slot, based on the definition of the problem instance being considered
    args:        the name of the problem instance being considered, the current time slot
    return:      data rates for each network for the current time slot
    '''
    global PROBLEM_INSTANCES

    key = findRelevantKey(problem_instance, currentTimeSlot)
    # print("t:", currentTimeSlot, ", key:", key)
    return PROBLEM_INSTANCES[problem_instance][key]['data_rate']
    # end getNetworkDataRate

def getDeviceListPerNetwork(problem_instance, currentTimeSlot):
    '''
    description: gets the list of devices that have access to each network
    args:        the name of the problem instance being considered, the current time slot
    return:      list of devices that have access to each network
    '''
    global PROBLEM_INSTANCES

    key = findRelevantKey(problem_instance, currentTimeSlot)
    return PROBLEM_INSTANCES[problem_instance][key]['device_list']
    # end getDeviceListPerNetwork

def getNashEquilibriumState(problem_instance, currentTimeSlot):
    '''
    description: gets the list Nash equilibrium state(s) for the current time slot, based on the definition of the problem instance being considered
    args:        the name of the problem instance being considered, the current time slot
    return:      the list Nash equilibrium state(s) for the current time slot
    '''
    global PROBLEM_INSTANCES

    key = findRelevantKey(problem_instance, currentTimeSlot)
    return PROBLEM_INSTANCES[problem_instance][key]['NEstate_list']
    # end getNashEquilibriumState

def isActive(problem_instance, currentTimeSlot, deviceID):
    '''
    description: determines whether the device is active in the current time slot; i.e., selecting and associating with a network
    args:        the name of the problem instance being considered, the current time slot, ID of a mobile device
    return:      True or False depending on whether the device is active in the current time slot
    '''
    global PROBLEM_INSTANCES

    key = findRelevantKey(problem_instance, currentTimeSlot)
    deviceList = PROBLEM_INSTANCES[problem_instance][key]['device_list']
    for list in deviceList:
        if deviceID in list: return True
    return False
    # end isActive

def getUnavailableNetwork(problem_instance, currentTimeSlot, deviceID):
    '''
    description: returns the list of networks currently unavailable to a device
    args:        name of the problem instance being considered, the current time slot, ID of a mobile device
    return:      list of networks currently not available (their IDs)
    '''
    global PROBLEM_INSTANCES

    unavailableNetworkList = []
    key = findRelevantKey(problem_instance, currentTimeSlot)
    deviceList = PROBLEM_INSTANCES[problem_instance][key]['device_list']
    for index, list in enumerate(deviceList):
        if deviceID not in list: unavailableNetworkList.append(index + 1)
    return unavailableNetworkList

def isNetworkAccessible(problem_instance, currentTimeSlot, networkID, deviceID):
    '''
    description: determines whether a network is available to a device
    args:        the name of the problem instance being considered, the current time slot, ID of a mobile device
    return:      True or False depending on whether the network is available to the device
    '''
    global PROBLEM_INSTANCES

    key = findRelevantKey(problem_instance, currentTimeSlot)
    deviceList = PROBLEM_INSTANCES[problem_instance][key]['device_list']
    # print("t:", currentTimeSlot, ", key:", key, ", deviceID:", deviceID, ", deviceList:", deviceList)
    if deviceID in deviceList[networkID - 1]: return True
    return False
    # end isNetworkAccessible

def getTimesOfChange(problem_instance, repetitionIndex):
    '''
    description: returns the time slots at which there is a change in the environment
    args:        name of problem instance being considered, the current repetition considered
    return:      the time slots at which there are changes
    '''
    global PROBLEM_INSTANCES, NUM_REPEATS, NUM_TIME_SLOT

    repetitionStartTime = (NUM_TIME_SLOT//NUM_REPEATS) * (repetitionIndex - 1) + 1  # start time slot of current repetition
    key_list = PROBLEM_INSTANCES[problem_instance].keys()
    # print("keys:", key_list, "numTimeSlot", NUM_TIME_SLOT)
    return [repetitionStartTime + int((NUM_TIME_SLOT // NUM_REPEATS) * key) for key in key_list]
    # end getTimesOfChange

''' for testing '''
def main():
    problem_instance = 'mobility_setup2'
    global NUM_MOBILE_DEVICE, NUM_TIME_SLOT, NUM_REPEATS, PROBLEM_INSTANCES, PERIOD_OPTIONS

    global_setting.constants.update({'num_mobile_device':6})
    global_setting.constants.update({'num_time_slot':10})
    global_setting.constants.update({'num_repeats': 2})

    initialize()

    # print(PROBLEM_INSTANCES[problem_instance])
    networkID = 2
    for t in range(1, NUM_TIME_SLOT + 1):
        # key = findRelevantKey(problem_instance, t)
        # print(t, " data rates", PROBLEM_INSTANCES[problem_instance][key]['data_rate'])
        # print(t, " devices list", PROBLEM_INSTANCES[problem_instance][key]['device_list'])
        print("change @ t = ", t, "?", changeInEnvironment(problem_instance, t))
        print(getNetworkDataRate(problem_instance, t))
        # for deviceID in list(range(1, NUM_MOBILE_DEVICE + 1)):
        #     if isActive(problem_instance, t, deviceID): print(deviceID, " - active")
        #     else: print(deviceID, " - NOT active")
        #
        #     if isNetworkAccessible(problem_instance, t, networkID, deviceID): print("Network ", networkID, " is available to device ", deviceID)
        #     else: print("Network ", networkID, " is NOT available to device ", deviceID)

if __name__ == '__main__': main()