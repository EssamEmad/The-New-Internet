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

    def checksum1(self, data_chunks, sum=0):
        data_chunks = data_chunks.decode()
        # make 16 bit words out of every two adjacent 8 bit words in the packet
        # and add them up
        for i in range(0, len(data_chunks), 2):
            if i + 1 >= len(data_chunks):
                sum += ord(data_chunks[i]) & 0xFF
            else:
                w = ((ord(data_chunks[i]) << 8) & 0xFF00) + (ord(data_chunks[i + 1]) & 0xFF)
                sum += w
        # take only 16 bits out of the 32 bit sum and add up the carries
        while (sum >> 16) > 0:
            sum = (sum & 0xFFFF) + (sum >> 16)
        # one's complement the result
        sum = ~sum
        return sum & 0xFFFF

    def is_accepted(self, data_chunks, sum=0):
        data_chunks = data_chunks.decode()
        # make 16 bit words out of every two adjacent 8 bit words in the packet
        # and add them up
        for i in range(0, len(data_chunks), 2):
            if i + 1 >= len(data_chunks):
                sum += ord(data_chunks[i]) & 0xFF
            else:
                w = ((ord(data_chunks[i]) << 8) & 0xFF00) + (ord(data_chunks[i + 1]) & 0xFF)
                sum += w
        # take only 16 bits out of the 32 bit sum and add up the carries
        while (sum >> 16) > 0:
            sum = (sum & 0xFFFF) + (sum >> 16)
        sum = sum + ~sum
        return ~sum == 0

class RandomGenerator:

    def __init__(self, probability = 0):
        self.p = probability

    def random(self):
        """Returns true or false depending on the probability that initialized the object with"
        """
        return random() < self.p
