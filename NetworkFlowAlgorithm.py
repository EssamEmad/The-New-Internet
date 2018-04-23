from abc import ABC, abstractmethod

class Window:

    def __init__(self, size, max_sqn):
        self.base_sqn = 0
        self.max_sqn = max_sqn
        self.size = size
        self.buffer = [None] * size

    def slide_if_needed(self):
        """Returns the pckts that should be delivered"""
        for i in range(len(self.buffer)):
            if self.buffer[i] != None:
                pkts = self.buffer.remove(0:i)
                self.buffer.extend([None] * i)
                self.base_sqn += i
                self.base_sqn %= self.max_sqn
                return pkts

    def __len__(self):
        return self.size


class ReceiverWindowManager (ABC):
"""Abstract class that should not be used alone"""
    @abstractmethod
    def __init__(self,size):
        self.window = Window(size)
    @abstractmethod
    def receive_pkt(self,pkt):
        """Returns the pkts that should be delivered if there are any"""
        pass
    @abstractmethod
    def is_pkt_expected(self,pkt):
        pass

class SelectiveRepeatReceiver(ReceiverWindowManager):

    def is_pkt_expected(self, pkt):
        """Returns whether this packet is in the expected window range"""
        pass
        return pkt.seqn >= self.window.base_sqn and pkt.seqn < (self.window.base_sqn + self.window.size) % self.window.max_sqn
    def receive_pkt(self,pkt):
        """Returns the pkts that should be delivered if there are any"""
        # if pkt.seqn < self.window.base_sqn:
        #     return True
        # elif pkt.seqn > (self.window.base_sqn + self.size) % self.max_sqn:
        #     return False # This pkt is beyond the window size and should be ignored
        # else:
        #     index = pkt.seqn - self.base_sqn
        #     self.buffer[index] = pkt
        #     self.slide_if_needed()
        #     return True
        # if self.is_pkt_expected(pkt): #Packet expected?
        index = abs(self.window.base_sqn - pkt.seqn)
        if index < len(self.window):
            if self.window.buffer[index] != None:
                return False
            else:
                self.window.buffer[index] = pkt
                return True
        return self.window.slide_if_needed()

class GoBkNReceiver (ReceiverWindowManager):

    def __init__(self,max_sqn):
        self.expected_sqn = 0
        self.max_sqn = max_sqn

    def receive_pkt(self,pkt):
        if pkt.seqn == self.expected_sqn:
            self.expected_sqn += 1
            self.expected_sqn %= max_sqn
            return [pkt]
        else:
            return None

class StopWaitReceiver ( GoBkNReceiver):
    def __init__(self):
        super.init(1)
