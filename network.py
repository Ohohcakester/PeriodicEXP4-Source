'''
@description:   Defines a class that models a wireless network
'''
import problem_instance_v2
''' _______________________________________________________________________ Network class definition ______________________________________________________________________ '''
class Network(object):
    ''' class to represent network objects '''
    numNetwork = 0  # keeps track of number of networks to automatically assign an ID to network upon creation

    def __init__(self, dataRate):
        Network.numNetwork = Network.numNetwork + 1     # increment number of network objects created
        self.networkID = Network.numNetwork             # ID of network
        self.dataRate = dataRate                        # date rate of network (in Mbps)
        self.associatedDevice = set()                   # set of associated devices
        # end __init__

    # ''' ################################################################################################################################################################### '''
    # def associateDevice(self, problem_instance, currentTimeSlot, deviceID):
    #     '''
    #     description: increments the number of devices connected to the network
    #     arg:         self
    #     returns:     None
    #     '''
    #     if problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, self.networkID, deviceID):
    #         self.associatedDevice.add(deviceID)
    #     # end associateDevice

    ''' ################################################################################################################################################################### '''
    def associateDevice(self, deviceID):
        '''
        description: increments the number of devices connected to the network
        arg:         self
        returns:     None
        '''
        self.associatedDevice.add(deviceID)
        # end associateDevice
    ''' ################################################################################################################################################################### '''
    def disassociateDevice(self, deviceID):
        '''
        description: decrements the number of devices connected to the network
        arg:         self
        returns:     None
        '''
        # if deviceID in self.associatedDevice: self.associatedDevice.remove(deviceID) # will not be in list in case network was not available when chosen...
        self.associatedDevice.remove(deviceID)
        # end disassociateDevice

    ''' ################################################################################################################################################################### '''
    def getDataRate(self):
        '''
        description: returns the data rate of the network
        args:        self
        return:      data rate of the network
        '''
        return self.dataRate

    ''' ################################################################################################################################################################### '''
    def setDataRate(self, rate):
        '''
        description: updates the data rate of the network
        args:        self, the data rate
        return:      None
        '''
        self.dataRate = rate
        # end setDataRate

    ''' ################################################################################################################################################################### '''
    def getPerDeviceBitRate(self, problem_instance, currentTimeSlot, deviceID):
        '''
        description: computes the bit rate observed by one device in Mbps, assuming network bandwidth is equally shared among its clients
        args:        self
        returns:     bit rate observed by a mobile device of the network (in Mbps)
        '''
        relevantAssociatedDevice = Network.getRelevantAssociatedDevice(self, problem_instance, currentTimeSlot)
        if problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, self.networkID, deviceID):
            # return self.dataRate / len(self.associatedDevice) # self.numDevice
            return self.dataRate/len(relevantAssociatedDevice)
        return 0

    ''' ################################################################################################################################################################### '''
    def getPerDeviceDownload(self, problem_instance, currentTimeSlot, deviceID, timeSlotDuration, delay=0):
        '''
        description: computes the total download of a mobile device during a time slot in Mbits (when switching cost is considered)
        args:        self, delay (the delay incurred while dissociating from the previous network and associating with this one and resuming, e.g., download)
        returns:     total download of a device during one time slot (in Mbits), considering switching cost
        '''
        relevantAssociatedDevice = Network.getRelevantAssociatedDevice(self, problem_instance, currentTimeSlot)
        if problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, self.networkID, deviceID):
            # return (self.dataRate / len(self.associatedDevice)) * (timeSlotDuration - delay)
            return (self.dataRate/len(relevantAssociatedDevice)) * (timeSlotDuration - delay)
        return 0
        # return (self.dataRate / self.numDevice) * (timeSlotDuration - delay)

    ''' ################################################################################################################################################################### '''
    def getNumAssociatedDevice(self):
        '''
        description: returns the number of devices associated to the network
        args:        self
        return:      count of associated device
        '''
        return len(self.associatedDevice)
        # end getNumAssociatedDevice

    ''' ################################################################################################################################################################### '''
    def getAssociatedDevice(self):
        '''
        description: returns the set of devices associated to the network
        args:        self
        return:      set of associated device
        '''
        return self.associatedDevice
        # end getAssociatedDevice

    ''' ################################################################################################################################################################### '''
    def getRelevantAssociatedDevice(self, problem_instance, currentTimeSlot):
        '''
        description: among the devices that chose the network, determine the number of them which actually have access to the network
        args:        self, the problem instance being considered, the current time slot
        return:      list of devices that selected the network which actually have access to it
        '''
        relevantAssociatedDevice = []
        for deviceID in self.associatedDevice:
            if problem_instance_v2.isNetworkAccessible(problem_instance, currentTimeSlot, self.networkID, deviceID):
                relevantAssociatedDevice.append(deviceID)
        return relevantAssociatedDevice
        # end getRelevantAssociatedDevice
# end class Network