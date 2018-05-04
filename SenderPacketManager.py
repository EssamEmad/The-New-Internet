from abc import ABC, abstractmethod
from threading import Timer
from Defaults import *
from Packet import *
class SenderPacketManager (ABC):


    @abstractmethod
    def __init__(self):
        """send_callback is the callback used to actually transmit the pckt over
        the internet"""
        pass
    @abstractmethod
    def send_pkt(self,pkt):
        """Returns whether or not the packet was buffered to be sent"""
        pass

    @abstractmethod
    def can_buffer_pkts(self):
        pass

    @abstractmethod
    def receive_ack(self,pkt):
        """Receive a control packet (NAK or ACK)"""
        pass

    @abstractmethod
    def close_connection(self):
        """Cleanup method used to cancel timers..etc"""
        pass
    @abstractmethod
    def is_empty(self):
        """Returns true if the buffer doesn't contain any pending packets, or packets pending ACKs"""
        pass

class SelectiveRepeatPacketManager(SenderPacketManager):

    ACKED_TYPE = 'Acked' #Used to mark a field in the buffer as being an acked packet so that when we try to slide the
    #window we'd know which packets are pending acks, which are empty slots and which have been acked(None is empty slot)
    def __init__(self,window_size, max_sqn, send_callback, timeout = Defaults.TIMEOUT):
        """send_callback has to be thread safe"""
        # super().__init__(window_size, max_sqn, send_callback)
        self.window_size = window_size
        self.max_sqn = max_sqn
        self.send_callback = send_callback
        self.buffer = [None] * window_size
        self.base_seqn = 0
        self.timeout_length = timeout
        self.timers_dict = {}

    def send_pkt(self,pkt):
        """If the window is not full, we put the pkt in the window and call the
        send callback immediately without checking if a send request has already been made"""
        is_retry = len(list(filter(lambda x: type(x) is Packet and x.seqn == pkt.seqn,self.buffer)))
        if self.can_buffer_pkts() or is_retry:
            index = self.calc_index(pkt.seqn)
            if index < self.window_size:
                self.buffer[index] = pkt
                self.send_callback(pkt)
                self.start_timer_for_pkt(pkt)
                return True
            # else:
                # print('Base seqn:{}, where pkts index:{}'.format(self.base_seqn,pkt.seqn))
            # print('Them failed index:{} paket: {}  base:{} '.format(index,pkt.seqn,self.base_seqn))
        return False

    def can_buffer_pkts(self):
        can_buffer = len(list(filter(lambda x: x is None, self.buffer)))
        # print('Sender can buffer packets: {}, buffer:{}'.format(can_buffer,self.buffer))
        return can_buffer

    def receive_ack(self,pkt):
        index = self.calc_index(pkt.seqn)
        # print('Window manager receivin ack with seqn:{}, base:{} buffer:{}'.format(pkt.seqn,self.base_seqn,self.buffer))
        if index >= len(self.buffer) or index < 0:
            # print('Ignoring ACK with SEQN:{}'.format(pkt.seqn))
            return #Ignore the ack
        self.buffer[index] = SelectiveRepeatPacketManager.ACKED_TYPE
        # stop the timer
        if pkt.seqn in self.timers_dict and self.timers_dict[pkt.seqn]:
            self.timers_dict[pkt.seqn].cancel()
            del self.timers_dict[pkt.seqn]
            # print('Canceling timer for SEQN:{}'.format(pkt.seqn))
        #re-organize the buffer if there were a continuous stream of ack'd packets (continuous stream of Nones)
        i = 0
        for i in range(len(self.buffer)):
            if not self.buffer[i] == SelectiveRepeatPacketManager.ACKED_TYPE:
                break
        pkts = self.buffer[0:i]
        del self.buffer[0:i]
        self.buffer.extend([None] * i)
        self.base_seqn = (self.base_seqn + i) % self.max_sqn
        # print('Advancing base to:{}'.format(self.base_seqn))
        # print('Window manager receivin ack with AFTEEEER seqn:{}, base:{} buffer:{}'.format(pkt.seqn,self.base_seqn,self.buffer))

        return

    def start_timer_for_pkt(self,pkt):
        # print('Starting Timer')
        if pkt.seqn in self.timers_dict:
            self.timers_dict[pkt.seqn].cancel()
        # else:
        timer =  Timer(self.timeout_length,self.send_pkt, [pkt])
        timer.start()
        self.timers_dict[pkt.seqn] = timer#RetryPolicyWrapper(timer)

    def close_connection(self):
        for key in  self.timers_dict:
            self.timers_dict[key].cancel()

    def calc_index(self,seqn):
        return abs(seqn + self.max_sqn - self.base_seqn) % self.max_sqn

    def is_empty(self):
        return not len(list(filter(lambda x : type(x) is Packet or x == SelectiveRepeatPacketManager.ACKED_TYPE,self.buffer )))
class GoBackNWindowManager(SenderPacketManager):

    def __init__(self, window_size, max_sqn, send_callback, timeout = Defaults.TIMEOUT):
        self.window_size = window_size
        self.max_sqn = max_sqn
        self.send_callback = send_callback
        self.buffer = [None] * window_size
        self.base_seqn = 0
        self.timeout_length = timeout
        self.timers_dict = {}

    def send_pkt(self, pkt):
        """If the window is not full, we put the pkt in the window and call the
        send callback immediately without checking if a send request has already been made"""
        is_retry = len(list(filter(lambda x: type(x) is Packet and x.seqn == pkt.seqn,self.buffer)))
        if self.can_buffer_pkts() or is_retry:
            index = abs(self.base_seqn - pkt.seqn)
            if index < self.window_size:
                self.buffer[index] = pkt
                self.send_callback(pkt)
                self.start_timer_for_pkt(pkt)
                return True
        # else:
        # print('Base seqn:{}, where pkts index:{}'.format(self.base_seqn,pkt.seqn))

    def can_buffer_pkts(self):
        can_buffer = len(list(filter(lambda x: x is None, self.buffer)))
        # print('Sender can buffer packets: {}, buffer:{}'.format(can_buffer,self.buffer))
        return can_buffer

    def receive_ack(self,pkt):
        """In GoBackN we receive cumulative acks. So any packet in the buffer preceding the passed pkt
        will be delivered as well"""
        index = self.calc_index(pkt.seqn) + 1
        if index >= self.window_size or index < 0:
            return
        # stop the timer
        for i in range(index):
            acked_pkt = self.buffer[i]
            if acked_pkt.seqn in self.timers_dict and self.timers_dict[acked_pkt.seqn]:
                self.timers_dict[acked_pkt.seqn].cancel()
                del self.timers_dict[acked_pkt.seqn]
        pkts = self.buffer[0:index]
        del self.buffer[0:index]
        self.buffer.extend([None] * index)
        self.base_seqn += index
        self.base_seqn %= self.max_sqn

    def start_timer_for_pkt(self,pkt):
        # print('Starting Timer for pkt:{}'.format(pkt.seqn))
        # if pkt.seqn in self.timers_dict:
        #     policy = self.timers_dict[pkt.seqn]
        #     if policy.can_retry():
        #         policy.timer = Timer(self.timeout_length,self.send_pkt, [pkt])
        #         policy.timer.start()
        # else:
        timer =  Timer(self.timeout_length,self.send_pkt, [pkt])
        timer.start()
        self.timers_dict[pkt.seqn] = timer#RetryPolicyWrapper(timer)
    def is_empty(self):
        return not len(list(filter(lambda x: x is not None, self.buffer)))
    def close_connection(self):
        for key in  self.timers_dict:
            self.timers_dict[key].cancel()

    def calc_index(self,seqn):
        return abs(seqn + self.max_sqn - self.base_seqn) % self.max_sqn

class StopAndWaitWindowManager(GoBackNWindowManager):
    def __init__(self, max_sqn, send_callback, timeout=6):
        super().__init__(1,max_sqn,send_callback,timeout)


# class RetryPolicyWrapper:
# #Wrapper used to store the timer in the timers dict. (Awfully designed, but not a pythoniesta and too lazy)
#     def __init__(self,timer, max_tries=5):
#         self.timer = timer
#         self.max_tries = max_tries
#         self.tries = 0
#
#     def can_retry(self):
#         """Returns whether we can retry, r the the maximum number of retries has been reached.
#         Caling this method max_tries times would return false at the end"""
#         self.tries += 1
#         can_retry =  self.tries < self.max_tries
#         return can_retry
#
#
#     def cancel(self):
#         self.timer.cancel()
