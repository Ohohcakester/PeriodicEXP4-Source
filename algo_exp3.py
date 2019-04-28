import numpy as np
from math import exp

def computeGamma(index):
    '''
    description: computes the value of gamma based on the current time slot or block index, without the need to know the horizon
    args:        self, current time slot t
    returns:     value of gamma for the current time slot
    '''
    return index ** (-1 / 3)
    # end computeGamma


class Exp3Algo(object):
    def __init__(self, K, T):
        self.K = K
        self.T = T
        self.t = 1
        self.gamma = computeGamma(self.t)
        self.probabilities = None
        self.choice = None

        self.arms = list(range(K))

        # initialize
        self.weights = [1.0]*K

    def get_next_arm(self):
        self.probabilities = list((1-self.gamma)*(weight/sum(self.weights)) + (self.gamma/self.K)
                            for weight in self.weights)
        self.choice = np.random.choice(self.arms, p=self.probabilities)

        return self.choice

    def give_reward(self, reward):
        #reward = getFeedback()
        estimatedReward = reward / self.probabilities[self.choice]

        self.t = self.t+1
        self.gamma = computeGamma(self.t)

        # update weight
        weights = self.weights
        try: weights[self.choice] *= exp((self.gamma * estimatedReward) / len(weights))
        except OverflowError: weights[self.choice] = 1
        self.weights = [w/max(weights) if w/max(weights) > 0 else (float_info.min * float_info.epsilon)
                    for w in weights]

    def get_log_headers(self):
        return ['weight%d' % i for i in range(1,self.K+1)] + \
               ['probability%d' % i for i in range(1,self.K+1)]
        
    def get_timestep_log(self):
        return self.weights + self.probabilities


