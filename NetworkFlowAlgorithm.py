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
            if self.buffer[i] == None:
                pkts = self.buffer[0:i]
                del self.buffer[0:i]
                self.buffer.extend([None] * i)
                self.base_sqn += i
                self.base_sqn %= self.max_sqn
                return pkts

    def __len__(self):
        return self.size


class ReceiverWindowManager (ABC):
#Abstract class that should not be used alone
    def __init__(self,size, max_seqn):
        self.window = Window(size,max_seqn)
    @abstractmethod
    def receive_pkt(self,pkt):
        """Returns the pkts that should be delivered if there are any"""
        pass
    @abstractmethod
    def should_ack_pkt(self,pkt):
        """Returns whether this packet should be acked or not"""
        pass

class SelectiveRepeatReceiver(ReceiverWindowManager):

    def should_ack_pkt(self, pkt):
        base = self.window.base_sqn
        #We are trying to capture 2 cases: a) One of the numbers rotated (58 and 3 for example if the max_seqn is 60 and window size is 10
        #b) 2 numbers didn't rotate
        # return abs(base - pkt.seqn) < self.window.size or (min(pkt.seqn,base) + self.window.max_sqn - max(pkt.seqn,base)) < self.window.size
        return  True #abs(pkt.seqn + self.window.max_sqn - base) % self.window.max_sqn < self.window.size
        # return pkt.seqn >= self.window.base_sqn and pkt.seqn < (self.window.base_sqn + self.window.size) % self.window.max_sqn
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
            if not self.window.buffer[index]:
                self.window.buffer[index] = pkt
        return self.window.slide_if_needed()

class GoBkNReceiver (ReceiverWindowManager):

    def __init__(self,max_sqn):
        self.expected_sqn = 0
        self.max_sqn = max_sqn

    def receive_pkt(self,pkt):
        if pkt.seqn == self.expected_sqn:
            self.expected_sqn += 1
            self.expected_sqn %= self.max_sqn
            return [pkt]
        else:
            return None
    def should_ack_pkt(self,pkt):
        return pkt.seqn == self.expected_sqn

class StopWaitReceiver ( GoBkNReceiver):
    def __init__(self):
        super.init(1)
