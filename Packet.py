import hashlib
from random import *
class Packet:
    def __init__(self, length, seqn,data, plp, pcorruption, checksum):
        self.length = length
        self.seqn = seqn
        self.data = data
        self.plp = RandomGenerator(plp)
        self.pcorruption = RandomGenerator(pcorruption)
        self.checksum = checksum

    def isACKType(self):
        """Returns whether the packet is a control packet or data packet,
        Control packets are ACKS as we use ACK only protocol"""
        return self.length == 8 #Acks are only 8 bytes in length

    def isCorrupt(self):
        return self.pcorruption.random()

    def isLost(self):
        return self.plp.random()

    def __str__(self):
        return 'Packet with seqn:{}'.format(self.seqn)
    def __repr__(self):
        return self.__str__()

    def update_checksum(self, chunk):
        self.checksum.update(chunk)

    def return_checksum(self):
        return self.checksum.hexdigest()

class RandomGenerator:

    def __init__(self, probability = 0):
        self.p = probability

    def random(self):
        """Returns true or false depending on the probability that initialized the object with"
        """
        return random() < self.p
