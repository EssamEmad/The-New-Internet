from abc import ABC, abstractmethod
from threading import Timer
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

class SelectiveRepeatPacketManager(SenderPacketManager):

    def __init__(self,window_size, max_sqn, send_callback, timeout = 6):
        """send_callback has to be thread safe"""
        # super().__init__(window_size, max_sqn, send_callback)
        self.window_size = window_size
        self.max_sqn = max_sqn
        self.send_callback = send_callback
        self.buffer = [None] * window_size
        self.base_seqn = 0
        self.timeout_length = timeout
        self.timers_dict = {} #Maps from seqn to RetryPolicyWrapper object

    def send_pkt(self,pkt):
        """If the window is not full, we put the pkt in the window and call the
        send callback immediately without checking if a send request has already been made"""
        if self.can_buffer_pkts():
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
        print('Window manager receivin ack with seqn:{}, base:{} buffer:{}'.format(pkt.seqn,self.base_seqn,self.buffer))
        if index >= len(self.buffer) or index < 0:
            print('Ignoring ACK with SEQN:{}'.format(pkt.seqn))
            return #Ignore the ack
        self.buffer[index] = None
        # stop the timer
        if pkt.seqn in self.timers_dict and self.timers_dict[pkt.seqn]:
            self.timers_dict[pkt.seqn].cancel()
            del self.timers_dict[pkt.seqn]
            print('Canceling timer for SEQN:{}'.format(pkt.seqn))
        #re-organize the buffer if there were a continuous stream of ack'd packets (continuous stream of Nones)
        last_none_index = 0
        while self.buffer[last_none_index] == None and last_none_index != len(self.buffer) - 1:
            last_none_index += 1
            i = last_none_index
            pkts = self.buffer[0:i]
            del self.buffer[0:i]
            self.buffer.extend([None] * i)
            self.base_seqn += i
            self.base_seqn %= self.max_sqn
            print('Advancing base to:{}'.format(self.base_seqn))
            # print('Window manager receiving ack with seqn:{}'.format(pkt.seqn))
            return

    def start_timer_for_pkt(self,pkt):
        print('Starting Timer')
        if pkt.seqn in self.timers_dict:
            self.timers_dict[pkt.seqn].retry()
        else:
            timer =  Timer(self.timeout_length,self.send_pkt, [pkt])
            timer.start()
            self.timers_dict[pkt.seqn] = RetryPolicyWrapper(timer)

    def close_connection(self):
        for key in  self.timers_dict:
            self.timers_dict[key].cancel()

    def calc_index(self,seqn):
        return abs(seqn + self.max_sqn - self.base_seqn) % self.max_sqn
class GoBackNWindowManager(SenderPacketManager):

    def __init__(self, window_size, max_sqn, send_callback, timeout = 6):
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
        if self.can_buffer_pkts():
            index = abs(self.base_seqn - pkt.seqn)
            if index < self.window_size:
                self.buffer[index] = pkt
                self.send_callback(pkt)
                self.start_timer_for_pkt(pkt)
                return True
        # else:
        print('Base seqn:{}, where pkts index:{}'.format(self.base_seqn,pkt.seqn))

    def can_buffer_pkts(self):
        can_buffer = len(list(filter(lambda x: x is None, self.buffer)))
        print('Sender can buffer packets: {}, buffer:{}'.format(can_buffer,self.buffer))
        return can_buffer

    def receive_ack(self,pkt):
        """In GoBackN we receive cumulative acks. So any packet in the buffer preceding the passed pkt
        will be delivered as well"""
        index = self.calc_index(pkt.seqn)
        # stop the timer
        for i in range(index + 1):
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
        print('Starting Timer for pkt:{}'.format(pkt.seqn))
        if pkt.seqn in self.timers_dict:
            self.timers_dict[pkt.seqn].retry()
        else:
            timer =  Timer(self.timeout_length,self.send_pkt, [pkt])
            timer.start()
            self.timers_dict[pkt.seqn] = RetryPolicyWrapper(timer)

    def close_connection(self):
        for key in  self.timers_dict:
            self.timers_dict[key].cancel()

    def calc_index(self,seqn):
        return abs(seqn + self.max_sqn - self.base_seqn) % self.max_sqn

class StopAndWaitWindowManager(GoBackNWindowManager):
    def __init__(self, max_sqn, send_callback, timeout=6):
        super().__init__(1,max_sqn,send_callback,timeout)


class RetryPolicyWrapper:
#Wrapper used to store the timer in the timers dict.
    def __init__(self,timer, max_tries=5):
        self.timer = timer
        self.max_tries = max_tries
        self.tries = 0

    def retry(self):
        """Returns whether we can retry, r the the maximum number of retries has been reached.
        Caling this method max_tries times would return false at the end"""
        self.tries += 1
        return self.tries < self.max_tries


    def cancel(self):
        self.timer.cancel()
