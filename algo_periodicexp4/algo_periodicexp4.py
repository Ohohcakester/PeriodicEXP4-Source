import os
from ctypes import cdll, c_int, c_double
lib = cdll.LoadLibrary(os.path.dirname(__file__) + '/libperiodicexp4.so')
lib.DataLog_next.restype = c_double
import math

class PeriodicExp4(object):
    # each function is a (lambda function, label_count) pair
    # first timestep t = 0.
    # T: number of timesteps
    # K: number of arms
    # functions: 
    # seed: random seed for determinstic output.
    # gamma: learning rate, between 0 and 1
    def __init__(self, T, K, functions, seed=0, gamma=None):
        self.F = len(functions)
        self.K = K
        self.t = 0
        self.functions = tuple(f[0] for f in functions)

        label_counts = (c_int*self.F)(*(f[1] for f in functions))
        #random_seeds = (c_int*self.F)(*random_seeds)
        if gamma == None:
            self.obj = lib.PeriodicExp4_new(T,K,self.F,label_counts, seed)
        elif gamma < 0:
            raise Exception('gamma cannot be negative.')
        else:
            self.obj = lib.PeriodicExp4_new_g(T,K,self.F,label_counts, seed, c_double(gamma))
        
    def get_next_arm(self):
        current_labels = (c_int*self.F)(*(f(self.t) for f in self.functions))
        return lib.PeriodicExp4_getNextArm(self.obj, current_labels)

    def give_reward(self, reward, gamma=-1):
        lib.PeriodicExp4_giveReward(self.obj, c_double(reward), c_double(gamma))
        self.t += 1

    # This function only works if compiled with #define ENABLE_LOGGING
    def extract_log(self):
        datalog = lib.PeriodicExp4_getLog(self.obj)
        size = lib.DataLog_size(datalog)
        cols = lib.DataLog_cols(datalog)
        lib.DataLog_reset(datalog)
        return cols, [lib.DataLog_next(datalog) for i in range(size)]

    def get_log_headers(self):
        return ['w_partitionF%d' % f for f in range(1,self.F+1)] +\
               ['w_arm%d' % i for i in range(1,self.K+1)] +\
               ['probability%d' % i for i in range(1,self.K+1)]
        #['temp_mwF%d' % f for f in range(1,self.F+1)] +\
        #['labelF%d' % f for f in range(1,self.F+1)] +\
        #['misc1%d' % i for i in range(1,self.K+1)] +\
        #['misc2%d' % i for i in range(1,self.K+1)] +\
        
    def get_timestep_log(self):
        datalog = lib.PeriodicExp4_getCurrentTimestepData(self.obj)
        size = lib.DataLog_size(datalog)
        lib.DataLog_reset(datalog)
        return [lib.DataLog_next(datalog) for i in range(size)]

def generate_random_seed():
    import random
    return random.randrange(100000)




"""
### MAKING FUNCTIONS - START ###
"""

def make_partition_cycles(T, periods):
    make_cycle_function = lambda T,P : (lambda t : P*t//(T), P)
    return tuple(make_cycle_function(T,i) for i in periods)


def make_repeating_partition_cycles(T, repeats, periods):
    def make_cycle_function(T,P):
        def f(t):
            i = (t*repeats)//T
            start = (i*T + repeats-1)//repeats
            length = ((i+1)*T + repeats-1)//repeats - start
            return (t-start)*P//length
        return (f, P)
    #make_cycle_function = lambda T,P : (lambda t : P*t//(T), P)
    return tuple(make_cycle_function(T,i) for i in periods)


"""
###  MAKING FUNCTIONS - END  ###
"""





"""
### ALGORITHM CONSTRUCTORS - START ###
"""

# period_list: list of integers representing the periods. 
# gamma = learning rate in [0,1]. Set to None or leave it undefined to use the paper-defined learning rate for exp4.
# set period_list = [1] for normal Exp3.
#  _____________________________
# |_____________________________| Period 1
#  ______________ ______________
# |______________|______________| Period 2
#  _________ _________ _________
# |_________|_________|_________| Period 3
#
def algo_partition_cycles(T, K, period_list, seed=None, gamma=None):
    if seed == None: seed = generate_random_seed()
    functions = make_partition_cycles(T, period_list)
    return PeriodicExp4(T, K, functions, seed=seed, gamma=gamma)

"""
###  ALGORITHM CONSTRUCTORS - END  ###
"""








def test_algorithm():
    T = 10000
    K = 10

    #alg = algo_partition_cycles(T, K, [3])
    #alg = algo_partition_cycles(T, K, [3] + list(range(60,90)))
    alg = algo_partition_cycles(T, K, list(range(1,30)))


    total_reward = 0
    picked_arms = []
    rewards = []
    GOOD_REWARD = 0.8
    for t in range(T):
        if t%1000 == 0: print('t=%d' % t)
        i = alg.get_next_arm()
        picked_arms.append(i)
        reward = (GOOD_REWARD if i==2 else 0)

        if False:
            if t >= T//2: reward = (GOOD_REWARD if i==4 else 0)

        if False:
            if t >= T//3: reward = (GOOD_REWARD if i==3 else 0)
            if t >= (2*T)//3: reward = (GOOD_REWARD if i==1 else 0)

        if False:
            if t >= T//4: reward = (GOOD_REWARD if i==2 else 0)
            if t >= (2*T)//4: reward = (GOOD_REWARD if i==5 else 0)
            if t >= (3*T)//4: reward = (GOOD_REWARD if i==1 else 0)

        if False:
            if t >= (T)//7: reward = (GOOD_REWARD if i==7 else 0)
            if t >= (2*T)//7: reward = (GOOD_REWARD if i==5 else 0)
            if t >= (3*T)//7: reward = (GOOD_REWARD if i==3 else 0)
            if t >= (4*T)//7: reward = (GOOD_REWARD if i==0 else 0)
            if t >= (5*T)//7: reward = (GOOD_REWARD if i==8 else 0)
            if t >= (6*T)//7: reward = (GOOD_REWARD if i==6 else 0)

        if False:
            if t >= (T)//6: reward = (GOOD_REWARD if i==7 else 0)
            if t >= (2*T)//6: reward = (GOOD_REWARD if i==5 else 0)
            if t >= (3*T)//6: reward = (GOOD_REWARD if i==3 else 0)
            if t >= (4*T)//6: reward = (GOOD_REWARD if i==0 else 0)
            if t >= (5*T)//6: reward = (GOOD_REWARD if i==8 else 0)

        if True:
            for z in range(1,27):
                if t >= (z*T)//27: reward = (GOOD_REWARD if i==(z%K) else 0)

        alg.give_reward(reward)
        rewards.append(reward)
        total_reward += reward

    print('Reward: %g' % (total_reward/GOOD_REWARD))


    LOGGING = False #Only turn this on if compiled with #define ENABLE_LOGGING
    if LOGGING:
        #print(''.join(str(i) for i in picked_arms))
        cols, weightlog = alg.extract_log()
        #logoutput = ' '.join(str(x) for x in weightlog)
        weightlog = [int(math.log(x)) for x in weightlog]
        lines = [weightlog[i*cols:(i+1)*cols] for i in range(0,T,10)]
        logoutput = '\n'.join(' '.join('%3d'%x for x in line) for line in lines)

        f = open('weightlog.txt', 'w+')
        f.write(logoutput)
        f.close()

        SP = 27
        interval = T//SP
        lines = [rewards[i*interval:(i+1)*interval] for i in range(SP)]
        log2output = '\n'.join(''.join('%d'%round(x/GOOD_REWARD) for x in line) for line in lines)

        f = open('weightlog2.txt', 'w+')
        f.write(log2output)
        f.close()


if __name__ == '__main__':
    test_algorithm()

    quit()

    repeats = 9
    def make_cycle_function(T,P):
        def f(t):
            i = (t*repeats)//T
            start = (i*T + repeats-1)//repeats
            length = ((i+1)*T + repeats-1)//repeats - start
            return (t-start)*P//length
        return (f, P)

    #make_cycle_function = lambda T,P : (lambda t : P*t//(T), P)

    f,_ = make_cycle_function(100, 9)


    last = -1
    sb = []
    for i in range(100):
        r = f(i)
        if r != last:
            print(''.join(str(x) for x in sb))
            sb = []
        sb.append(r)
        last = r
    print(''.join(str(x) for x in sb))
    sb = []

