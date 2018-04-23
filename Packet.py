from random import *
class Packet:
    def __init__(self, length, seqn,data, plp, pcorruption):
        self.length = length
        self.seqn = seqn
        self.data = data
        self.plp = RandomGenerator(plp)
        self.pcorruption = RandomGenerator(pcorruption)

    def isACKType(self):
        """Returns whether the packet is a control packet or data packet,
        Control packets are ACKS as we use ACK only protocol"""
        return self.length == 8 #Acks are only 8 bytes in length

    def isCorrupt(self):
        return self.pcorruption.random()

    def isLost(self):
        return self.plp.random()



class RandomGenerator:

    def __init__(self, probability = 0):
        self.p = probability

    def random():
        """Returns true or false depending on the probability that initialized the object with"
        """
        return random.random() < probability
