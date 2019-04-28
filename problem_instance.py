"""
Manages the variation of network bitrates and other network properties over time.
A problem instance maker should return (run, maxGain, numNetworks)
"""
import math, random

def run_instance(env, networkList, instance):
    for timeoutDuration in instance(networkList):
        yield env.timeout(timeoutDuration)

def make_datarate_instance(events):
    seq = sorted(events.items(), key=lambda x:x[0])
    assert seq[0][0] == 0, 'first event must start from 0'
    maxGain = max(max(pair[1]) for pair in seq)
    numNetworks = len(seq[0][1])

    def run(networkList):
        last_time = 0
        yield (1)
        for t, dataRates in seq:
            dt = t - last_time
            last_time = t
            yield (3*dt)
            for dataRate, network in zip(dataRates, networkList):
                network.dataRate = dataRate
    return run, maxGain, numNetworks

EPSILON=0.0000001
def make_fractional_datarate_instance(T, events):
    return make_datarate_instance({int(T*p+EPSILON):v for p,v in events.items()})


def sine(T, relativePeriod, phaseShift, amplitude):
    # relativePeriod = 1 --> period T
    # relativePeriod = 2 --> period 2T
    freq = 2*math.pi / T / relativePeriod
    shift = phaseShift*2*math.pi
    return lambda t: math.sin(t*freq-shift)*amplitude

def make_random_continous_function(T, seed, scale, meanAmplitude):
    localRandom = random.Random(seed)

    numberOfFunctions = 20
    functions = []
    amp = meanAmplitude/numberOfFunctions
    for i in range(numberOfFunctions):
        amplitude = localRandom.uniform(amp/3, amp*5/3)
        shift = localRandom.uniform(0,1)
        #relativePeriod = 2**localRandom.uniform(-3,2)
        relativePeriod = (2**localRandom.uniform(-3,2))*scale
        functions.append(sine(T, relativePeriod, shift, amplitude))

    return lambda t: sum(f(t) for f in functions)


def make_continuous_datarate_instance(T, numNetworks, seed, totalBandwidth, scale, offsetPercent):
    localRandom = random.Random(seed)
    bandwidthFunctions = [make_random_continous_function(T, localRandom.randrange(2147483647), scale, 10) for i in range(numNetworks)]
    
    def run(networkList):
        yield (1)
        for t in range(1,T+1):
            dataRates = [f(t) for f in bandwidthFunctions]
            dataRates = [x*x+(offsetPercent*100) for x in dataRates] # square everything
            totalRate = sum(dataRates)
            for dataRate, network in zip(dataRates, networkList):
                network.dataRate = dataRate*totalBandwidth/totalRate
            yield (3)
    return run, totalBandwidth, numNetworks

def repeat_instance(T, repeats, instanceFun):
    maxGain = 0
    instances = []
    for i in range(repeats):
        dT = T*(i+1)//repeats - T*i//repeats
        instance, localMaxGain, numNetworks = instanceFun(dT)
        instances.append((dT, instance))
        maxGain = max(maxGain, localMaxGain)

    def run(networkList):
        yield (1)
        for dT, instance in instances:
            runInstance = instance(networkList)
            next(runInstance) # remove the yield (1) at the start
            stepsLeft = dT
            for timeout in runInstance:
                stepsLeft -= timeout//3 # timeout is an integer
                yield timeout
            yield (3*stepsLeft)

    return run, maxGain, numNetworks

''' __________ problem instance definitions __________ '''
'''       the keys are the problem instance names      '''

PROBLEM_INSTANCES = {
    'instance_1': 
    lambda T: make_fractional_datarate_instance(T, {
        0: (4,7,22),
    }),

    'instance_2': 
    lambda T: make_fractional_datarate_instance(T, {
        0:   (20,5,15,140,20),
        1/5: (10,5,15,10,160),
        2/5: (75,15,20,77,13),
        3/5: (12,133,15,17,23),
        4/5: (17,82,81,10,10),
    }),

    'instance_2b': 
    lambda T: make_fractional_datarate_instance(T, {
        0:     (20,5,15,140,20),
        1/15:  (10,5,15,10,160),
        2/15:  (75,15,20,77,13),
        3/15:  (12,133,15,17,23),
        4/15:  (17,82,81,10,10),
        5/15:  (20,5,15,140,20),
        6/15:  (10,5,15,10,160),
        7/15:  (75,15,20,77,13),
        8/15:  (12,133,15,17,23),
        9/15:  (17,82,81,10,10),
        10/15: (20,5,15,140,20),
        11/15: (10,5,15,10,160),
        12/15: (75,15,20,77,13),
        13/15: (12,133,15,17,23),
        14/15: (17,82,81,10,10),
    }),

    'instance_3': 
    lambda T: make_fractional_datarate_instance(T, {
        0:   (0,0,0,200,0),
        1/5: (0,0,200,0,0),
        2/5: (0,0,0,0,200),
        3/5: (0,200,0,0,0),
        4/5: (200,0,0,0,0),
    }),

    'instance_4': 
    lambda T: make_fractional_datarate_instance(T, {
        0:   (13,2,60,19,6),
        1/7: (72,14,4,5,5),
        2/7: (5,1,36,46,12),
        3/7: (0,12,1,56,31),
        4/7: (43,5,6,6,40),
        5/7: (1,25,38,36,0),
        6/7: (40,13,10,21,16),
    }),

    'instance_testing': 
    lambda T: make_fractional_datarate_instance(T, {
        0:   (0,0,100,100,0),
        1/5: (50,50,0,50,50),
        2/5: (0,0,0,0,200),
        3/5: (100,100,0,0,0),
        4/5: (40,40,40,40,40),
    }),

    'instance_testing2': 
    lambda T: make_fractional_datarate_instance(T, {
        0: (40,20,10,160,20),
    }),

    'instance_cont1': 
    lambda T: make_continuous_datarate_instance(T,
        numNetworks=3, seed=3, scale=1, totalBandwidth=65,
        offsetPercent=0),

    'instance_cont2': 
    lambda T: make_continuous_datarate_instance(T,
        numNetworks=3, seed=531, scale=3, totalBandwidth=65,
        offsetPercent=0),

    'instance_cont3': 
    lambda T: make_continuous_datarate_instance(T,
        numNetworks=3, seed=15, scale=3, totalBandwidth=65,
        offsetPercent=0),

    'instance_cont4': 
    lambda T: make_continuous_datarate_instance(T,
        numNetworks=3, seed=389, scale=2, totalBandwidth=65,
        offsetPercent=0.3),

    'instance_cont5': 
    lambda T: make_continuous_datarate_instance(T,
        numNetworks=3, seed=821, scale=3, totalBandwidth=65,
        offsetPercent=0.6),

    'instance_cont6': 
    lambda T: make_continuous_datarate_instance(T,
        numNetworks=5, seed=411, scale=2.5, totalBandwidth=100,
        offsetPercent=0.03),
}

''' __________________________________________________ '''


def test_continuous_datarate_instance():
    seed = random.randrange(2147483647)
    #seed = 2

    T = 1440
    numRepeat = 1
    import matplotlib.pyplot as plt
    class NetworkStub(object):
        def __init__(self):
            self.dataRate = 0

    numNetworks = 3
    #instance, _1, numNetworks = make_continuous_datarate_instance(T, numNetworks, seed, 1, 100)
    instance, _1, numNetworks = repeat_instance(T, numRepeat, PROBLEM_INSTANCES['instance_cont3'])
    print("instance:", instance)
    print("_1", _1)
    print("numNetworks:", numNetworks)

    #instance, _1, numNetworks = PROBLEM_INSTANCES['instance_testing'](T)

    networkList = [NetworkStub() for i in range(numNetworks)]

    results = []
    iterInstance = iter(instance(networkList))
    next(iterInstance) # pop the timeout(1)
    for e in iterInstance:
        steps = e//3
        for i in range(steps):
            results.append([network.dataRate for network in networkList])
    for i in range(T-len(results)):
        results.append([network.dataRate for network in networkList])

    results = [list(v) for v in zip(*results)] #transpose

    print("results:", results)
    x = list(range(T))

    for bandwidth in results:
        print(bandwidth)
        plt.plot(x, bandwidth)
    plt.show()

# def test_continuous_functions():
#     T = 1000
#     import matplotlib.pyplot as plt
#     x = list(range(T))
#     for i in range(2):
#         f = make_random_continous_function(T, random.randrange(10000), 1, 10)
#         # plt.plot(x, [f(t) for t in x])
#     # plt.show()

# 0 = start.
if __name__ == '__main__':
    test_continuous_datarate_instance()
    #test_continuous_functions()


    quit()
    # test code
    make_datarate_instance({
        0: (10,20,24),
        13: (42,20,19),
        17: (15,4,24),
    })

    make_fractional_datarate_instance(1200, {
        0: (10,20,24),
        1/3: (42,20,19),
        2/3: (15,4,24),
    })